"""タスクが0件の時の空状態表示コンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import get_text_secondary_color

if TYPE_CHECKING:
    from collections.abc import Callable


class TaskEmptyState(ft.Container):
    """タスクが0件の時の空状態を表示するコンポーネント。"""

    def __init__(
        self,
        *,
        on_create: Callable[[], None] | None = None,
    ) -> None:
        """空状態コンポーネントを初期化。

        Args:
            on_create: 「新規作成」ボタンクリック時のコールバック
        """
        self.on_create = on_create

        super().__init__(
            content=self._build_content(),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _build_content(self) -> ft.Control:
        """空状態のコンテンツを構築する。"""
        icon = ft.Icon(
            name=ft.Icons.TASK_ALT,
            size=64,
            color=get_text_secondary_color(),
        )

        message = ft.Text(
            "タスクがありません",
            size=16,
            color=get_text_secondary_color(),
        )

        controls = [icon, message]

        if self.on_create:
            create_button = ft.ElevatedButton(
                text="新規タスク作成",
                icon=ft.Icons.ADD,
                on_click=lambda _: self.on_create() if self.on_create else None,
            )
            controls.append(create_button)

        return ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        )
