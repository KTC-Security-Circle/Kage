"""Terms management view implementation.

【責務】
    レイアウト構築とイベント配線を担当。
    Controller/Presenterを活用し、UIの構築に集中する。

    - BaseViewを継承し、with_loading/notify_error等を利用
    - コンポーネントの組み合わせとレイアウト構成
    - イベントハンドラでControllerへ委譲
    - State変更後の差分更新

【責務外（他層の担当）】
    - 状態管理 → State
    - ビジネスロジック → Controller
    - UI整形 → Presenter
    - 純粋関数 → utils
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.sample import SampleTermStatus
from views.shared.base_view import BaseView, BaseViewProps

from .components.action_bar import ActionBarProps, TermActionBar
from .components.status_tabs import StatusTabsProps, TermStatusTabs
from .components.term_list import TermList, TermListProps
from .controller import TermsController
from .presenter import get_empty_message
from .state import TermsViewState

if TYPE_CHECKING:
    from uuid import UUID


class TermsView(BaseView):
    """社内用語管理のメインビュー。"""

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
        self.controller = TermsController(state=self.term_state)

        # Components
        self.action_bar: TermActionBar | None = None
        self.status_tabs: TermStatusTabs | None = None
        self.term_list: TermList | None = None

        # Initial load
        self.controller.load_initial_terms()

    def build(self) -> ft.Control:
        """Build the main content area."""
        return self.build_content()

    def build_content(self) -> ft.Control:
        """Build the main content area."""
        # Header
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.title,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"{self.description} ({len(self.term_state.all_terms)}件)",
                        size=16,
                        color=ft.Colors.OUTLINE,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(24),
        )

        # Action bar
        action_bar_props = ActionBarProps(
            on_search=self._handle_search,
            on_create=self._handle_create_term,
        )
        self.action_bar = TermActionBar(action_bar_props)

        # Status tabs
        counts = self.controller.get_counts()
        status_tabs_props = StatusTabsProps(
            approved_count=counts[SampleTermStatus.APPROVED],
            draft_count=counts[SampleTermStatus.DRAFT],
            deprecated_count=counts[SampleTermStatus.DEPRECATED],
            on_status_change=self._handle_status_change,
        )
        self.status_tabs = TermStatusTabs(status_tabs_props)

        # Term list
        derived_terms = self.term_state.derived_terms()
        term_list_props = TermListProps(
            terms=derived_terms,
            selected_term_id=self.term_state.selected_term_id,
            empty_message=get_empty_message(self.term_state.current_tab),
            on_term_select=self._handle_term_select_uuid,
        )
        self.term_list = TermList(term_list_props)

        # Main content
        main_content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.status_tabs,
                            self.term_list,
                        ],
                        spacing=16,
                    ),
                    expand=True,
                    padding=ft.padding.all(16),
                ),
            ],
            expand=True,
        )

        return ft.Column(
            controls=[
                header,
                ft.Container(
                    content=self.action_bar,
                    padding=ft.padding.symmetric(horizontal=24),
                ),
                main_content,
            ],
            expand=True,
        )

    def _handle_search(self, query: str) -> None:
        """検索クエリの変更をハンドリングする。

        Args:
            query: 検索クエリ
        """
        self.controller.update_search(query)
        self._refresh_term_list()

    def _handle_status_change(self, status: SampleTermStatus) -> None:
        """ステータスタブの変更をハンドリングする。

        Args:
            status: 選択されたステータス
        """
        self.controller.update_tab(status)
        self._refresh_term_list()
        self._refresh_status_tabs()

    def _handle_term_select_uuid(self, term_id: UUID) -> None:
        """用語選択をハンドリングする（UUID）。

        Args:
            term_id: 選択された用語のID
        """
        self.controller.select_term(term_id)
        self._refresh_term_list()

    def _handle_term_select(self, term_id: str) -> None:
        """用語選択をハンドリングする（文字列）。

        Args:
            term_id: 選択された用語のID
        """
        from uuid import UUID

        self._handle_term_select_uuid(UUID(term_id))

    def _handle_create_term(self) -> None:
        """用語作成ボタンのクリックをハンドリングする。"""
        self.show_snack_bar("用語作成機能は準備中です")

    def _refresh_term_list(self) -> None:
        """用語リストを更新する。"""
        if self.term_list:
            derived_terms = self.term_state.derived_terms()
            term_list_props = TermListProps(
                terms=derived_terms,
                selected_term_id=self.term_state.selected_term_id,
                empty_message=get_empty_message(self.term_state.current_tab),
                on_term_select=self._handle_term_select_uuid,
            )
            self.term_list.set_props(term_list_props)

    def _refresh_status_tabs(self) -> None:
        """ステータスタブを更新する。"""
        if self.status_tabs:
            counts = self.controller.get_counts()
            status_tabs_props = StatusTabsProps(
                approved_count=counts[SampleTermStatus.APPROVED],
                draft_count=counts[SampleTermStatus.DRAFT],
                deprecated_count=counts[SampleTermStatus.DEPRECATED],
                on_status_change=self._handle_status_change,
            )
            self.status_tabs.set_props(status_tabs_props)
