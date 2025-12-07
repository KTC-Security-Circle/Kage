"""デイリーレビューカードコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from views.theme import (
    BORDER_RADIUS,
    BORDER_WIDTH,
    OPACITY,
    SPACING,
    create_medium_shadow,
    get_accent_background_color,
    get_accent_border_color,
    get_on_surface_color,
    get_outline_color,
    get_surface_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class DailyReviewCard(ft.Container):
    """デイリーレビューカードを表示するコンポーネント。"""

    def __init__(
        self,
        *,
        review: dict[str, Any],
        on_action_click: Callable[[str], None] | None = None,
    ) -> None:
        """デイリーレビューカードを初期化。

        Args:
            review: デイリーレビュー情報（message, color, icon, action_text, action_route）
            on_action_click: アクションボタンクリック時のコールバック
        """
        self.review = review
        self.on_action_click = on_action_click

        super().__init__(
            content=self._build_content(),
            padding=ft.padding.all(SPACING.lg),
            bgcolor=self._get_background_color(),
            border_radius=BORDER_RADIUS.lg,
            border=ft.border.all(BORDER_WIDTH.thin, self._get_border_color()),
        )

    def _get_background_color(self) -> str:
        """背景色を取得する。"""
        color_name = self.review.get("color", "primary")
        return ft.Colors.with_opacity(OPACITY.subtle, get_accent_background_color(color_name))

    def _get_border_color(self) -> str:
        """ボーダー色を取得する。"""
        color_name = self.review.get("color", "primary")
        return ft.Colors.with_opacity(OPACITY.border_light, get_accent_border_color(color_name))

    def _get_icon(self) -> str:
        """アイコンを取得する。"""
        icon_map = {
            "error": ft.Icons.GITE_ROUNDED,
            "coffee": ft.Icons.COFFEE,
            "play_arrow": ft.Icons.BOLT,
            "trending_up": ft.Icons.TRENDING_UP,
            "lightbulb": ft.Icons.AUTO_AWESOME,
            "check_circle": ft.Icons.CHECK_CIRCLE,
            "wb_sunny": ft.Icons.WB_SUNNY,
        }
        return icon_map.get(self.review.get("icon", ""), ft.Icons.INFO)

    def _build_content(self) -> ft.Control:
        """カードのコンテンツを構築する。"""
        icon_container = ft.Container(
            content=ft.Icon(self._get_icon(), size=24, color=get_on_surface_color()),
            padding=SPACING.sm + SPACING.xs,
            bgcolor=get_surface_color(),
            border_radius=BORDER_RADIUS.round,
            shadow=create_medium_shadow(),
        )

        message_text = ft.Text(
            self.review.get("message", ""),
            size=18,
            weight=ft.FontWeight.NORMAL,
            color=get_on_surface_color(),
        )

        action_button = None
        if self.on_action_click:
            action_button = ft.Container(
                content=ft.OutlinedButton(
                    text=self.review.get("action_text", ""),
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda _: self.on_action_click(self.review.get("action_route", ""))
                    if self.on_action_click
                    else None,
                    style=ft.ButtonStyle(
                        color=get_on_surface_color(),
                        bgcolor=get_surface_color(),
                        side=ft.BorderSide(
                            BORDER_WIDTH.thin,
                            ft.Colors.with_opacity(OPACITY.border_light, get_outline_color()),
                        ),
                    ),
                ),
                margin=ft.margin.only(top=SPACING.sm),
            )

        controls: list[ft.Control] = [
            ft.Row(
                [
                    icon_container,
                    ft.Container(
                        content=ft.Column([message_text], spacing=0),
                        expand=True,
                    ),
                ],
                spacing=SPACING.md,
                alignment=ft.MainAxisAlignment.START,
            ),
        ]

        if action_button:
            controls.append(action_button)

        return ft.Column(controls, spacing=0)

    def update_review(self, review: dict[str, Any]) -> None:
        """レビュー情報を更新する。

        Args:
            review: 新しいレビュー情報
        """
        self.review = review
        self.content = self._build_content()
        self.bgcolor = self._get_background_color()
        self.border = ft.border.all(BORDER_WIDTH.thin, self._get_border_color())
        self.update()
