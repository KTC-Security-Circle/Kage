"""メモ統計情報カードコンポーネントモジュール."""

from __future__ import annotations

import flet as ft


class MemoStatsCard(ft.Container):
    """メモ統計情報カードコンポーネント.

    総メモ件数などの統計情報を表示するカード。
    """

    def __init__(self, memo_count: int = 0) -> None:
        """MemoStatsCardの初期化.

        Args:
            memo_count: メモ件数
        """
        super().__init__()
        self.memo_count = memo_count
        self.width = 200

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "総メモ数",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{self.memo_count}件",
                            size=24,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            elevation=2,
        )

    def update_memo_count(self, count: int) -> None:
        """メモ件数を更新.

        Args:
            count: 新しいメモ件数
        """
        self.memo_count = count
        self._build_card()
        self.update()
