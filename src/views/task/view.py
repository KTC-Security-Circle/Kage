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
from views.task.components.projects_placeholder import ProjectsPlaceholder
from views.task.components.quick_actions import QuickActions
from views.task.components.task_dialog import TaskDialog
from views.task.components.tasks_board import TasksBoard

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService
    from models import TaskRead


class TaskView(ft.Container):
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
        super().__init__()
        self._page = page
        logger.info("TaskView 初期化開始")

        # ✅ Application Serviceを取得（Session管理不要）
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

        # ビューの構築
        self._build_view()
        logger.info("TaskView 初期化完了")

    def _build_view(self) -> None:
        """ビューを構築

        新しい3セクション縦レイアウト:
        1. QUICK-ACTION: 水平配置のクイックアクションボタン
        2. PROJECTS: プロジェクト管理エリア（将来実装予定）
        3. TASKS: 2カラムタスクボード（CLOSED vs INBOX）
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
        self.expand = True
        self.bgcolor = ft.Colors.GREY_50  # 背景色を設定

        logger.info("TaskView ビュー構築完了")

    def _handle_quick_action(self, action: QuickActionCommand) -> None:
        """クイックアクション処理

        Args:
            action: 実行するアクション
        """
        logger.info(f"クイックアクション実行: {action}")

        # アクションに応じて適切なステータスでタスク作成ダイアログを表示
        if action in (QuickActionCommand.DO_NOW, QuickActionCommand.DO_NEXT):
            self.task_dialog.show_create_dialog(TaskStatus.NEXT_ACTION)
        elif action == QuickActionCommand.DO_SOMEDAY:
            self.task_dialog.show_create_dialog(TaskStatus.SOMEDAY_MAYBE)
        elif action == QuickActionCommand.REFERENCE:
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
                # ✅ GOOD: Application Serviceを使用（Session管理不要）
                command = DeleteTaskCommand(task_id=task.id)
                self._task_app_service.delete_task(command)

                logger.info(f"タスクを削除しました: {task.title}")
                # タスクボードの更新
                self.tasks_board.refresh()
                # 成功メッセージ
                self._show_success("タスクを削除しました")
            except Exception as e:
                logger.error(f"タスク削除エラー: {e}")
                self._show_error(f"タスクの削除に失敗しました: {e}")
            finally:
                # ダイアログを閉じる
                self._page.close(confirm_dialog)

        def delete_cancelled(_: ft.ControlEvent) -> None:
            self._page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("タスク削除の確認"),
            content=ft.Text(f"「{task.title}」を削除しますか？\nこの操作は元に戻せません。"),
            actions=[
                ft.TextButton(
                    text="キャンセル",
                    on_click=delete_cancelled,
                ),
                ft.ElevatedButton(
                    text="削除",
                    icon=ft.Icons.DELETE,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_500,
                    on_click=delete_confirmed,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._page.open(confirm_dialog)

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_400,
        )
        self._page.open(snack_bar)

    def _show_success(self, message: str) -> None:
        """成功メッセージを表示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_400,
        )
        self._page.open(snack_bar)

    def refresh_all(self) -> None:
        """全体を再読み込み"""
        logger.info("TaskView リフレッシュ")
        self.tasks_board.refresh()
        if self._page:
            self.update()


def create_task_view(page: ft.Page) -> ft.Container:
    """タスクビューを作成

    Args:
        page: Fletのページオブジェクト

    Returns:
        TaskView: 作成されたタスクビューインスタンス
    """
    task_view = TaskView(page=page)
    return ft.Container(content=task_view, expand=True, bgcolor=ft.Colors.GREY_50)
