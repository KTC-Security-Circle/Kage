"""プロジェクトがない場合の空状態コンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import get_grey_color, get_on_primary_color, get_outline_color, get_primary_color

if TYPE_CHECKING:
    from collections.abc import Callable


class ProjectEmptyState(ft.Container):
    """プロジェクトがない場合の空状態を表示するコンポーネント。"""

    def __init__(self, *, on_create: Callable[[], None] | None = None) -> None:
        """空状態コンポーネントを初期化。

        Args:
            on_create: 新規作成ボタンのコールバック
        """
        self.on_create = on_create

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.FOLDER_OPEN_OUTLINED,
                        size=64,
                        color=get_outline_color(),
                    ),
                    ft.Text(
                        "プロジェクトがありません",
                        theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color=get_grey_color(600),
                    ),
                    ft.Text(
                        "新規プロジェクトを作成してタスクを整理しましょう",
                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=get_grey_color(600),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        text="最初のプロジェクトを作成",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: self._handle_create() if self.on_create else None,
                        bgcolor=get_primary_color(),
                        color=get_on_primary_color(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _handle_create(self) -> None:
        """新規作成ハンドラ。"""
        if self.on_create:
            self.on_create()
