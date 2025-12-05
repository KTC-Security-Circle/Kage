"""プロジェクト未選択状態のコンポーネント。"""

from __future__ import annotations

import flet as ft

from views.theme import get_grey_color, get_outline_color


class ProjectNoSelection(ft.Card):
    """プロジェクト未選択状態を表示するコンポーネント。"""

    def __init__(self) -> None:
        """未選択状態コンポーネントを初期化。"""
        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN,
                            size=48,
                            color=get_outline_color(),
                        ),
                        ft.Text(
                            "プロジェクトを選択して詳細を表示",
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=get_grey_color(500),
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=48,
            ),
            expand=True,
        )
