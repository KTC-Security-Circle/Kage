"""サイドバーコンポーネント

タスク管理のワークフローに基づいたナビゲーションサイドバーを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.task.components.project_list import ProjectList
from views.task.components.quick_actions import QuickActionCommand, QuickActions
from views.task.components.status_list import StatusList

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.project_service import ProjectService
    from logic.services.task_service import TaskService
    from models import TaskStatus


class Sidebar(ft.Column):
    """サイドバーコンポーネント

    タスク管理のためのナビゲーションを提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        task_service: TaskService,
        project_service: ProjectService,
        on_section_change: Callable[[str, dict | None], None],
    ) -> None:
        """Sidebarのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            task_service: タスクサービス
            project_service: プロジェクトサービス
            on_section_change: セクション変更時のコールバック
        """
        super().__init__()
        self._page = page
        self.task_service = task_service
        self.project_service = project_service
        self.on_section_change = on_section_change

        # サイドバーの幅設定
        self.width = 280
        self.spacing = 16

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築"""
        logger.info("Sidebar コンポーネント構築開始")

        # クイックアクション
        self.quick_actions = QuickActions(on_action_click=self._handle_quick_action)

        # プロジェクトリスト
        self.project_list = ProjectList(
            project_service=self.project_service,
            on_project_select=self._handle_project_select,
        )

        # ステータスリスト
        self.status_list = StatusList(
            task_service=self.task_service,
            on_status_select=self._handle_status_select,
        )

        # サイドバーコンテンツ
        self.controls = [
            self.quick_actions,
            self.project_list,
            self.status_list,
        ]

        logger.info("Sidebar コンポーネント構築完了")

    def _handle_quick_action(self, action: QuickActionCommand) -> None:
        """クイックアクション処理

        Args:
            action: 実行するアクション
        """
        logger.info(f"サイドバーからクイックアクション実行: {action}")
        self.on_section_change("quick_action", {"action": action.value})

    def _handle_project_select(self, project_id: int | None) -> None:
        """プロジェクト選択処理

        Args:
            project_id: 選択されたプロジェクトID
        """
        logger.info(f"プロジェクト選択: {project_id}")
        self.on_section_change("project", {"project_id": project_id})

    def _handle_status_select(self, status: TaskStatus | None) -> None:
        """ステータス選択処理

        Args:
            status: 選択されたステータス
        """
        logger.info(f"ステータス選択: {status}")
        self.on_section_change("status", {"status": status})

    def refresh_all(self) -> None:
        """全コンポーネントをリフレッシュ"""
        logger.info("Sidebar 全コンポーネントリフレッシュ")
        self.project_list.refresh()
        self.status_list.refresh()
        self.update()
