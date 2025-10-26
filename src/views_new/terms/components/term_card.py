"""Term card components for displaying terminology entries."""

import flet as ft

from models.terminology import Terminology, TerminologyStatus

# Constants
MAX_SYNONYMS_DISPLAY = 3


# 定数
MAX_SYNONYMS_DISPLAY = 3


class TermCard(ft.Container):
    """Individual term card for displaying terminology information."""

    def __init__(
        self,
        term: Terminology,
        *,
        is_selected: bool = False,
        on_click: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize term card.

        Args:
            term: Terminology model instance
            is_selected: Whether this card is currently selected
            on_click: Callback when card is clicked
        """
        super().__init__()
        self.term = term
        self.is_selected = is_selected
        self.on_click = on_click

    def build(self) -> ft.Control:
        """Build the term card."""
        status_icon = self._get_status_icon()
        status_badge = self._get_status_badge()

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header with title and status
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    status_icon,
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                self.term.title,
                                                weight=ft.FontWeight.BOLD,
                                                size=16,
                                            ),
                                            ft.Text(
                                                f"キー: {self.term.key}",
                                                size=12,
                                                color=ft.Colors.OUTLINE,
                                            ),
                                        ],
                                        spacing=2,
                                        tight=True,
                                    ),
                                ],
                                spacing=8,
                            ),
                            status_badge,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Description
                    ft.Text(
                        self.term.description or "説明なし",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    # Synonyms
                    self._build_synonyms_display(),
                ],
                spacing=8,
                tight=True,
            ),
            padding=16,
            border_radius=8,
            border=ft.border.all(
                1,
                ft.Colors.PRIMARY if self.is_selected else ft.Colors.OUTLINE_VARIANT,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if self.is_selected else None,
            on_click=self._handle_click,
        )

    def _get_status_icon(self) -> ft.Control:
        """Get status icon based on term status."""
        icon_map = {
            TerminologyStatus.APPROVED: ft.Icons.CHECK_CIRCLE,
            TerminologyStatus.DRAFT: ft.Icons.HELP_OUTLINE,
            TerminologyStatus.DEPRECATED: ft.Icons.CANCEL,
        }

        return ft.Icon(
            icon_map.get(self.term.status, ft.Icons.HELP_OUTLINE),
            size=16,
        )

    def _get_status_badge(self) -> ft.Control:
        """Get status badge based on term status."""
        status_config = {
            TerminologyStatus.APPROVED: {
                "text": "承認済み",
                "bgcolor": ft.Colors.PRIMARY,
                "color": ft.Colors.ON_PRIMARY,
            },
            TerminologyStatus.DRAFT: {
                "text": "草案",
                "bgcolor": ft.Colors.OUTLINE_VARIANT,
                "color": ft.Colors.OUTLINE,
            },
            TerminologyStatus.DEPRECATED: {
                "text": "非推奨",
                "bgcolor": ft.Colors.OUTLINE_VARIANT,
                "color": ft.Colors.OUTLINE,
            },
        }

        config = status_config.get(self.term.status, status_config[TerminologyStatus.DRAFT])

        return ft.Container(
            content=ft.Text(
                config["text"],
                size=12,
                color=config["color"],
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=config["bgcolor"],
            border_radius=4,
        )

    def _build_synonyms_display(self) -> ft.Control:
        """Build synonyms display with chips."""
        if not self.term.synonyms:
            return ft.Container()

        visible_synonyms = self.term.synonyms[:3]

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

        if len(self.term.synonyms) > MAX_SYNONYMS_DISPLAY:
            synonym_chips.append(
                ft.Container(
                    content=ft.Text(
                        f"+{len(self.term.synonyms) - 3}",
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

    def _handle_click(self, _: ft.ControlEvent) -> None:
        """Handle card click event."""
        if self.on_click:
            self.on_click(self.term)

    def update_selection(self, *, is_selected: bool) -> None:
        """Update selection state of the card.

        Args:
            is_selected: New selection state
        """
        self.is_selected = is_selected
        self.update()


class TermCardList(ft.Control):
    """List container for term cards."""

    def __init__(
        self,
        terms: list[Terminology],
        selected_term: Terminology | None = None,
        on_term_select: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize term card list.

        Args:
            terms: List of terminology entries to display
            selected_term: Currently selected term
            on_term_select: Callback when a term is selected
        """
        super().__init__()
        self.terms = terms
        self.selected_term = selected_term
        self.on_term_select = on_term_select
        self.term_cards: list[TermCard] = []

    def build(self) -> ft.Control:
        """Build the term card list."""
        if not self.terms:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.ARTICLE_OUTLINED,
                            size=48,
                            color=ft.Colors.OUTLINE,
                        ),
                        ft.Text(
                            "用語がありません",
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

        self.term_cards = []
        card_controls = []

        for term in self.terms:
            is_selected = self.selected_term and term.id == self.selected_term.id
            card = TermCard(
                term=term,
                is_selected=is_selected,
                on_click=self._handle_term_select,
            )
            self.term_cards.append(card)
            card_controls.append(card)

        return ft.Column(
            controls=card_controls,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

    def _handle_term_select(self, term: Terminology) -> None:
        """Handle term selection.

        Args:
            term: Selected terminology entry
        """
        self.selected_term = term

        # Update selection state of all cards
        for card in self.term_cards:
            card.update_selection(card.term.id == term.id)

        if self.on_term_select:
            self.on_term_select(term)

    def update_terms(
        self,
        terms: list[Terminology],
        selected_term: Terminology | None = None,
    ) -> None:
        """Update the terms displayed in the list.

        Args:
            terms: New list of terminology entries
            selected_term: New selected term
        """
        self.terms = terms
        self.selected_term = selected_term
        self.update()
