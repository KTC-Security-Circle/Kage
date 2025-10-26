"""Terms management view implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views_new.sample import SampleTerm, SampleTermStatus, get_sample_terms
from views_new.shared.base_view import BaseView

from .components.action_bar import TermActionBar
from .components.status_tabs import TermStatusTabs

if TYPE_CHECKING:
    from .components.term_detail import TermDetail


class TermsView(BaseView):
    """Main view for terminology management."""

    def __init__(self, page: ft.Page) -> None:
        """Initialize terms view.

        Args:
            page: Flet page instance
        """
        super().__init__(page)
        self.title = "社内用語管理"
        self.description = "社内固有の用語・略語・定義を管理"

        # Sample data for now
        self.terms: list[SampleTerm] = []
        self.filtered_terms: list[SampleTerm] = []
        self.selected_term: SampleTerm | None = None
        self.current_status = SampleTermStatus.APPROVED
        self.search_query = ""

        # Components
        self.action_bar: TermActionBar | None = None
        self.status_tabs: TermStatusTabs | None = None
        self.term_detail: TermDetail | None = None
        self.term_list_container: ft.Container | None = None

        self._load_sample_data()

    def build(self) -> ft.Control:
        """Build the main content area."""
        from loguru import logger

        logger.info("TermsView.build() called")
        logger.info(f"Terms loaded: {len(self.terms)} items")
        return self.build_content()

    def build_content(self) -> ft.Control:
        """Build the main content area."""
        # Header with title and description
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.title,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"{self.description} ({len(self.terms)}件)",
                        size=16,
                        color=ft.Colors.OUTLINE,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(24),
        )

        # Action bar with search and create
        self.action_bar = TermActionBar(
            on_search=self._handle_search,
            on_create_term=self._handle_create_term,
        )

        # Status tabs
        self._update_status_counts()
        self.status_tabs = TermStatusTabs(
            approved_count=len([t for t in self.terms if t.status == SampleTermStatus.APPROVED]),
            draft_count=len([t for t in self.terms if t.status == SampleTermStatus.DRAFT]),
            deprecated_count=len([t for t in self.terms if t.status == SampleTermStatus.DEPRECATED]),
            on_status_change=self._handle_status_change,
        )

        # Main content area with list and detail
        self._filter_terms()

        # GitHubイシュー#2793の解決策を適用：Rowにexpand=Trueを設定
        main_content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.status_tabs,
                            self._build_term_list(),
                        ],
                        spacing=16,
                    ),
                    expand=True,
                    padding=ft.padding.all(16),
                ),
            ],
            expand=True,  # この設定が重要
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
            expand=True,  # GitHubイシューの解決策：親のColumnにもexpandを設定
        )

    def _build_term_list(self) -> ft.Control:
        """Build the terms list container."""
        if not self.filtered_terms:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.ARTICLE_OUTLINED,
                            size=48,
                            color=ft.Colors.OUTLINE,
                        ),
                        ft.Text(
                            f"{self._get_status_text()}の用語はありません",
                            size=16,
                            color=ft.Colors.OUTLINE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                padding=32,
                alignment=ft.alignment.center,
            )

        # Build term cards
        term_cards = []
        for term in self.filtered_terms:
            is_selected_bool = self.selected_term is not None and term.id == self.selected_term.id
            card = self._build_term_card(term, is_selected=is_selected_bool)
            term_cards.append(card)

        self.term_list_container = ft.Container(
            content=ft.Column(
                controls=term_cards,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        return self.term_list_container

    def _build_term_card(self, term: SampleTerm, *, is_selected: bool) -> ft.Control:
        """Build individual term card."""
        status_icon = self._get_status_icon(term.status)

        card_content = ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                status_icon,
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            term.title,
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                        ),
                                        ft.Text(
                                            f"キー: {term.key}",
                                            size=12,
                                            color=ft.Colors.OUTLINE,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                ),
                # Description
                ft.Text(
                    term.description or "説明なし",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                # Synonyms
                self._build_card_synonyms(term),
            ],
            spacing=8,
        )

        return ft.Container(
            content=card_content,
            padding=16,
            border_radius=8,
            border=ft.border.all(
                1,
                ft.Colors.PRIMARY if is_selected else ft.Colors.OUTLINE_VARIANT,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_selected else None,
            on_click=lambda _, t=term: self._handle_term_select(t),
        )

    def _build_card_synonyms(self, term: SampleTerm) -> ft.Control:
        """Build synonyms display for card."""
        if not term.synonyms:
            return ft.Container()

        max_display = 3
        visible_synonyms = term.synonyms[:max_display]

        synonym_chips = [
            ft.Container(
                content=ft.Text(
                    str(synonym),
                    size=12,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border_radius=4,
            )
            for synonym in visible_synonyms
        ]

        if len(term.synonyms) > max_display:
            synonym_chips.append(
                ft.Container(
                    content=ft.Text(
                        f"+{len(term.synonyms) - max_display}",
                        size=12,
                        color=ft.Colors.ON_SECONDARY_CONTAINER,
                    ),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    border_radius=4,
                )
            )

        return ft.Row(
            controls=synonym_chips,
            spacing=4,
            wrap=True,
        )

    def _build_term_detail(self) -> ft.Control:
        """Build the term detail panel."""
        # 現在は詳細パネルを非表示にして、リストのみ表示
        return ft.Container(
            content=ft.Text("詳細表示は準備中です", color=ft.Colors.OUTLINE),
            padding=24,
        )

    def _get_status_icon(self, status: SampleTermStatus) -> ft.Control:
        """Get status icon for term status."""
        icon_map = {
            SampleTermStatus.APPROVED: ft.Icons.CHECK_CIRCLE,
            SampleTermStatus.DRAFT: ft.Icons.HELP_OUTLINE,
            SampleTermStatus.DEPRECATED: ft.Icons.CANCEL,
        }

        return ft.Icon(
            icon_map.get(status, ft.Icons.HELP_OUTLINE),
            size=16,
        )

    def _get_status_text(self) -> str:
        """Get status text for current status."""
        status_text = {
            SampleTermStatus.APPROVED: "承認済み",
            SampleTermStatus.DRAFT: "草案",
            SampleTermStatus.DEPRECATED: "非推奨",
        }
        return status_text.get(self.current_status, "承認済み")

    def _handle_search(self, query: str) -> None:
        """Handle search query change."""
        self.search_query = query.lower()
        self._filter_terms()
        self._refresh_term_list()

    def _handle_status_change(self, status: SampleTermStatus) -> None:
        """Handle status tab change."""
        self.current_status = status
        self._filter_terms()
        self._refresh_term_list()

    def _handle_term_select(self, term: SampleTerm) -> None:
        """Handle term selection."""
        self.selected_term = term
        if self.term_detail:
            self.term_detail.update_term(term)
        self._refresh_term_list()

    def _handle_create_term(self, _: ft.ControlEvent | None = None) -> None:
        """Handle create term button click."""
        # TODO: Implement term creation dialog
        self.show_snack_bar("用語作成機能は準備中です")

    def _handle_edit_term(self, term: SampleTerm) -> None:
        """Handle edit term button click."""
        # TODO: Implement term editing dialog
        self.show_snack_bar(f"用語「{term.title}」の編集機能は準備中です")

    def _handle_tag_click(self, tag_name: str) -> None:
        """Handle tag click."""
        # TODO: Navigate to tag view or filter by tag
        self.show_snack_bar(f"タグ「{tag_name}」の機能は準備中です")

    def _filter_terms(self) -> None:
        """Filter terms based on current status and search query."""
        # Filter by status
        status_filtered = [term for term in self.terms if term.status == self.current_status]

        # Filter by search query
        if self.search_query:
            self.filtered_terms = [
                term
                for term in status_filtered
                if (
                    self.search_query in term.title.lower()
                    or self.search_query in term.key.lower()
                    or (term.description and self.search_query in term.description.lower())
                    or any(self.search_query in synonym.lower() for synonym in term.synonyms)
                )
            ]
        else:
            self.filtered_terms = status_filtered

    def _refresh_term_list(self) -> None:
        """Refresh the term list display."""
        # ページ全体を更新
        if self.page:
            self.page.update()

    def _update_status_counts(self) -> None:
        """Update status counts for tabs."""
        if self.status_tabs:
            approved_count = len([t for t in self.terms if t.status == SampleTermStatus.APPROVED])
            draft_count = len([t for t in self.terms if t.status == SampleTermStatus.DRAFT])
            deprecated_count = len([t for t in self.terms if t.status == SampleTermStatus.DEPRECATED])

            self.status_tabs.update_counts(approved_count, draft_count, deprecated_count)

    def _load_sample_data(self) -> None:
        """Load sample terminology data."""
        self.terms = get_sample_terms()
        self.filtered_terms = self.terms.copy()
        self._filter_terms_by_status()

    def _filter_terms_by_status(self) -> None:
        """Filter terms by current status."""
        self.filtered_terms = [term for term in self.terms if term.status == self.current_status]
