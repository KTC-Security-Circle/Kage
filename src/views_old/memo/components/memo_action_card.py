"""メモアクション用のカードコンポーネントモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


class MemoActionCard(ft.Container):
    """メモアクション用のカードコンポーネント.

    メモ画面で使用する再利用可能なアクションカード。
    """

    def __init__(
        self,
        title: str,
        icon: str,
        description: str,
        on_click_handler: Callable | None = None,
    ) -> None:
        """MemoActionCardの初期化.

        Args:
            title: カードのタイトル
            icon: 表示するアイコン
            description: カードの説明文
            on_click_handler: クリック時のハンドラー関数
        """
        super().__init__()
        self.title = title
        self.icon = icon
        self.description = description
        self.on_click = on_click_handler

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=self.icon,
                            size=40,
                        ),
                        ft.Text(
                            self.title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            self.description,
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=20,
                width=150,
                height=120,
            ),
            elevation=2,
        )
