"""統計カード群コンポーネント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.theme import (
    BORDER_RADIUS,
    BORDER_WIDTH,
    OPACITY,
    SPACING,
    create_subtle_shadow,
    get_on_surface_color,
    get_outline_color,
    get_surface_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class StatCardData:
    """統計カードのデータ。"""

    title: str
    value: str
    subtitle: str
    icon: str
    on_click: Callable[[], None] | None = None


class StatsCards(ft.ResponsiveRow):
    """統計カード群を表示するコンポーネント。"""

    def __init__(
        self,
        *,
        stats: list[StatCardData],
    ) -> None:
        """統計カード群を初期化。

        Args:
            stats: 統計カードデータのリスト
        """
        self.stats = stats

        super().__init__(
            controls=[self._build_stat_card(stat) for stat in stats],
            spacing=SPACING.md,
            run_spacing=SPACING.md,
        )

    def _build_stat_card(self, stat: StatCardData) -> ft.Container:
        """個別統計カードを構築する。

        Args:
            stat: 統計カードデータ

        Returns:
            統計カードのコンテナ
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                stat.title,
                                size=18,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Icon(stat.icon, size=20, color=get_on_surface_color()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=SPACING.sm),
                    ft.Text(
                        stat.value,
                        size=36,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        stat.subtitle,
                        size=14,
                        color=ft.Colors.with_opacity(OPACITY.medium, get_text_secondary_color()),
                    ),
                ],
                spacing=0,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.lg),
            bgcolor=get_surface_color(),
            border_radius=BORDER_RADIUS.lg,
            border=ft.border.all(
                BORDER_WIDTH.thin,
                ft.Colors.with_opacity(OPACITY.light, get_outline_color()),
            ),
            shadow=create_subtle_shadow(),
            on_click=lambda _, _stat=stat: _stat.on_click() if _stat.on_click else None,
            ink=True,
            col={"xs": 12, "sm": 6, "md": 4},
        )

    def update_stats(self, stats: list[StatCardData]) -> None:
        """統計データを更新する。

        Args:
            stats: 新しい統計カードデータのリスト
        """
        self.stats = stats
        self.controls = [self._build_stat_card(stat) for stat in stats]
        self.update()
