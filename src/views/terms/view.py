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

from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

import flet as ft
from loguru import logger

from models import TermRead, TermStatus
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
        tag_service = self.apps.tag
        self.controller = TermsController(
            state=self.term_state,
            service=TerminologyApplicationPortAdapter(service),
            _tag_service=tag_service,
        )

        # Components
        self.status_tabs: TermStatusTabs | None = None
        self.term_list: TermList | None = None
        self.detail_panel: TermDetailPanel | None = None

        # Dialogs
        self.create_dialog: CreateTermDialog | None = None
        self.edit_dialog: Any | None = None

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
            on_search=self._handle_search,
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
        grid = self.create_two_column_layout(
            left_content=self.term_list.control,
            right_content=self.detail_panel.control,
        )

        # メインコンテンツ
        return self.create_standard_layout(
            header=header,
            status_tabs=self.status_tabs,
            content=grid,
        )

    def _handle_search(self, query: str) -> None:
        """検索ハンドラ。

        Args:
            query: 検索クエリ
        """
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

    def _handle_status_change(self, status: TermStatus | None) -> None:
        """ステータスタブの変更をハンドリングする。

        Args:
            status: 選択されたステータス（Noneの場合は無視）
        """
        if status is None:
            return
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
            term_id: 編集する用語ID
        """
        try:
            term_uuid = UUID(term_id)
            # 用語データを取得
            term = next((t for t in self.term_state.all_terms if t.id == term_uuid), None)
            if term:
                self._show_edit_dialog(term)
            else:
                self.show_snack_bar("用語が見つかりませんでした")
        except ValueError:
            logger.warning("Invalid UUID format", extra={"term_id": term_id})
            if self.page:
                self.show_error_snackbar(self.page, "無効なIDです")

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

        # タグマップを取得
        from views.shared.components import TagBadgeData
        from views.theme import get_grey_color

        all_tags = self.controller.get_all_tags()
        tag_map = {str(tag.id): tag for tag in all_tags}

        cards: list[TermCardData] = []
        for term in derived_terms:
            # [AI GENERATED] デフォルト引数で term_id をキャプチャ
            # ループ変数の遅延評価（late binding）を回避
            def _on_click(term_id: UUID = term.id) -> None:
                self._handle_term_select_uuid(term_id)

            # タグバッジを作成
            tag_badges = tuple(
                TagBadgeData(
                    name=tag.name,
                    color=get_grey_color(),
                )
                for tag_id in (getattr(term, "tags", None) or [])
                if (tag := tag_map.get(str(tag_id.id) if hasattr(tag_id, "id") else str(tag_id)))
            )

            card_data = create_term_card_data(
                term,
                is_selected=(term.id == selected_id) if selected_id else False,
                on_click=_on_click,
                tag_badges=tag_badges,
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

        # 全タグを取得
        all_tags = self.controller.get_all_tags()

        dialog_props = CreateTermDialogProps(
            on_create=self._handle_dialog_create,
            on_cancel=self._handle_dialog_cancel,
            all_tags=all_tags,
        )
        self.create_dialog = CreateTermDialog(dialog_props)

        if self.page:
            self.page.overlay.append(self.create_dialog.dialog)
            self.create_dialog.dialog.open = True
            self.page.update()

    def _show_edit_dialog(self, term: TermRead) -> None:
        """用語編集ダイアログを表示する。

        Args:
            term: 編集する用語データ
        """
        from .components.edit_term_dialog import EditTermDialog, EditTermDialogProps

        # 全タグを取得
        all_tags = self.controller.get_all_tags()

        # 用語データを辞書形式に変換
        term_data = {
            "id": str(term.id),
            "key": term.key,
            "title": term.title,
            "description": term.description,
            "status": term.status,
            "source_url": term.source_url,
            "tags": [{"name": tag.name, "id": str(tag.id)} for tag in getattr(term, "tags", [])],
            "synonyms": [syn.text for syn in getattr(term, "synonyms", [])],
        }

        dialog_props = EditTermDialogProps(
            term_data=term_data,
            on_update=lambda data: self._handle_dialog_update(term.id, data),
            on_cancel=self._handle_edit_dialog_cancel,
            all_tags=all_tags,
        )
        self.edit_dialog = EditTermDialog(dialog_props)

        if self.page:
            self.page.overlay.append(self.edit_dialog.dialog)
            self.edit_dialog.dialog.open = True
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

            # タグが指定されていれば同期
            tag_ids = form_data.get("tag_ids", [])
            if tag_ids and isinstance(tag_ids, list):
                from uuid import UUID

                tag_uuids = [UUID(tag_id) for tag_id in tag_ids]
                await self.controller.sync_tags(created_term.id, tag_uuids)

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

    def _handle_dialog_update(self, term_id: UUID, form_data: dict[str, object]) -> None:
        """ダイアログからの用語更新をハンドリングする。

        Args:
            term_id: 用語ID
            form_data: フォームデータ（key, title, description, status, source_url, synonyms, tag_ids）
        """
        if self.page:
            self.page.run_task(self._async_update_term, term_id, form_data)

    async def _async_update_term(self, term_id: UUID, form_data: dict[str, object]) -> None:
        """非同期で用語を更新する。

        Args:
            term_id: 用語ID
            form_data: フォームデータ
        """
        try:
            # 用語更新
            updated_term = await self.controller.update_term(term_id, cast("TermFormData", form_data))

            # タグが指定されていれば同期
            tag_ids = form_data.get("tag_ids", [])
            if isinstance(tag_ids, list):
                tag_uuids = [UUID(tag_id) for tag_id in tag_ids]
                await self.controller.sync_tags(term_id, tag_uuids)

            # タグ同期後、最新データを再取得
            await self.controller.load_initial_terms()

            self._close_edit_dialog()
            self.show_snack_bar(f"用語 '{updated_term.key}' を更新しました")
            normalized_status = self._normalize_status(updated_term.status)
            self.controller.update_tab(normalized_status)
            self.controller.select_term(updated_term.id)
            self._refresh_term_list()
            self._refresh_status_tabs()
            self._set_active_status_tab(normalized_status)
            self._show_detail()

        except ValueError as e:
            # バリデーションエラー
            logger.warning("Validation error during term update", extra={"error": str(e)})
            if self.page:
                self.show_error_snackbar(self.page, f"バリデーションエラー: {e}")

        except Exception:
            # その他のエラー
            logger.exception("Failed to update term")
            self._close_edit_dialog()
            if self.page:
                self.show_error_snackbar(self.page, "用語の更新に失敗しました")

    def _handle_edit_dialog_cancel(self) -> None:
        """編集ダイアログのキャンセルをハンドリングする。"""
        self._close_edit_dialog()

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

    def _close_edit_dialog(self) -> None:
        """用語編集ダイアログを閉じる。"""
        if hasattr(self, "edit_dialog") and self.edit_dialog and self.page:
            # 1. ダイアログを閉じる
            self.edit_dialog.dialog.open = False
            self.page.update()

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
