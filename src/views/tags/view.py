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

from loguru import logger

if TYPE_CHECKING:
    import flet as ft

from logic.application.memo_application_service import MemoApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import HeaderButtonData

from .components import (
    EmptyTagsState,
    EmptyTagsStateProps,
    TagDetailPanel,
    TagFormData,
    TagListItem,
    show_tag_create_dialog,
    show_tag_edit_dialog,
)
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
        tag_service = self.apps.get_service(TagApplicationService)
        memo_service = self.apps.get_service(MemoApplicationService)
        task_service = self.apps.get_service(TaskApplicationService)
        self.controller = TagsController(self.tags_state, tag_service, memo_service, task_service)
        self.presenter = TagsPresenter()

        # UIルート要素
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
            try:
                self.controller.load_initial_tags()
            except Exception as exc:  # pragma: no cover - UI フォールバック
                if self.page:
                    self.show_error_snackbar(self.page, f"タグの読み込みに失敗しました: {exc}")

        # Headerコンポーネント (検索と新規作成ボタン)
        total_count = len(self.tags_state.items)
        filtered_count = self.tags_state.filtered_count
        subtitle = f"メモやタスクを整理 ({filtered_count}/{total_count}件)"

        self._header = self.create_header(
            title="タグ",
            subtitle=subtitle,
            search_placeholder="タグを検索...",
            on_search=self._handle_search,
            action_buttons=[
                HeaderButtonData(
                    label="新規タグ",
                    icon=ft.Icons.ADD,
                    on_click=self._handle_create,
                    is_primary=True,
                )
            ],
        )

        # アクションバーは削除（Headerに統合）

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
        grid = self.create_two_column_layout(
            left_content=self._list_column,
            right_content=self._detail_panel,
        )

        return self.create_standard_layout(
            header=self._header,
            content=grid,
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

    def _tags_by_id(self) -> dict[str, dict[str, str]]:
        """[AI GENERATED] タグIDをキーとしたタグ辞書を返す

        Returns:
            dict[str, dict[str, str]]: タグIDをキーとしたタグ辞書
        """
        return {tag["id"]: tag for tag in self.tags_state.items}

    def _get_selected_tag(self) -> dict[str, str] | None:
        """選択中のタグを取得する

        Returns:
            dict[str, str] | None: 選択中のタグ、未選択の場合はNone
        """
        selected_id = self.tags_state.selected_id
        if not selected_id:
            return None
        return self._tags_by_id().get(selected_id)

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _handle_create(self) -> None:
        """Header作成ボタンのクリック処理。"""
        self._on_create()

    def _refresh_ui(self) -> None:
        """State変更後にUIを更新する（差分更新）"""
        # ヘッダー件数更新はHeader再構築が必要なため、現状はスキップ
        # TODO: Headerコンポーネントにset_propsメソッドを追加して動的更新を可能にする

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

    def _on_create(self, _e: ft.ControlEvent | None = None) -> None:  # type: ignore[name-defined]
        """新規作成ハンドラ"""
        if not self.page:
            return

        def on_submit(form_data: TagFormData) -> None:
            """タグ作成時のコールバック"""
            try:
                self.controller.create_tag(form_data.name, form_data.color, form_data.description)
            except Exception as exc:  # pragma: no cover - UI フォールバック
                self.show_error_snackbar(self.page, f"タグの作成に失敗しました: {exc}")
                return
            self._refresh_ui()
            self.show_success_snackbar(f"タグ「{form_data.name}」を作成しました")

        show_tag_create_dialog(self.page, on_submit)

    def _handle_search(self, query: str) -> None:
        """検索ハンドラ

        Args:
            query: 検索クエリ
        """
        self.controller.update_search(SearchQuery(raw=query))
        self._refresh_ui()

    def _on_refresh(self, _e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """更新ハンドラ"""
        try:
            self.controller.refresh()
        except Exception as exc:  # pragma: no cover - UI フォールバック
            if self.page:
                self.show_error_snackbar(self.page, f"タグデータの更新に失敗しました: {exc}")
            return
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
            try:
                self.controller.update_tag(
                    selected_tag["id"],
                    name=form_data.name,
                    color=form_data.color,
                    description=form_data.description,
                )
            except Exception as exc:  # pragma: no cover - UI フォールバック
                self.show_error_snackbar(self.page, f"タグの更新に失敗しました: {exc}")
                return
            self._refresh_ui()
            self.show_success_snackbar(f"タグ「{form_data.name}」を更新しました")

        show_tag_edit_dialog(self.page, selected_tag, on_submit)

    def _navigate_with_pending_id(self, storage_key: str, item_id: str, route: str, item_type: str) -> None:
        """client_storageにIDを保存してページ遷移する共通処理

        Args:
            storage_key: client_storageのキー名（例: "pending_memo_id"）
            item_id: 保存するID
            route: 遷移先のルート（例: "/memos"）
            item_type: アイテムの種類（ログ/エラーメッセージ用、例: "メモ"）
        """
        if not self.page:
            return

        logger.info(f"{item_type}画面への遷移を開始: {item_id}")
        try:
            self.page.client_storage.set(storage_key, item_id)
            self.page.go(route)
            logger.debug(f"{item_type}画面への遷移が完了: {route} ({storage_key}={item_id})")
        except Exception as e:
            logger.error(f"{item_type}画面への遷移に失敗: {e}", exc_info=True)
            self.show_error_snackbar(self.page, f"{item_type}画面への遷移に失敗しました")

    def _on_memo_click(self, _e: ft.ControlEvent, memo_id: str) -> None:  # type: ignore[name-defined]
        """関連メモクリックハンドラ

        メモIDをclient_storageに一時保存し、メモ画面に遷移する。
        遷移先でpending_memo_idを読み取り、該当メモを選択表示する。

        Args:
            _e: イベント（未使用）
            memo_id: 選択されたメモのID
        """
        self._navigate_with_pending_id("pending_memo_id", memo_id, "/memos", "メモ")

    def _on_task_click(self, _e: ft.ControlEvent, task_id: str) -> None:  # type: ignore[name-defined]
        """関連タスククリックハンドラ

        タスクIDをclient_storageに一時保存し、タスク画面に遷移する。
        遷移先でpending_task_idを読み取り、該当タスクを選択表示する。

        Args:
            _e: イベント（未使用）
            task_id: 選択されたタスクのID
        """
        self._navigate_with_pending_id("pending_task_id", task_id, "/tasks", "タスク")
