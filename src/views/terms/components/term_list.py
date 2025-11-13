"""Term list component."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.sample import SampleTerm, SampleTermStatus

from .shared.constants import (
    CARD_PADDING,
    CARD_SPACING,
    MAX_DESCRIPTION_LINES,
    MAX_SYNONYMS_DISPLAY,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID


@dataclass(frozen=True, slots=True)
class TermListProps:
    """TermList用のプロパティ。"""

    terms: list[SampleTerm]
    selected_term_id: UUID | None = None
    empty_message: str = "用語がありません"
    on_term_select: Callable[[UUID], None] | None = None


class TermList(ft.Column):
    """用語リストコンポーネント。"""

    def __init__(self, props: TermListProps) -> None:
        """Initialize term list.

        Args:
            props: リストの設定プロパティ
        """
        super().__init__()
        self.props = props
        self.spacing = CARD_SPACING
        self.scroll = ft.ScrollMode.AUTO

        self._build_list()

    def _build_list(self) -> None:
        """リストを構築する。"""
        if not self.props.terms:
            self.controls = [self._build_empty_state()]
            return

        self.controls = [self._build_term_card(term) for term in self.props.terms]

    def _build_empty_state(self) -> ft.Control:
        """空状態を構築する。"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE_OUTLINED,
                        size=48,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Text(
                        self.props.empty_message,
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

    def _build_term_card(self, term: SampleTerm) -> ft.Control:
        """用語カードを構築する。

        Args:
            term: 用語データ

        Returns:
            用語カードコントロール
        """
        is_selected = self.props.selected_term_id == term.id
        status_icon = self._get_status_icon(term.status)

        card_content = ft.Column(
            controls=[
                # Header
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
                # Description
                ft.Text(
                    term.description or "説明なし",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    max_lines=MAX_DESCRIPTION_LINES,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                # Synonyms
                self._build_synonyms(term),
            ],
            spacing=CARD_SPACING,
        )

        return ft.Container(
            content=card_content,
            padding=CARD_PADDING,
            border_radius=8,
            border=ft.border.all(
                1,
                ft.Colors.PRIMARY if is_selected else ft.Colors.OUTLINE_VARIANT,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_selected else None,
            on_click=lambda _, t=term: self._handle_click(t.id),
            data=term.id,
        )

    def _build_synonyms(self, term: SampleTerm) -> ft.Control:
        """同義語表示を構築する。

        Args:
            term: 用語データ

        Returns:
            同義語表示コントロール
        """
        if not term.synonyms:
            return ft.Container()

        visible_synonyms = term.synonyms[:MAX_SYNONYMS_DISPLAY]
        synonym_chips = [
            ft.Container(
                content=ft.Text(
                    synonym,
                    size=12,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border_radius=4,
            )
            for synonym in visible_synonyms
        ]

        if len(term.synonyms) > MAX_SYNONYMS_DISPLAY:
            synonym_chips.append(
                ft.Container(
                    content=ft.Text(
                        f"+{len(term.synonyms) - MAX_SYNONYMS_DISPLAY}",
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

    def _get_status_icon(self, status: SampleTermStatus) -> ft.Control:
        """ステータスアイコンを取得する。

        Args:
            status: 用語ステータス

        Returns:
            ステータスアイコン
        """
        icon_map = {
            SampleTermStatus.APPROVED: ft.Icons.CHECK_CIRCLE,
            SampleTermStatus.DRAFT: ft.Icons.HELP_OUTLINE,
            SampleTermStatus.DEPRECATED: ft.Icons.CANCEL,
        }
        return ft.Icon(
            icon_map.get(status, ft.Icons.HELP_OUTLINE),
            size=16,
        )

    def _handle_click(self, term_id: UUID) -> None:
        """カードクリックをハンドリングする。

        Args:
            term_id: クリックされた用語のID
        """
        if self.props.on_term_select:
            self.props.on_term_select(term_id)

    def set_props(self, props: TermListProps) -> None:
        """新しいプロパティを設定する。

        Args:
            props: 新しいプロパティ
        """
        self.props = props
        self._build_list()
        with contextlib.suppress(AssertionError):
            self.update()
