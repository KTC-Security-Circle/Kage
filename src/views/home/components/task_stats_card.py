"""タスク統計情報カードコンポーネント."""

from __future__ import annotations

import flet as ft


class TaskStatsCard(ft.Container):
    """タスク統計情報カードコンポーネント.

    今日のタスク件数などの統計情報を表示するカード。
    """

    def __init__(self, task_count: int = 0) -> None:
        """TaskStatsCardの初期化.

        Args:
            task_count: タスク件数
        """
        super().__init__()
        self.task_count = task_count
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
                            "今日のタスク",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{self.task_count}件",
                            size=24,
                            # color=ft.Colors.BLUE_600,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            elevation=2,
        )

    def update_task_count(self, count: int) -> None:
        """タスク件数を更新.

        Args:
            count: 新しいタスク件数
        """
        self.task_count = count
        self._build_card()
        self.update()
