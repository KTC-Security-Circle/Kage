"""Inboxメモセクションコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from views.theme import (
    BORDER_RADIUS,
    BORDER_WIDTH,
    OPACITY,
    SPACING,
    get_on_surface_color,
    get_outline_color,
    get_primary_color,
    get_surface_color,
    get_surface_variant_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class InboxMemosSection(ft.Container):
    """Inboxメモセクションを表示するコンポーネント。"""

    def __init__(
        self,
        *,
        memos: list[dict[str, Any]],
        on_memo_click: Callable[[str], None] | None = None,
        on_see_all_click: Callable[[], None] | None = None,
        max_display: int = 3,
    ) -> None:
        """Inboxメモセクションを初期化。

        Args:
            memos: メモのリスト
            on_memo_click: メモクリック時のコールバック
            on_see_all_click: 「すべて見る」クリック時のコールバック
            max_display: 最大表示件数
        """
        self.memos = memos[:max_display]
        self.on_memo_click = on_memo_click
        self.on_see_all_click = on_see_all_click

        super().__init__(
            content=self._build_content(),
            padding=ft.padding.all(24),
            bgcolor=get_surface_variant_color(),
            border_radius=12,
            border=ft.border.all(1, get_outline_color()),
        )

    def _build_content(self) -> ft.Control:
        """セクションのコンテンツを構築する。"""
        header = ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.AUTO_AWESOME, size=20, color=get_on_surface_color()),
                        ft.Text(
                            "メモ",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=SPACING.xs,
                ),
                ft.TextButton(
                    text="すべて見る",
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color=get_on_surface_color(),
                    style=ft.ButtonStyle(color=get_on_surface_color()),
                    on_click=lambda _: self.on_see_all_click() if self.on_see_all_click else None,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        description = ft.Text(
            "整理が必要なメモがあります。AIにタスクを生成させましょう。",
            size=14,
            color=get_text_secondary_color(),
        )

        memo_items = [self._build_memo_item(memo) for memo in self.memos]

        return ft.Column(
            [
                header,
                description,
                ft.Column(
                    memo_items,
                    spacing=SPACING.xs,
                ),
            ],
            spacing=SPACING.sm,
        )

    def _build_memo_item(self, memo: dict[str, Any]) -> ft.Container:
        """個別メモアイテムを構築する。

        Args:
            memo: メモ情報

        Returns:
            メモアイテムのコンテナ
        """
        max_content_length = 100
        content_preview = (
            memo["content"][:max_content_length] + "..."
            if len(memo["content"]) > max_content_length
            else memo["content"]
        )

        status_badge = self._build_status_badge(memo.get("ai_suggestion_status"))

        title_row = ft.Row(
            [
                ft.Text(
                    memo.get("title", ""),
                    size=14,
                    weight=ft.FontWeight.NORMAL,
                ),
            ],
            spacing=SPACING.xs,
        )
        if status_badge:
            title_row.controls.append(status_badge)

        return ft.Container(
            content=ft.Column(
                [
                    title_row,
                    ft.Text(
                        content_preview,
                        size=14,
                        color=ft.Colors.with_opacity(OPACITY.medium, get_on_surface_color()),
                        max_lines=2,
                    ),
                ],
                spacing=SPACING.xs,
                tight=True,
            ),
            padding=SPACING.sm + SPACING.xs,
            bgcolor=get_surface_color(),
            border_radius=BORDER_RADIUS.md,
            border=ft.border.all(
                BORDER_WIDTH.thin,
                ft.Colors.with_opacity(OPACITY.border_light, get_outline_color()),
            ),
            on_click=lambda _, _memo=memo: self.on_memo_click(_memo.get("id", "")) if self.on_memo_click else None,
            ink=True,
        )

    def _build_status_badge(self, ai_status: str | None) -> ft.Container | None:
        """AIステータスバッジを構築する。

        Args:
            ai_status: AIステータス（available/pending/not_requested）

        Returns:
            ステータスバッジまたはNone
        """
        if ai_status == "available":
            return ft.Container(
                content=ft.Text(
                    "AI提案あり",
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=get_primary_color("dark"),
                ),
                padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
                bgcolor=get_surface_variant_color(),
                border_radius=BORDER_RADIUS.sm,
                border=ft.border.all(BORDER_WIDTH.thin, get_primary_color()),
            )
        if ai_status == "pending":
            return ft.Container(
                content=ft.Text(
                    "AI処理中",
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.with_opacity(OPACITY.high, get_text_secondary_color()),
                ),
                padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
                bgcolor=ft.Colors.with_opacity(OPACITY.light, get_surface_variant_color()),
                border_radius=BORDER_RADIUS.sm,
                border=ft.border.all(
                    BORDER_WIDTH.thin,
                    ft.Colors.with_opacity(OPACITY.border_medium, get_outline_color()),
                ),
            )
        if ai_status == "not_requested":
            return ft.Container(
                content=ft.Text(
                    "AI未実行",
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.with_opacity(OPACITY.medium, get_text_secondary_color()),
                ),
                padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
                bgcolor="transparent",
                border_radius=BORDER_RADIUS.sm,
                border=ft.border.all(
                    BORDER_WIDTH.thin,
                    ft.Colors.with_opacity(OPACITY.border_medium, get_outline_color()),
                ),
            )
        return None

    def update_memos(self, memos: list[dict[str, Any]], max_display: int = 3) -> None:
        """メモリストを更新する。

        Args:
            memos: 新しいメモのリスト
            max_display: 最大表示件数
        """
        self.memos = memos[:max_display]
        self.content = self._build_content()
        self.update()
