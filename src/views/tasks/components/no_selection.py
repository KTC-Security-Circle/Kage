"""タスク未選択時の右ペイン表示コンポーネント。"""

from __future__ import annotations

import flet as ft

from views.theme import get_text_secondary_color


class TaskNoSelection(ft.Card):
    """タスク未選択時の右ペインに表示するプレースホルダー。"""

    def __init__(self) -> None:
        """未選択状態コンポーネントを初期化。"""
        super().__init__(
            content=self._build_content(),
            elevation=0,
        )

    def _build_content(self) -> ft.Control:
        """未選択状態のコンテンツを構築する。"""
        icon = ft.Icon(
            name=ft.Icons.TASK_ALT,
            size=48,
            color=get_text_secondary_color(),
        )

        message = ft.Text(
            "タスクを選択してください",
            size=16,
            color=get_text_secondary_color(),
        )

        return ft.Container(
            content=ft.Column(
                controls=[icon, message],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=48,
        )
