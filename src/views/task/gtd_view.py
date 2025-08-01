"""GTDベースタスク管理のメインビュー

このモジュールは、GTD（Getting Things Done）の原則に基づいたタスク管理UIを提供します。
新しいTaskモデルとProjectモデルを使用して、モダンで直感的なタスク管理インターフェースを構築します。
"""

from __future__ import annotations

import flet as ft

from logic.services.project_service import ProjectService
from logic.services.task_service import TaskService
from models.new_task import TaskStatus
from views.task.components.gtd_sidebar import GTDSidebar
from views.task.components.task_content_area import TaskContentArea


class GTDTaskView(ft.Row):
    """GTDベースのタスク管理メインビュー

    左サイドバーとメインコンテンツエリアからなるレイアウトでGTDワークフローを実現します。
    """

    def __init__(self, page: ft.Page) -> None:
        """GTDTaskViewのコンストラクタ

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__()
        self._page = page
        self.expand = True
        self.spacing = 0

        # サービス層の初期化
        self.task_service = TaskService()
        self.project_service = ProjectService()

        # コンポーネントの初期化
        self._initialize_components()

        # レイアウトの構築
        self._build_layout()

    def _initialize_components(self) -> None:
        """各コンポーネントを初期化"""
        # 左サイドバー
        self.sidebar = GTDSidebar(
            page=self._page,
            task_service=self.task_service,
            project_service=self.project_service,
            on_section_change=self._on_section_change,
        )

        # メインコンテンツエリア
        self.content_area = TaskContentArea(
            page=self._page,
            task_service=self.task_service,
            project_service=self.project_service,
        )

    def _build_layout(self) -> None:
        """レイアウトを構築"""
        self.controls = [
            # 左サイドバー
            ft.Container(
                content=self.sidebar,
                width=300,
                bgcolor=ft.Colors.GREY_100,
                padding=10,
            ),
            # メインコンテンツエリア
            ft.Container(
                content=self.content_area,
                expand=True,
                padding=20,
            ),
        ]

    def _on_section_change(self, section_type: str, section_data: dict | None = None) -> None:
        """サイドバーのセクション変更時のコールバック

        Args:
            section_type: セクションの種類（'status', 'project', 'quick_action'）
            section_data: セクションに関連するデータ
        """
        if section_type == "status":
            # ステータス別タスク表示
            status = section_data.get("status") if section_data else None
            if status:
                self.content_area.show_tasks_by_status(status)

        elif section_type == "project":
            # プロジェクト別タスク表示
            project_id = section_data.get("project_id") if section_data else None
            if project_id:
                self.content_area.show_tasks_by_project(project_id)

        elif section_type == "quick_action":
            # クイックアクション処理
            action = section_data.get("action") if section_data else None
            self._handle_quick_action(action)

    def _handle_quick_action(self, action: str | None) -> None:
        """クイックアクション処理

        Args:
            action: 実行するアクション
        """
        if action == "add_to_inbox":
            self.content_area.show_quick_add_form(TaskStatus.INBOX)
        elif action == "add_today_task":
            self.content_area.show_quick_add_form(TaskStatus.NEXT_ACTION)
        elif action == "add_waiting_task":
            self.content_area.show_quick_add_form(TaskStatus.WAITING_FOR)
        # 他のクイックアクションもここに追加

    def refresh_all(self) -> None:
        """全体を再読み込み"""
        self.sidebar.refresh()
        self.content_area.refresh()


def create_gtd_task_view(page: ft.Page) -> ft.Container:
    """GTDタスクビューを作成

    Args:
        page: Fletのページオブジェクト

    Returns:
        GTDTaskView: 作成されたGTDタスクビューインスタンス
    """
    return ft.Container(content=GTDTaskView(page=page))
