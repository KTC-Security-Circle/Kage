"""カラーパレットコンポーネント

タグの色選択のためのカラーパレットUIコンポーネント。
10色のプリセットカラーから選択可能。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from views.theme import get_on_primary_color

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


def create_color_palette(
    available_colors: list[dict[str, str]],
    on_color_select: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
) -> ft.Control:  # type: ignore[name-defined]
    """カラーパレットを構築する。

    Args:
        available_colors: 利用可能な色のリスト（name, value, hex）
        on_color_select: 色選択時のコールバック

    Returns:
        カラーパレットコンポーネント
    """
    import flet as ft

    color_buttons = [
        ft.Container(
            content=ft.Text(
                color["name"],
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=get_on_primary_color(),
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=color["value"],
            width=80,
            height=40,
            border_radius=ft.border_radius.all(8),
            padding=ft.padding.all(8),
            on_click=lambda e, c=color: on_color_select(e, c),
            tooltip=f"{color['name']} ({color['hex']})",
        )
        for color in available_colors
    ]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "色を選択",
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(
                    content=ft.GridView(
                        controls=color_buttons,
                        runs_count=5,
                        spacing=8,
                        run_spacing=8,
                        max_extent=80,
                    ),
                    height=120,
                ),
            ],
            spacing=12,
        ),
    )
