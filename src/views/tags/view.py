"""タグ管理ビュー (Layered Architecture 版)

`src/views_old/template/src/components/TagsScreen.tsx` を参考にした
モダンな2カラムレイアウトでタグ管理機能を提供。

レイアウト構成:
    - 左カラム (1/3): タグリスト（選択可能なリストアイテム）
    - 右カラム (2/3): 選択されたタグの詳細パネル（関連メモ・タスク表示）

レイヤー構成:
    - View: レイアウト構築とイベント配線のみ
    - Controller: ユースケース的操作（ロード/検索/選択/関連アイテム取得）
    - State: 表示状態の単一ソース
    - Presenter: StateからUI用Propsへ整形
    - Components: Props駆動の純粋UI

今後の拡張ポイント:
    - ApplicationServices 経由の永続化（現状はMock）
    - タグ編集ダイアログの統合
    - カラーパレットダイアログの統合
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from views.shared.base_view import BaseView, BaseViewProps

from .components import (
    EmptyTagsState,
    EmptyTagsStateProps,
    TagDetailPanel,
    TagFormData,
    TagListItem,
    TagsActionBar,
    show_tag_create_dialog,
    show_tag_edit_dialog,
)
from .components.page_header import create_page_header
from .controller import TagsController
from .presenter import TagsPresenter
from .query import SearchQuery
from .state import TagsViewState


class TagsView(BaseView):
    """タグ管理機能のトップレベルView。

    Notes:
        - `src/views_old/template` の TagsScreen.tsx を参考に2カラムレイアウトを実装。
        - 左カラム: タグリスト（選択可能）
        - 右カラム: 選択されたタグの詳細パネル
        - データ取得はControllerに委譲し、ViewはUI組立に集中する。
    """

    def __init__(self, props: BaseViewProps) -> None:  # type: ignore[name-defined]
        super().__init__(props)
        self.tags_state = TagsViewState()
        self.controller = TagsController(self.tags_state)
        self.presenter = TagsPresenter()

        # UIルート要素
        self._action_bar: TagsActionBar | None = None
        self._list_column: ft.Column | None = None  # type: ignore[name-defined]
        self._detail_panel: TagDetailPanel | None = None
        self._header: ft.Control | None = None  # type: ignore[name-defined]

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        import flet as ft

        # 初期ロード（一度のみ）
        if not self.tags_state.initial_loaded:
            self.controller.load_initial_tags()

        # ヘッダー
        self._header = create_page_header(self.tags_state.filtered_count)

        # アクションバー
        action_bar_props = self.presenter.build_action_bar_props(
            self.tags_state,
            on_create=self._on_create,
            on_search=self._on_search,
            on_refresh=self._on_refresh,
        )
        self._action_bar = TagsActionBar(action_bar_props)

        # タグリスト（左カラム）
        list_controls = self._build_list_controls()
        self._list_column = ft.Column(
            controls=list_controls,
            spacing=8,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # 詳細パネル（右カラム）
        selected_tag = self._get_selected_tag()
        detail_props = self.presenter.build_tag_detail_panel_props(
            selected_tag,
            self.controller,
            on_edit=self._on_edit_selected,
            on_memo_click=self._on_memo_click,
            on_task_click=self._on_task_click,
        )
        self._detail_panel = TagDetailPanel(detail_props)

        # 2カラムレイアウト
        return ft.Container(
            content=ft.Column(
                controls=[
                    self._header,
                    self._action_bar,
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self._list_column,
                                expand=1,
                                padding=ft.padding.only(right=8),
                            ),
                            ft.Container(
                                content=self._detail_panel,
                                expand=2,
                                padding=ft.padding.only(left=8),
                            ),
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    # ------------------------------------------------------------------
    # UI Building Helpers
    # ------------------------------------------------------------------
    def _build_list_controls(self) -> list[ft.Control]:  # type: ignore[name-defined]
        """タグリストアイテムを構築する"""
        if not self.tags_state.filtered_tags:
            empty_props = EmptyTagsStateProps(on_create=self._on_create)
            return [EmptyTagsState(empty_props)]

        controls: list[ft.Control] = []  # type: ignore[name-defined]
        for tag in self.tags_state.filtered_tags:
            item_props = self.presenter.build_tag_list_item_props(
                tag,
                self.controller,
                selected=tag["id"] == self.tags_state.selected_id,
                on_click=self._on_tag_click,
            )
            controls.append(TagListItem(item_props))
        return controls

    def _get_selected_tag(self) -> dict[str, str] | None:
        """選択中のタグを取得する"""
        if not self.tags_state.selected_id:
            return None
        for tag in self.tags_state.items:
            if tag["id"] == self.tags_state.selected_id:
                return tag
        return None

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _refresh_ui(self) -> None:
        """State変更後にUIを更新する（差分更新）"""
        import flet as ft

        # ヘッダー件数更新（set_props的な更新が望ましいが、ヘッダーは単純なのでTextを直接更新）
        if self._header and hasattr(self._header, "parent"):
            parent_col = self._header.parent  # type: ignore[attr-defined]
            if parent_col and isinstance(parent_col, ft.Column):
                idx = parent_col.controls.index(self._header)  # type: ignore[arg-type]
                parent_col.controls[idx] = create_page_header(self.tags_state.filtered_count)  # type: ignore[index]
                self._header = parent_col.controls[idx]

        # リスト差分更新（全再構築より、個別アイテムのset_propsを呼ぶべきだが、
        # フィルタ変更時は件数が変わるため、シンプルに全再構築）
        # TODO: 仮想化（ListView等）を導入してパフォーマンス向上
        if self._list_column:
            new_controls = self._build_list_controls()
            # 既存コントロールと新規コントロールのIDを比較して差分更新を実装
            # ここでは簡易的に全置換（将来の改善ポイント）
            self._list_column.controls = new_controls
            self._list_column.update()

        # 詳細パネル更新（Props経由で差分更新）
        if self._detail_panel:
            selected_tag = self._get_selected_tag()
            detail_props = self.presenter.build_tag_detail_panel_props(
                selected_tag,
                self.controller,
                on_edit=self._on_edit_selected,
                on_memo_click=self._on_memo_click,
                on_task_click=self._on_task_click,
            )
            self._detail_panel.set_props(detail_props)

        self.safe_update()

    def _on_create(self, _e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規作成ハンドラ"""
        if not self.page:
            return

        def on_submit(form_data: TagFormData) -> None:
            """タグ作成時のコールバック"""
            # [AI GENERATED] 注意: form_dataは現在スタブ実装のため使用されていない
            # TODO: self.controller.create_tag(form_data.name, form_data.color, form_data.description)
            self.controller.create_tag_stub()
            self._refresh_ui()
            self.show_success_snackbar(f"タグ「{form_data.name}」を作成しました")

        show_tag_create_dialog(self.page, on_submit)

    def _on_search(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索ハンドラ"""
        value = getattr(e.control, "value", "")  # type: ignore[attr-defined]
        self.controller.update_search(SearchQuery(raw=value))
        self._refresh_ui()

    def _on_refresh(self, _e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """更新ハンドラ"""
        self.controller.refresh()
        self._refresh_ui()
        self.show_success_snackbar("タグデータを更新しました")

    def _on_tag_click(self, _e: ft.ControlEvent, tag_id: str) -> None:  # type: ignore[name-defined]
        """タグリストアイテムクリックハンドラ"""
        self.controller.select_tag(tag_id)
        self._refresh_ui()

    def _on_edit_selected(self, _e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """選択タグの編集ハンドラ"""
        if not self.page:
            return

        selected_tag = self._get_selected_tag()
        if not selected_tag:
            self.show_info_snackbar("編集するタグを選択してください")
            return

        def on_submit(form_data: TagFormData) -> None:
            """タグ編集時のコールバック"""
            # TODO: Controllerにタグ編集を委譲（現状はスタブ）
            # 理由: ApplicationServiceとの統合が未完了
            # 実装:
            # self.controller.update_tag(
            #     selected_tag["id"], form_data.name, form_data.color, form_data.description
            # )
            # 置換先: controller.py の update_tag メソッドを実装
            self._refresh_ui()
            self.show_success_snackbar(f"タグ「{form_data.name}」を更新しました")

        show_tag_edit_dialog(self.page, selected_tag, on_submit)

    def _on_memo_click(self, _e: ft.ControlEvent, memo_id: str) -> None:  # type: ignore[name-defined]
        """関連メモクリックハンドラ"""
        # TODO: メモ詳細画面の実装待ち
        # 理由: メモ詳細画面（/memos/:id）がまだ存在しない
        # 実装: MemosViewで詳細表示機能を実装後、ここで遷移を有効化
        # 置換先: src/views/memos/ 内に詳細表示機能を追加
        # 暫定: メモ一覧画面へ遷移してユーザーに選択させる
        if self.page:
            self.page.go("/memos")
            self.show_info_snackbar(f"メモ {memo_id} を一覧から選択してください")

    def _on_task_click(self, _e: ft.ControlEvent, task_id: str) -> None:  # type: ignore[name-defined]
        """関連タスククリックハンドラ"""
        # タスク管理画面へ遷移
        # 注意: TasksViewで特定タスクの選択・フォーカス機能があれば連携できる
        if self.page:
            self.page.go("/tasks")
            self.show_info_snackbar(f"タスク {task_id} を一覧から確認してください")
