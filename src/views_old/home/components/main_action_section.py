"""メインアクションセクションコンポーネント."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views_old.home.components.task_stats_card import TaskStatsCard

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService


class MainActionSection(ft.Column):
    """メインアクションセクションコンポーネント.

    タスク管理ボタンと統計情報を表示するセクション。
    """

    def __init__(self, page: ft.Page, task_app_service: TaskApplicationService) -> None:
        """MainActionSectionの初期化.

        Args:
            page: Fletのページオブジェクト
            task_app_service: タスクアプリケーションサービスインスタンス
        """
        super().__init__()
        self._page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.task_app_service = task_app_service

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.ElevatedButton(
                text="タスク管理",
                icon=ft.Icons.TASK_ALT,
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    # bgcolor=ft.Colors.BLUE_600,
                    # color=ft.Colors.WHITE,
                    text_style=ft.TextStyle(size=16),
                ),
                on_click=self._navigate_to_tasks,
            ),
            TaskStatsCard(task_count=self.get_today_task_count()),
        ]

    def _navigate_to_tasks(self, _: ft.ControlEvent) -> None:
        """タスク画面への遷移処理.

        Args:
            _: イベントオブジェクト
        """
        self._page.go("/task")

    def get_today_task_count(self) -> int:
        """今日のタスク件数を取得.

        Returns:
            今日のタスク件数
        """
        from logic.queries.task_queries import GetTodayTasksCountQuery

        query = GetTodayTasksCountQuery()
        return self.task_app_service.get_today_tasks_count(query)
