"""GTDサイドバーコンポーネント

GTD（Getting Things Done）のワークフローに基づいたナビゲーションサイドバーを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.task.components.gtd_project_list import GTDProjectList
from views.task.components.gtd_quick_actions import GTDQuickActions
from views.task.components.gtd_status_list import GTDStatusList

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.project_service import ProjectService
    from logic.services.task_service import TaskService
    from models import TaskStatus


class GTDSidebar(ft.Column):
    """GTDサイドバーコンポーネント

    タスク管理のためのGTDベースナビゲーションを提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        task_service: TaskService,
        project_service: ProjectService,
        on_section_change: Callable[[str, dict | None], None],
    ) -> None:
        """GTDSidebarのコンストラクタ

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
        self.spacing = 10
        self.expand = True

        # 現在選択されているセクション
        self.selected_section = None

        # コンポーネントの構築
        self._build_sidebar()

    def _build_sidebar(self) -> None:
        """サイドバーのレイアウトを構築"""
        # 新しいコンポーネントベースのサイドバー
        self.quick_actions = GTDQuickActions(on_action_click=self._handle_quick_action)

        self.project_list = GTDProjectList(
            project_service=self.project_service,
            on_project_click=self._handle_project_select,
            on_add_project_click=self._add_new_project,
        )

        self.status_list = GTDStatusList(
            task_service=self.task_service,
            on_status_click=self._handle_status_select,
        )

        self.controls = [
            self.quick_actions,
            ft.Container(height=8),  # スペーサー
            self.project_list,
            ft.Container(height=8),  # スペーサー
            self.status_list,
        ]

    def _handle_quick_action(self, action: str) -> None:
        """クイックアクション処理"""
        logger.info(f"クイックアクション実行: {action}")
        self.on_section_change("quick_action", {"action": action})

    def _handle_project_select(self, project_id: str) -> None:
        """プロジェクト選択処理"""
        logger.info(f"プロジェクト選択: ID {project_id}")
        self.selected_section = f"project_{project_id}"
        self.on_section_change("project", {"project_id": project_id})

    def _handle_status_select(self, status: TaskStatus) -> None:
        """ステータス選択処理"""
        logger.info(f"ステータス選択: {status.value}")
        self.selected_section = f"status_{status.value}"
        self.on_section_change("status", {"status": status})

    def _add_new_project(self) -> None:
        """新規プロジェクト追加"""
        # [AI GENERATED] プロジェクト作成ダイアログの実装は後の段階で行う
        logger.warning("新規プロジェクト追加機能は未実装です")

    def refresh(self) -> None:
        """サイドバーの内容を再読み込み"""
        # 新しいコンポーネントのリフレッシュ
        if hasattr(self, "project_list"):
            self.project_list.refresh()
        if hasattr(self, "status_list"):
            self.status_list.refresh()
        self.update()
