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
    TagListItem,
    TagsActionBar,
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
        """State変更後にUIを更新する"""
        import flet as ft

        # ヘッダー件数更新
        if self._header and hasattr(self._header, "parent"):
            parent_col = self._header.parent  # type: ignore[attr-defined]
            if parent_col and isinstance(parent_col, ft.Column):
                idx = parent_col.controls.index(self._header)  # type: ignore[arg-type]
                parent_col.controls[idx] = create_page_header(self.tags_state.filtered_count)  # type: ignore[index]
                self._header = parent_col.controls[idx]

        # リスト再構築
        if self._list_column:
            self._list_column.controls = self._build_list_controls()

        # 詳細パネル更新
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
        # TODO: タグ作成ダイアログを表示
        # 理由: ユーザー入力（name, color, description）を受け取る
        # 実装: dialog = TagCreateDialog(on_submit=self._handle_create_submit)
        # 置換先: src/views/tags/components/tag_create_dialog.py を新規作成
        # 注意: カラーパレットダイアログの統合も必要
        self.controller.create_tag_stub()
        self._refresh_ui()
        self.show_info_snackbar("新規タグ作成は後続実装予定")

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
        # TODO: タグ編集ダイアログを表示
        # 理由: 選択中タグの情報を編集可能にする
        # 実装: dialog = TagEditDialog(tag=selected_tag, on_submit=self._handle_edit_submit)
        # 置換先: src/views/tags/components/tag_edit_dialog.py を新規作成
        # 注意: カラーパレットダイアログの統合、バリデーション、更新後のリフレッシュ
        selected_tag = self._get_selected_tag()
        if selected_tag:
            self.show_info_snackbar(f"タグ『{selected_tag['name']}』編集は準備中")

    def _on_memo_click(self, _e: ft.ControlEvent, memo_id: str) -> None:  # type: ignore[name-defined]
        """関連メモクリックハンドラ"""
        # TODO: メモ詳細画面へ遷移
        # 理由: 選択されたメモの詳細を表示する
        # 実装: self.page.go(f"/memos/{memo_id}")
        # 置換先: src/router.py のルーティング設定を確認
        # 注意: MemosViewでの選択状態復元が必要かもしれない
        self.show_info_snackbar(f"メモ {memo_id} への遷移は後続実装予定")

    def _on_task_click(self, _e: ft.ControlEvent, task_id: str) -> None:  # type: ignore[name-defined]
        """関連タスククリックハンドラ"""
        # TODO: タスク詳細画面へ遷移
        # 理由: 選択されたタスクの詳細を表示する
        # 実装: self.page.go(f"/tasks/{task_id}")
        # 置換先: src/router.py のルーティング設定を確認
        # 注意: TasksViewでの選択状態復元が必要かもしれない
        self.show_info_snackbar(f"タスク {task_id} への遷移は後続実装予定")
