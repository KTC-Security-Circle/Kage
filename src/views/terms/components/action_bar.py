"""Action bar component for terms management."""

import flet as ft


class TermActionBar(ft.Row):
    """Action bar with search and create functionality for terms."""

    def __init__(
        self,
        on_search: ft.OptionalEventCallable = None,
        on_create_term: ft.OptionalEventCallable = None,
        search_placeholder: str = "用語、キー、同義語で検索...",
    ) -> None:
        """Initialize term action bar.

        Args:
            on_search: Callback when search query changes
            on_create_term: Callback when create term button is clicked
            search_placeholder: Placeholder text for search field
        """
        super().__init__()
        self.on_search = on_search
        self.on_create_term = on_create_term
        self.search_placeholder = search_placeholder
        self.search_field: ft.TextField | None = None

        # 初期化時にコントロールを構築
        self._build_controls()

    def _build_controls(self) -> None:
        """Build and setup controls."""
        self.search_field = ft.TextField(
            hint_text=self.search_placeholder,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=8,
            on_change=self._handle_search,
            expand=True,
        )

        create_button = ft.ElevatedButton(
            text="新しい用語",
            icon=ft.Icons.ADD,
            on_click=self._handle_create,
        )

        self.controls = [
            self.search_field,
            create_button,
        ]
        self.spacing = 16
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def build(self) -> ft.Control:
        """Build the action bar."""
        # この方法は使用しない（ft.Rowを継承しているため）
        return self

    def _handle_search(self, e: ft.ControlEvent) -> None:
        """Handle search input change."""
        if self.on_search:
            self.on_search(e.control.value)

    def _handle_create(self, _: ft.ControlEvent) -> None:
        """Handle create term button click."""
        if self.on_create_term:
            self.on_create_term()

    def clear_search(self) -> None:
        """Clear the search field."""
        if self.search_field:
            self.search_field.value = ""
            self.search_field.update()

    def get_search_query(self) -> str:
        """Get current search query.

        Returns:
            Current search query string
        """
        return self.search_field.value or "" if self.search_field else ""
