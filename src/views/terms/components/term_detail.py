"""Term detail component for displaying full term information."""

import flet as ft

from views.sample import SampleTerm, SampleTermStatus


class TermDetail(ft.Container):
    """Detailed view of a terminology entry."""

    def __init__(
        self,
        term: SampleTerm | None = None,
        on_edit: ft.OptionalEventCallable = None,
        on_tag_click: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize term detail view.

        Args:
            term: SampleTerm entry to display
            on_edit: Callback when edit button is clicked
            on_tag_click: Callback when a tag is clicked
        """
        super().__init__()
        self.term = term
        self.on_edit = on_edit
        self.on_tag_click = on_tag_click

        # 初期化時にコンテンツを構築
        self._build_container_content()

    def _build_container_content(self) -> None:
        """Build the content."""
        if not self.term:
            self.content = self._build_empty_state()
        else:
            self.content = ft.Column(
                controls=[
                    self._build_header(),
                    self._build_content(),
                    self._build_metadata(),
                    self._build_edit_button(),
                ],
                spacing=16,
            )
        self.padding = 24

    def build(self) -> ft.Control:
        """Build the term detail view."""
        # この方法は使用しない（ft.Containerを継承しているため）
        return self
        """Build the term detail view."""
        if not self.term:
            return self._build_empty_state()

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._build_header(),
                    self._build_content(),
                    self._build_metadata(),
                    self._build_edit_button(),
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
        )

    def _build_empty_state(self) -> ft.Control:
        """Build empty state when no term is selected."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE_OUTLINED,
                        size=64,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Text(
                        "用語を選択して詳細を表示",
                        size=18,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=48,
            alignment=ft.alignment.center,
        )

    def _build_header(self) -> ft.Control:
        """Build the header section with title and status."""
        if not self.term:
            return ft.Container()  # Return empty container if no term

        status_badge = self._get_status_badge()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.BOOK,
                                size=24,
                                color=ft.Colors.PRIMARY,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        self.term.title,
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"キー: {self.term.key}",
                                        size=14,
                                        color=ft.Colors.OUTLINE,
                                        style=ft.TextStyle(font_family="monospace"),
                                    ),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    status_badge,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=8,
        )

    def _build_content(self) -> ft.Control:
        """Build the main content section."""
        if not self.term:
            return ft.Container()  # Return empty container if no term

        sections = []

        # Description section
        sections.append(self._build_description_section())

        # Synonyms section
        if self.term.synonyms:
            sections.append(self._build_synonyms_section())

        # Tags section
        if self.term.tags:
            sections.append(self._build_tags_section())

        # Source URL section
        if self.term.source_url:
            sections.append(self._build_source_section())

        return ft.Column(
            controls=sections,
            spacing=24,
        )

    def _build_description_section(self) -> ft.Control:
        """Build description section."""
        if not self.term:
            return ft.Container()

        return ft.Column(
            controls=[
                ft.Text(
                    "説明",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Text(
                    self.term.description or "説明が登録されていません",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=8,
        )

    def _build_synonyms_section(self) -> ft.Control:
        """Build synonyms section."""
        if not self.term:
            return ft.Container()

        synonym_chips = [
            ft.Container(
                content=ft.Text(
                    synonym,
                    size=14,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border_radius=16,
            )
            for synonym in self.term.synonyms
        ]

        return ft.Column(
            controls=[
                ft.Text(
                    "同義語",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Row(
                    controls=synonym_chips,
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=8,
        )

    def _build_tags_section(self) -> ft.Control:
        """Build tags section."""
        if not self.term:
            return ft.Container()

        tag_chips = []
        for tag_name in self.term.tags:
            chip = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.TAG,
                            size=16,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            tag_name,
                            size=14,
                            color=ft.Colors.PRIMARY,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.all(1, ft.Colors.PRIMARY),
                border_radius=16,
                on_click=lambda _, tag=tag_name: self._handle_tag_click(tag),
            )
            tag_chips.append(chip)

        return ft.Column(
            controls=[
                ft.Text(
                    "タグ",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Row(
                    controls=tag_chips,
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=8,
        )

    def _build_source_section(self) -> ft.Control:
        """Build source URL section."""
        return ft.Column(
            controls=[
                ft.Text(
                    "出典",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.ElevatedButton(
                    text="外部リンクを開く",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=self._handle_source_click,
                ),
            ],
            spacing=8,
        )

    def _build_metadata(self) -> ft.Control:
        """Build metadata section with dates."""
        if not self.term:
            return ft.Container()

        created_date = self.term.created_at.strftime("%Y年%m月%d日")
        updated_date = self.term.updated_at.strftime("%Y年%m月%d日")

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "作成日",
                                size=12,
                                color=ft.Colors.OUTLINE,
                            ),
                            ft.Text(
                                created_date,
                                size=14,
                                color=ft.Colors.ON_SURFACE,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "最終更新",
                                size=12,
                                color=ft.Colors.OUTLINE,
                            ),
                            ft.Text(
                                updated_date,
                                size=14,
                                color=ft.Colors.ON_SURFACE,
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=32,
            ),
            padding=ft.padding.all(16),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )

    def _build_edit_button(self) -> ft.Control:
        """Build edit button."""
        return ft.ElevatedButton(
            text="編集",
            icon=ft.Icons.EDIT,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY,
            ),
            on_click=self._handle_edit,
            width=200,
        )

    def _get_status_badge(self) -> ft.Control:
        """Get status badge based on term status."""
        if not self.term:
            return ft.Container()

        status_config = {
            SampleTermStatus.APPROVED: {
                "text": "承認済み",
                "bgcolor": ft.Colors.PRIMARY,
                "color": ft.Colors.ON_PRIMARY,
            },
            SampleTermStatus.DRAFT: {
                "text": "草案",
                "bgcolor": ft.Colors.OUTLINE_VARIANT,
                "color": ft.Colors.OUTLINE,
            },
            SampleTermStatus.DEPRECATED: {
                "text": "非推奨",
                "bgcolor": ft.Colors.ERROR_CONTAINER,
                "color": ft.Colors.ON_ERROR_CONTAINER,
            },
        }

        config = status_config.get(self.term.status, status_config[SampleTermStatus.DRAFT])

        return ft.Container(
            content=ft.Text(
                config["text"],
                size=14,
                color=config["color"],
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor=config["bgcolor"],
            border_radius=8,
        )

    def _handle_edit(self, _: ft.ControlEvent) -> None:
        """Handle edit button click."""
        if self.on_edit and self.term:
            self.on_edit(self.term)

    def _handle_tag_click(self, tag_name: str) -> None:
        """Handle tag click event."""
        if self.on_tag_click:
            self.on_tag_click(tag_name)

    def _handle_source_click(self, _: ft.ControlEvent) -> None:
        """Handle source URL click."""
        if self.term and self.term.source_url:
            # Open URL in browser - this would need platform-specific implementation
            pass

    def update_term(self, term: SampleTerm | None) -> None:
        """Update the displayed term.

        Args:
            term: New SampleTerm entry to display
        """
        self.term = term
        self._build_container_content()
        self.update()
