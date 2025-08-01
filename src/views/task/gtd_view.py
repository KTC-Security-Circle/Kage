"""GTDベースタスク管理のメインビュー

このモジュールは、GTD（Getting Things Done）の原則に基づいたタスク管理UIを提供します。
新しい3セクション縦レイアウトを実装し、TaskモデルとProjectモデルを使用したモダンなインターフェースを構築します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.services.project_service import ProjectService
from logic.services.task_service import TaskService
from views.task.components.gtd_projects_placeholder import GTDProjectsPlaceholder
from views.task.components.gtd_quick_actions import GTDQuickActions
from views.task.components.gtd_tasks_board import GTDTasksBoard

if TYPE_CHECKING:
    from models.new_task import TaskRead, TaskStatus


class GTDTaskView(ft.Container):
    """GTDタスク管理のメインビュークラス

    新しい3セクション縦レイアウトを実装:
    1. QUICK-ACTION セクション: 水平配置のクイックアクションボタン
    2. PROJECTS セクション: プロジェクト管理エリア（将来実装予定）
    3. TASKS セクション: 2カラムタスクボード（CLOSED vs INBOX）
    """

    def __init__(self, page: ft.Page) -> None:
        """GTDTaskViewのコンストラクタ

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__()
        self._page = page
        logger.info("GTDTaskView 初期化開始")

        # サービス初期化
        self.task_service = TaskService()
        self.project_service = ProjectService()

        # 現在選択中のタスク
        self.selected_task: TaskRead | None = None

        # ビューの構築
        self._build_view()
        logger.info("GTDTaskView 初期化完了")

    def _build_view(self) -> None:
        """ビューを構築

        新しい3セクション縦レイアウト:
        1. QUICK-ACTION: 水平配置のクイックアクションボタン
        2. PROJECTS: プロジェクト管理エリア（将来実装予定）
        3. TASKS: 2カラムタスクボード（CLOSED vs INBOX）
        """
        logger.info("GTDTaskView ビュー構築開始")

        # コンポーネント初期化
        self.quick_actions = GTDQuickActions(
            on_action_click=self._handle_quick_action,
        )

        self.projects_placeholder = GTDProjectsPlaceholder()

        self.tasks_board = GTDTasksBoard(
            task_service=self.task_service,
            on_task_click=self._on_task_click,
            on_task_status_change=self._on_task_status_change,
        )

        # メインレイアウト（縦3セクション構成）
        self.content = ft.Column(
            [
                # セクション1: QUICK-ACTION（水平配置）
                self.quick_actions,
                # セクション2: PROJECTS（将来実装予定）
                self.projects_placeholder,
                # セクション3: TASKS（2カラムボード）
                self.tasks_board,
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,  # スクロール機能を有効化
            expand=True,  # 利用可能な縦スペースを最大限活用
        )

        # コンテナのスタイル設定
        self.padding = 20
        self.bgcolor = ft.Colors.GREY_50  # 背景色を設定

        logger.info("GTDTaskView ビュー構築完了")

    def _handle_quick_action(self, action: str) -> None:
        """クイックアクション処理

        Args:
            action: 実行するアクション
        """
        logger.info(f"クイックアクション実行: {action}")
        # 将来: タスク作成ダイアログまたはフォームを表示

    def _on_task_created(self, task: TaskRead) -> None:
        """タスク作成時のコールバック

        Args:
            task: 作成されたタスク
        """
        logger.info(f"新しいタスクが作成されました: {task.title}")
        # タスクボードの更新
        self.tasks_board.refresh()

    def _on_task_click(self, task: TaskRead) -> None:
        """タスククリック時のコールバック

        Args:
            task: クリックされたタスク
        """
        logger.info(f"タスクがクリックされました: {task.title}")
        self.selected_task = task
        # 将来: タスク詳細ダイアログまたは編集画面を表示

    def _on_task_status_change(self, task: TaskRead, new_status: TaskStatus) -> None:
        """タスクステータス変更時のコールバック

        Args:
            task: 対象タスク
            new_status: 新しいステータス
        """
        logger.info(f"タスクステータスが変更されました: {task.title} -> {new_status.value}")
        # タスクボードの更新
        self.tasks_board.refresh()

    def refresh_all(self) -> None:
        """全体を再読み込み"""
        logger.info("GTDTaskView リフレッシュ")
        self.tasks_board.refresh()
        if self._page:
            self.update()


def create_gtd_task_view(page: ft.Page) -> ft.Container:
    """GTDタスクビューを作成

    Args:
        page: Fletのページオブジェクト

    Returns:
        GTDTaskView: 作成されたGTDタスクビューインスタンス
    """
    return ft.Container(content=GTDTaskView(page=page))
