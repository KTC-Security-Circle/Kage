"""Terms management view implementation (新デザイン).

【責務】
    レイアウト構築とイベント配線を担当。
    Controller/Presenterを活用し、UIの構築に集中する。

    - BaseViewを継承し、with_loading/notify_error等を利用
    - コンポーネントの組み合わせとレイアウト構成（2カラム: 左リスト、右詳細）
    - イベントハンドラでControllerへ委譲
    - State変更後の差分更新

【責務外（他層の担当）】
    - 状態管理 → State
    - ビジネスロジック → Controller
    - UI整形 → Presenter
    - 純粋関数 → utils
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import UUID

import flet as ft
from loguru import logger

from models import TermStatus
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import HeaderButtonData

from .components.status_tabs import StatusTabsProps, TermStatusTabs
from .components.term_detail import DetailPanelProps, TermDetailPanel
from .components.term_list import TermList, TermListProps
from .controller import TermFormData, TerminologyApplicationPortAdapter, TermsController
from .presenter import create_term_card_data, create_term_detail_data, get_empty_message
from .state import TermsViewState

if TYPE_CHECKING:
    from .components.create_term_dialog import CreateTermDialog
    from .components.term_card import TermCardData
    from .components.term_detail import TermDetailData


class TermsView(BaseView):
    """社内用語管理のメインビュー（最新デザイン対応）。"""

    def __init__(self, props: BaseViewProps) -> None:
        """Initialize terms view.

        Args:
            props: View共通プロパティ
        """
        super().__init__(props)
        self.title = "社内用語管理"
        self.description = "社内固有の用語・略語・定義を管理"

        # State & Controller
        self.term_state = TermsViewState()
        service = self.apps.terminology
        self.controller = TermsController(
            state=self.term_state,
            service=TerminologyApplicationPortAdapter(service),
        )

        # Components
        self.status_tabs: TermStatusTabs | None = None
        self.term_list: TermList | None = None
        self.detail_panel: TermDetailPanel | None = None

        # Dialogs
        self.create_dialog: CreateTermDialog | None = None

    def build(self) -> ft.Control:
        """Build the main content area."""
        # 初期ロード（非同期）をスケジュール
        if self.page:
            self.page.run_task(self._initial_load)
        return self.build_content()

    async def _initial_load(self) -> None:
        """初期データのロード（非同期）。"""
        try:
            await self.controller.load_initial_terms()
            self._refresh_term_list()
            self._refresh_status_tabs()
            if not self.term_state.all_terms:
                self.show_info_snackbar("まだ用語が登録されていません。新しい用語を作成してください。")
        except Exception:
            logger.exception("Failed to load initial terms")
            if self.page:
                self.show_error_snackbar(self.page, "初期データの読み込みに失敗しました")

    def build_content(self) -> ft.Control:
        """Build the main content area."""
        # Headerコンポーネント (検索と新規作成ボタン)
        total_count = len(self.term_state.all_terms)
        header = self.create_header(
            title=self.title,
            subtitle=f"{self.description} ({total_count}件)",
            search_placeholder="用語、キー、同義語で検索...",
            on_search=self._handle_search_query,
            action_buttons=[
                HeaderButtonData(
                    label="新しい用語",
                    icon=ft.Icons.ADD,
                    on_click=self._handle_create_term,
                    is_primary=True,
                )
            ],
        )

        # ステータスタブ
        counts = self.controller.get_counts()
        status_tabs_props = StatusTabsProps(
            approved_count=counts[TermStatus.APPROVED],
            draft_count=counts[TermStatus.DRAFT],
            deprecated_count=counts[TermStatus.DEPRECATED],
            on_status_change=self._handle_status_change,
        )
        self.status_tabs = TermStatusTabs(status_tabs_props)

        # 用語リスト
        term_list_props = TermListProps(
            on_item_click=self._handle_term_select_str,
            empty_message=get_empty_message(self.term_state.current_tab),
        )
        self.term_list = TermList(term_list_props)

        # 詳細パネル
        detail_panel_props = DetailPanelProps(
            on_edit=self._handle_edit_term,
            on_tag_click=self._handle_tag_click,
            on_item_click=self._handle_related_item_click,
        )
        self.detail_panel = TermDetailPanel(detail_panel_props)

        # 初期データ描画
        self._refresh_term_list()

        # 2カラムレイアウト（左: リスト、右: 詳細）
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.status_tabs,
                            self.term_list.control,
                        ],
                        spacing=16,
                        expand=True,
                    ),
                    col={"xs": 12, "lg": 5},
                    padding=ft.padding.only(right=12),
                ),
                ft.Container(
                    content=self.detail_panel.control,
                    col={"xs": 12, "lg": 7},
                ),
            ],
            expand=True,
        )

        # メインコンテンツ
        return ft.Column(
            controls=[
                header,
                ft.Divider(),
                grid,
            ],
            spacing=16,
            expand=True,
        )

    def _handle_search_query(self, query: str) -> None:
        """Header検索フィールドからの検索処理。

        Args:
            query: 検索クエリ
        """
        if self.page:
            self.page.run_task(self._async_search, query)

    def _handle_search(self, e: ft.ControlEvent) -> None:
        """検索クエリの変更をハンドリングする。

        Args:
            e: コントロールイベント
        """
        query = getattr(e.control, "value", "") or ""
        if self.page:
            self.page.run_task(self._async_search, query)

    async def _async_search(self, query: str) -> None:
        """非同期検索を実行する。

        Args:
            query: 検索クエリ
        """
        try:
            await self.controller.update_search(query)
            self._refresh_term_list()
        except Exception:
            logger.exception("Failed to perform search")
            if self.page:
                self.show_error_snackbar(self.page, "検索に失敗しました")

    def _handle_status_change(self, status: TermStatus) -> None:
        """ステータスタブの変更をハンドリングする。

        Args:
            status: 選択されたステータス
        """
        self.controller.update_tab(status)
        self._refresh_term_list()
        self._refresh_status_tabs()
        self._set_active_status_tab(status)

    def _handle_term_select_uuid(self, term_id: UUID) -> None:
        """用語選択をハンドリングする（UUID）。

        Args:
            term_id: 選択された用語のID
        """
        self.controller.select_term(term_id)
        self._refresh_term_list()
        self._show_detail()

    def _handle_term_select_str(self, term_id: str) -> None:
        """用語選択をハンドリングする（文字列）。

        Args:
            term_id: 選択された用語のID
        """
        try:
            self._handle_term_select_uuid(UUID(term_id))
        except ValueError:
            logger.warning("Invalid UUID format", extra={"term_id": term_id})
            if self.page:
                self.show_error_snackbar(self.page, "無効なIDです")

    def _handle_create_term(self) -> None:
        """用語作成ボタンのクリックをハンドリングする。"""
        self._show_create_dialog()

    def _handle_edit_term(self, term_id: str) -> None:
        """用語編集ボタンのクリックをハンドリングする。

        Args:
            term_id: 編集する用語のID
        """
        self.show_snack_bar(f"用語編集機能は準備中です (ID: {term_id})")

    def _handle_tag_click(self, tag_name: str) -> None:
        """タグクリックをハンドリングする。

        Args:
            tag_name: クリックされたタグ名
        """
        self.show_snack_bar(f"タグ '{tag_name}' の機能は準備中です")

    def _handle_related_item_click(self, item_type: str, item_id: str) -> None:
        """関連アイテムクリックをハンドリングする。

        Args:
            item_type: アイテムタイプ（"memo" or "task"）
            item_id: アイテムID
        """
        self.show_snack_bar(f"{item_type} アイテム遷移機能は準備中です (ID: {item_id})")

    def _refresh_term_list(self) -> None:
        """用語リストを更新する。"""
        if not self.term_list:
            return

        self.term_list.update_props(
            TermListProps(
                on_item_click=self._handle_term_select_str,
                empty_message=get_empty_message(self.term_state.current_tab),
            )
        )
        derived_terms = self.term_state.visible_terms
        selected_id = self.term_state.selected_term_id

        cards: list[TermCardData] = []
        for term in derived_terms:
            # [AI GENERATED] デフォルト引数で term_id をキャプチャ
            # ループ変数の遅延評価（late binding）を回避
            def _on_click(term_id: UUID = term.id) -> None:
                self._handle_term_select_uuid(term_id)

            card_data = create_term_card_data(
                term,
                is_selected=(term.id == selected_id) if selected_id else False,
                on_click=_on_click,
            )
            cards.append(card_data)

        self.term_list.set_cards(cards)

    def _show_detail(self) -> None:
        """選択された用語の詳細を表示する。"""
        if not self.detail_panel:
            return

        selected_term = self.term_state.selected_term
        if not selected_term:
            self.detail_panel.set_item(None)
            return

        # TODO: 関連アイテムの取得ロジック実装
        detail_data: TermDetailData = create_term_detail_data(
            selected_term,
            related_items=[],
        )
        self.detail_panel.set_item(detail_data)

    def _refresh_status_tabs(self) -> None:
        """ステータスタブを更新する。"""
        if not self.status_tabs:
            return

        counts = self.controller.get_counts()
        status_tabs_props = StatusTabsProps(
            approved_count=counts[TermStatus.APPROVED],
            draft_count=counts[TermStatus.DRAFT],
            deprecated_count=counts[TermStatus.DEPRECATED],
            on_status_change=self._handle_status_change,
        )
        self.status_tabs.set_props(status_tabs_props)

    def _show_create_dialog(self) -> None:
        """用語作成ダイアログを表示する。"""
        from .components.create_term_dialog import CreateTermDialog, CreateTermDialogProps

        dialog_props = CreateTermDialogProps(
            on_create=self._handle_dialog_create,
            on_cancel=self._handle_dialog_cancel,
        )
        self.create_dialog = CreateTermDialog(dialog_props)

        if self.page:
            self.page.overlay.append(self.create_dialog.dialog)
            self.create_dialog.dialog.open = True
            self.page.update()

    def _handle_dialog_create(self, form_data: dict[str, object]) -> None:
        """ダイアログからの用語作成をハンドリングする。

        Args:
            form_data: フォームデータ（key, title, description, status, source_url, synonyms）
        """
        if self.page:
            self.page.run_task(self._async_create_term, form_data)

    async def _async_create_term(self, form_data: dict[str, object]) -> None:
        """非同期で用語を作成する。

        Args:
            form_data: フォームデータ
        """
        try:
            # 用語作成
            created_term = await self.controller.create_term(cast("TermFormData", form_data))
            self._close_create_dialog()
            self.show_snack_bar(f"用語 '{created_term.key}' を作成しました")
            normalized_status = self._normalize_status(created_term.status)
            self.controller.update_tab(normalized_status)
            self.controller.select_term(created_term.id)
            self._refresh_term_list()
            self._refresh_status_tabs()
            self._set_active_status_tab(normalized_status)
            self._show_detail()

        except ValueError as e:
            # バリデーションエラー
            logger.warning("Validation error during term creation", extra={"error": str(e)})
            if self.page:
                self.show_error_snackbar(self.page, f"バリデーションエラー: {e}")

        except Exception:
            # その他のエラー
            logger.exception("Failed to create term")
            self._close_create_dialog()
            if self.page:
                self.show_error_snackbar(self.page, "用語の作成に失敗しました")

    def _handle_dialog_cancel(self) -> None:
        """ダイアログのキャンセルをハンドリングする。"""
        self._close_create_dialog()

    def _close_create_dialog(self) -> None:
        """用語作成ダイアログを閉じる。"""
        if self.create_dialog and self.page:
            # 1. ダイアログを閉じる
            self.create_dialog.dialog.open = False
            self.page.update()  # 先にダイアログを閉じる表示を反映

            # 2. オーバーレイから削除
            # if self.create_dialog.dialog in self.page.overlay:
            #     self.page.overlay.remove(self.create_dialog.dialog)
            #     self.page.update()  # オーバーレイからの削除を反映

            # # 3. 参照をクリア
            # self.create_dialog = None

    def _set_active_status_tab(self, status: TermStatus) -> None:
        """ステータスタブの選択状態を指定したステータスに同期する。"""
        if self.status_tabs:
            self.status_tabs.set_active_status(status)

    def _normalize_status(self, status: TermStatus | str | None) -> TermStatus:
        """TermStatusまたは文字列をTermStatusに正規化する。"""
        if isinstance(status, TermStatus):
            return status
        if isinstance(status, str):
            try:
                return TermStatus(status)
            except ValueError:
                logger.warning("Unknown term status value: %s", status)
        return TermStatus.APPROVED
