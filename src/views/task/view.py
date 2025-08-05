"""タスク管理のメインビュー

このモジュールは、タスク管理UIを提供します。
新しい3セクション縦レイアウトを実装し、TaskモデルとProjectモデルを使用したモダンなインターフェースを構築します。
Application Serviceパターンを使用してSession管理を分離。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.commands.task_commands import DeleteTaskCommand
from logic.factory import get_application_service_container
from models import QuickActionCommand, TaskStatus
from views.shared import BaseView, ErrorHandlingMixin
from views.task.components.projects_placeholder import ProjectsPlaceholder
from views.task.components.quick_actions import QuickActions
from views.task.components.task_dialog import TaskDialog
from views.task.components.tasks_board import TasksBoard

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService
    from models import TaskRead


class TaskView(BaseView, ErrorHandlingMixin):
    """タスク管理のメインビュークラス

    新しい3セクション縦レイアウトを実装:
    1. QUICK-ACTION セクション: 水平配置のクイックアクションボタン
    2. PROJECTS セクション: プロジェクト管理エリア（将来実装予定）
    3. TASKS セクション: 2カラムタスクボード（CLOSED vs INBOX）
    """

    def __init__(self, page: ft.Page) -> None:
        """TaskViewのコンストラクタ

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__(page)
        logger.info("TaskView 初期化開始")

        container = get_application_service_container()
        self._task_app_service: TaskApplicationService = container.get_task_application_service()

        # ダイアログ初期化（サービスは後で注入）
        self.task_dialog = TaskDialog(
            page=page,
            on_task_created=self._on_task_created,
            on_task_updated=self._on_task_updated,
        )

        # 現在選択中のタスク
        self.selected_task: TaskRead | None = None

        logger.info("TaskView 初期化完了")

    def build_content(self) -> ft.Control:
        """ビューコンテンツを構築

        新しい3セクション縦レイアウト:
        1. QUICK-ACTION: 水平配置のクイックアクションボタン
        2. PROJECTS: プロジェクト管理エリア（将来実装予定）
        3. TASKS: 2カラムタスクボード（CLOSED vs INBOX）

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        logger.info("TaskView ビュー構築開始")

        # コンポーネント初期化
        self.quick_actions = QuickActions(
            on_action_click=self._handle_quick_action,
        )

        self.projects_placeholder = ProjectsPlaceholder()

        self.tasks_board = TasksBoard(
            on_task_click=self._on_task_click,
            on_task_status_change=self._on_task_status_change,
            on_task_delete=self._on_task_delete,
        )

        # メインレイアウト（縦3セクション構成）
        content = ft.Column(
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

        logger.info("TaskView ビュー構築完了")
        return content

    def _handle_quick_action(self, action: QuickActionCommand) -> None:
        """クイックアクション処理

        Args:
            action: 実行するアクション
        """
        logger.info(f"クイックアクション実行: {action}")

        # [AI GENERATED] ビジネスロジックをApplication Serviceに委譲
        try:
            # Application Serviceからアクションに対応するステータスを取得
            task_status = self._task_app_service.get_task_status_for_quick_action(action)

            # 取得したステータスでタスク作成ダイアログを表示
            self.task_dialog.show_create_dialog(task_status)

            logger.info(f"クイックアクションマッピング成功: {action} -> {task_status}")

        except Exception as e:
            logger.error(f"クイックアクション処理エラー: {e}")
            self.show_error(f"アクションの処理に失敗しました: {e}")
            # [AI GENERATED] エラー時はデフォルトでINBOXステータスを使用
            self.task_dialog.show_create_dialog(TaskStatus.INBOX)

    def _on_task_created(self, task: TaskRead) -> None:
        """タスク作成時のコールバック

        Args:
            task: 作成されたタスク
        """
        logger.info(f"新しいタスクが作成されました: {task.title}")
        # タスクボードの更新
        self.tasks_board.refresh()

    def _on_task_updated(self, task: TaskRead) -> None:
        """タスク更新時のコールバック

        Args:
            task: 更新されたタスク
        """
        logger.info(f"タスクが更新されました: {task.title}")
        # タスクボードの更新
        self.tasks_board.refresh()

    def _on_task_click(self, task: TaskRead) -> None:
        """タスククリック時のコールバック

        Args:
            task: クリックされたタスク
        """
        logger.info(f"タスクがクリックされました: {task.title}")
        self.selected_task = task
        # タスク編集ダイアログを表示
        self.task_dialog.show_edit_dialog(task)

    def _on_task_status_change(self, task: TaskRead, new_status: TaskStatus) -> None:
        """タスクステータス変更時のコールバック

        Args:
            task: 対象タスク
            new_status: 新しいステータス
        """
        logger.info(f"タスクステータスが変更されました: {task.title} -> {new_status.value}")
        # タスクボードの更新
        self.tasks_board.refresh()

    def _on_task_delete(self, task: TaskRead) -> None:
        """タスク削除時のコールバック

        Args:
            task: 削除対象タスク
        """
        logger.info(f"タスク削除要求: {task.title}")

        # 削除確認ダイアログを表示
        def delete_confirmed(_: ft.ControlEvent) -> None:
            try:
                command = DeleteTaskCommand(task_id=task.id)
                self._task_app_service.delete_task(command)

                logger.info(f"タスクを削除しました: {task.title}")
                # タスクボードの更新
                self.tasks_board.refresh()
                # 成功メッセージ
                self.show_success("タスクを削除しました")
            except Exception as e:
                logger.error(f"タスク削除エラー: {e}")
                self.show_error(f"タスクの削除に失敗しました: {e}")

        self.show_confirm_dialog(
            title="タスク削除の確認",
            content=f"「{task.title}」を削除しますか？\nこの操作は元に戻せません。",
            on_confirm=delete_confirmed,
            confirm_text="削除",
            cancel_text="キャンセル",
        )

    def refresh_all(self) -> None:
        """全体を再読み込み"""
        logger.info("TaskView リフレッシュ")
        self.tasks_board.refresh()
        self.refresh()


def create_task_view(page: ft.Page) -> ft.Container:
    """タスクビューを作成

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Container: 作成されたタスクビューインスタンス
    """
    task_view = TaskView(page=page)
    task_view.mount()  # コンテンツを構築
    return task_view
