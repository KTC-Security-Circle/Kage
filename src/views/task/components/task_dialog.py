"""タスク作成・編集ダイアログコンポーネント

タスクの作成や編集を行うダイアログを提供します。
Application Serviceパターンを使用してSession管理を分離。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.commands.task_commands import CreateTaskCommand, UpdateTaskCommand
from logic.factory import get_application_service_container
from models import TaskStatus

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date

    from logic.application.task_application_service import TaskApplicationService
    from models import TaskRead


@dataclass
class TaskAlertDialogParams:
    title: str
    on_cancel: Callable[[ft.ControlEvent], None]
    on_create: Callable[[ft.ControlEvent], None]
    title_field: ft.TextField
    description_field: ft.TextField
    status_dropdown: ft.Dropdown
    due_date_field: ft.TextField


class TaskAlertDialog(ft.AlertDialog):
    """タスクアラートダイアログ

    タスクの作成や編集を行うためのダイアログです。
    """

    def __init__(self, params: TaskAlertDialogParams) -> None:
        """TaskAlertDialogのコンストラクタ

        Args:
            params: ダイアログのパラメータ
        """
        super().__init__()
        self.params = params
        self.modal = True
        self.title = ft.Text(self.params.title)
        self.approve_button = ft.ElevatedButton(
            text="作成",
            icon=ft.Icons.ADD,
            on_click=self.params.on_create,
        )
        self.actions = [
            ft.TextButton(
                text="キャンセル",
                on_click=lambda _: self.params.on_cancel,
            ),
            self.approve_button,
        ]
        self.content = ft.Container(
            content=ft.Column(
                [
                    self.params.title_field,
                    self.params.description_field,
                    self.params.status_dropdown,
                    self.params.due_date_field,
                ],
                spacing=16,
                tight=True,
            ),
            width=400,
            height=350,
        )
        self.actions_alignment = ft.MainAxisAlignment.END


class TaskDialog:
    """タスク作成・編集ダイアログ

    Application Serviceパターンを使用してSession管理を分離
    """

    def __init__(
        self,
        page: ft.Page,
        on_task_created: Callable[[TaskRead], None] | None = None,
        on_task_updated: Callable[[TaskRead], None] | None = None,
    ) -> None:
        """TaskDialogのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            on_task_created: タスク作成時のコールバック
            on_task_updated: タスク更新時のコールバック
        """
        self.page = page
        self.on_task_created = on_task_created
        self.on_task_updated = on_task_updated

        # ✅ Application Serviceを取得（Session管理不要）
        container = get_application_service_container()
        self._task_app_service: TaskApplicationService = container.get_task_application_service()

        # 編集モード（Noneの場合は新規作成）
        self.editing_task: TaskRead | None = None

        # フォームフィールド
        self.title_field = ft.TextField(
            label="タスクタイトル",
            hint_text="やりたいことを簡潔に入力してください",
            border_radius=8,
            autofocus=True,
        )

        self.description_field = ft.TextField(
            label="説明（任意）",
            hint_text="詳細な説明や補足があれば入力してください",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=8,
            value="",
        )

        self.status_dropdown = ft.Dropdown(
            label="ステータス",
            options=[
                ft.dropdown.Option(TaskStatus.INBOX.value, "📥 INBOX（整理用）"),
                ft.dropdown.Option(TaskStatus.NEXT_ACTION.value, "🎯 次に取るべき行動"),
                ft.dropdown.Option(TaskStatus.WAITING_FOR.value, "⏳ 待機中"),
                ft.dropdown.Option(TaskStatus.SOMEDAY_MAYBE.value, "💭 いつかやる"),
                ft.dropdown.Option(TaskStatus.DELEGATED.value, "👥 委譲済み"),
            ],
            value=TaskStatus.INBOX.value,
            border_radius=8,
        )

        self.due_date_field = ft.TextField(
            label="締切日（任意）",
            hint_text="YYYY-MM-DD",
            border_radius=8,
        )

        # ダイアログの作成
        self.dialog = self._create_dialog()

    def _create_dialog(self) -> TaskAlertDialog:
        """ダイアログを作成"""
        # return ft.AlertDialog(
        #     modal=True,
        #     title=ft.Text("新しいタスクを作成"),
        #     content=ft.Container(
        #         content=ft.Column(
        #             [
        #                 self.title_field,
        #                 self.description_field,
        #                 self.status_dropdown,
        #                 self.due_date_field,
        #             ],
        #             spacing=16,
        #             tight=True,
        #         ),
        #         width=400,
        #         height=350,
        #     ),
        #     actions=[
        #         ft.TextButton(
        #             text="キャンセル",
        #             on_click=self._on_cancel,
        #         ),
        #         ft.ElevatedButton(
        #             text="作成",
        #             icon=ft.Icons.ADD,
        #             on_click=self._on_create,
        #         ),
        #     ],
        #     actions_alignment=ft.MainAxisAlignment.END,
        # )
        return TaskAlertDialog(
            TaskAlertDialogParams(
                title="新しいタスクを作成",
                on_cancel=self._on_cancel,
                on_create=self._on_create,
                title_field=self.title_field,
                description_field=self.description_field,
                status_dropdown=self.status_dropdown,
                due_date_field=self.due_date_field,
            )
        )

    def show_create_dialog(self, initial_status: TaskStatus = TaskStatus.INBOX) -> None:
        """新規作成ダイアログを表示

        Args:
            initial_status: 初期ステータス
        """
        logger.info(f"タスク作成ダイアログを表示 (初期ステータス: {initial_status})")

        # フィールドをリセット
        self.editing_task = None
        self.title_field.value = ""
        self.description_field.value = ""
        self.status_dropdown.value = initial_status.value
        self.due_date_field.value = ""

        # ダイアログのタイトルとボタンを更新
        self.dialog.title = ft.Text("新しいタスクを作成")
        # self.dialog.actions[1].text = "作成"
        # self.dialog.actions[1].icon = ft.Icons.ADD
        self.dialog.approve_button.text = "作成"
        self.dialog.approve_button.icon = ft.Icons.ADD

        # ダイアログを表示
        self.page.open(self.dialog)

    def show_edit_dialog(self, task: TaskRead) -> None:
        """編集ダイアログを表示

        Args:
            task: 編集するタスク
        """
        logger.info(f"タスク編集ダイアログを表示 (タスク: {task.title})")

        # 編集モードに設定
        self.editing_task = task

        # フィールドに既存の値を設定
        self.title_field.value = task.title
        self.description_field.value = task.description
        self.status_dropdown.value = task.status.value
        self.due_date_field.value = task.due_date.isoformat() if task.due_date else ""

        # ダイアログのタイトルとボタンを更新
        self.dialog.title = ft.Text("タスクを編集")
        # self.dialog.actions[1].text = "更新"
        # self.dialog.actions[1].icon = ft.Icons.SAVE
        self.dialog.approve_button.text = "更新"
        self.dialog.approve_button.icon = ft.Icons.SAVE

        # ダイアログを表示
        self.page.open(self.dialog)

    def _on_cancel(self, _: ft.ControlEvent) -> None:
        """キャンセルボタンクリック時の処理"""
        logger.info("タスクダイアログをキャンセル")
        self.page.close(self.dialog)

    def _on_create(self, _: ft.ControlEvent) -> None:
        """作成/更新ボタンクリック時の処理"""
        try:
            # [AI GENERATED] 最小限のUIバリデーション（空文字チェックのみ）
            if not self.title_field.value or not self.title_field.value.strip():
                self._show_error("タスクタイトルを入力してください")
                return

            # [AI GENERATED] 日付の基本的なフォーマットチェック
            due_date = None
            if self.due_date_field.value and self.due_date_field.value.strip():
                try:
                    from datetime import datetime

                    due_date = datetime.strptime(self.due_date_field.value, "%Y-%m-%d").date()  # noqa: DTZ007
                except ValueError:
                    self._show_error("締切日は YYYY-MM-DD 形式で入力してください")
                    return

            # [AI GENERATED] 詳細なバリデーションはApplication Service層に委譲
            if self.editing_task is None:
                # 新規作成
                self._create_task(due_date)
            else:
                # 更新
                self._update_task(due_date)

        except Exception as e:
            logger.error(f"タスク作成/更新エラー: {e}")
            self._show_error(f"エラーが発生しました: {e}")

    def _create_task(self, due_date: date | None) -> None:
        """タスクを作成"""
        # [AI GENERATED] バリデーションはApplication Service層に委譲
        # UIレベルでの基本チェックは_on_createで実施済み

        command = CreateTaskCommand(
            title=self.title_field.value.strip() if self.title_field.value else "",
            description=self.description_field.value.strip() if self.description_field.value else "",
            status=TaskStatus(self.status_dropdown.value),
            due_date=due_date,
        )

        created_task = self._task_app_service.create_task(command)

        logger.info(f"タスクを作成しました: {created_task.title}")

        # コールバック実行
        if self.on_task_created:
            self.on_task_created(created_task)

        # ダイアログを閉じる
        self.page.close(self.dialog)

        # 成功メッセージ
        self._show_success("タスクを作成しました")

    def _update_task(self, due_date: date | None) -> None:
        """タスクを更新"""
        if self.editing_task is None:
            return

        if not self.title_field.value:
            self._show_error("タスクタイトルを入力してください")
            return

        command = UpdateTaskCommand(
            task_id=self.editing_task.id,
            title=self.title_field.value.strip(),
            description=self.description_field.value.strip() if self.description_field.value else "",
            status=TaskStatus(self.status_dropdown.value),
            due_date=due_date,
        )

        updated_task = self._task_app_service.update_task(command)

        logger.info(f"タスクを更新しました: {updated_task.title}")

        # コールバック実行
        if self.on_task_updated:
            self.on_task_updated(updated_task)

        # ダイアログを閉じる
        self.page.close(self.dialog)

        # 成功メッセージ
        self._show_success("タスクを更新しました")

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_400,
        )
        self.page.open(snack_bar)

    def _show_success(self, message: str) -> None:
        """成功メッセージを表示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_400,
        )
        self.page.open(snack_bar)
