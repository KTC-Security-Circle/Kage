"""タスク管理のUIコンポーネント

このモジュールは、タスクのCRUD操作を行うためのUIコンポーネントを提供します。
FletライブラリとTaskServiceを使用してタスク管理機能を実装しています。
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import flet as ft

from logic.task import TaskService, TaskUIHelper
from models.task import OldTaskUpdate as TaskUpdate

if TYPE_CHECKING:
    from collections.abc import Callable

    from models.task import OldTaskRead as TaskRead

    # 型定義
    type OnTaskCreated = Callable[[TaskRead], None] | None
    type OnTaskUpdated = Callable[[TaskRead], None] | None
    type OnTaskDeleted = Callable[[TaskRead], None] | None


class TaskCreateForm(ft.Column):
    """タスク作成フォームコンポーネント

    新しいタスクを作成するためのフォームUIを提供します。
    """

    def __init__(self, page: ft.Page, service: TaskService, on_task_created: OnTaskCreated = None) -> None:
        """TaskCreateFormのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            service: タスクサービスインスタンス
            on_task_created: タスク作成時のコールバック関数
        """
        super().__init__()
        self._page = page
        self.on_task_created = on_task_created
        self.service = service
        self.ui_helper = TaskUIHelper()

        # フォーム要素の初期化
        self.title_field = ft.TextField(
            label="タスクタイトル",
            hint_text="タスクのタイトルを入力してください",
            max_length=100,
            width=400,
        )

        self.description_field = ft.TextField(
            label="説明（任意）",
            hint_text="タスクの詳細説明を入力してください",
            multiline=True,
            max_lines=3,
            max_length=500,
            width=400,
        )

        self.error_text = ft.Text(color=ft.colors.RED, visible=False)

        self.create_button = ft.ElevatedButton(
            text="タスクを作成",
            icon=ft.icons.ADD,
            on_click=self._on_create_clicked,
        )

        self.clear_button = ft.TextButton(
            text="クリア",
            on_click=self._on_clear_clicked,
        )

        # レイアウト構築
        self.controls = [
            ft.Text("新しいタスクを作成", style=ft.TextThemeStyle.HEADLINE_SMALL),
            self.title_field,
            self.description_field,
            self.error_text,
            ft.Row(
                [
                    self.create_button,
                    self.clear_button,
                ]
            ),
        ]

    def _on_create_clicked(self, _: ft.ControlEvent) -> None:
        """タスク作成ボタンクリック時の処理"""
        try:
            # 入力値の取得
            title = self.title_field.value or ""
            description = self.description_field.value or ""

            # バリデーション
            is_valid, error_message = self.ui_helper.validate_task_input(title, description)
            if not is_valid:
                self._show_error(error_message)
                return

            # タスク作成
            task = self.service.create_new_task(title, description)

            # 成功時の処理
            self._clear_form()
            self._hide_error()

            # コールバック実行
            if self.on_task_created:
                self.on_task_created(task)

            # 成功メッセージ表示
            self._page.open(ft.SnackBar(content=ft.Text("タスクを作成しました")))

        except Exception as ex:
            self._show_error(f"タスクの作成に失敗しました: {ex!s}")

    def _on_clear_clicked(self, _: ft.ControlEvent) -> None:
        """クリアボタンクリック時の処理"""
        self._clear_form()
        self._hide_error()

    def _clear_form(self) -> None:
        """フォームをクリア"""
        self.title_field.value = ""
        self.description_field.value = ""
        self.update()

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示"""
        self.error_text.value = message
        self.error_text.visible = True
        self.update()

    def _hide_error(self) -> None:
        """エラーメッセージを非表示"""
        self.error_text.visible = False
        self.update()


class TaskItem(ft.Card):
    """個別タスクアイテムコンポーネント

    単一のタスクを表示・操作するためのカードUIを提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        service: TaskService,
        task: TaskRead,
        on_task_updated: OnTaskUpdated = None,
        on_task_deleted: OnTaskDeleted = None,
    ) -> None:
        """TaskItemのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            service: タスクサービスインスタンス
            task: 表示するタスクオブジェクト
            on_task_updated: タスク更新時のコールバック関数
            on_task_deleted: タスク削除時のコールバック関数
        """
        super().__init__()
        self._page = page
        self.task = task
        self.on_task_updated = on_task_updated
        self.on_task_deleted = on_task_deleted
        self.service = service
        self.ui_helper = TaskUIHelper()

        # 編集モードのフラグ
        self.is_editing = False

        # UI要素の構築
        self._build_ui()

    def _build_ui(self) -> None:
        """UIを構築"""
        # 完了状態トグルボタン
        self.complete_checkbox = ft.Checkbox(
            value=self.task.completed,
            on_change=self._on_complete_toggled,
        )

        # タスクタイトル表示/編集
        self.title_display = ft.Text(
            value=self.ui_helper.format_task_title(self.task),
            style=ft.TextThemeStyle.TITLE_MEDIUM,
            color=self.ui_helper.get_task_status_color(self.task),
        )

        self.title_edit = ft.TextField(
            value=self.task.title,
            visible=False,
            width=300,
        )

        # 説明表示/編集
        description_text = self.ui_helper.truncate_description(self.task.description)
        self.description_display = ft.Text(
            value=description_text,
            color=ft.colors.GREY_700,
        )

        self.description_edit = ft.TextField(
            value=self.task.description,
            multiline=True,
            max_lines=3,
            visible=False,
            width=300,
        )

        # 日付表示
        self.date_text = ft.Text(
            value=self.ui_helper.format_task_date(self.task),
            size=12,
            color=ft.colors.GREY_600,
        )

        # 操作ボタン
        self.edit_button = ft.IconButton(
            icon=ft.icons.EDIT,
            tooltip="編集",
            on_click=self._on_edit_clicked,
        )

        self.save_button = ft.IconButton(
            icon=ft.icons.SAVE,
            tooltip="保存",
            visible=False,
            on_click=self._on_save_clicked,
        )

        self.cancel_button = ft.IconButton(
            icon=ft.icons.CANCEL,
            tooltip="キャンセル",
            visible=False,
            on_click=self._on_cancel_clicked,
        )

        self.delete_button = ft.IconButton(
            icon=ft.icons.DELETE,
            tooltip="削除",
            icon_color=ft.colors.RED,
            on_click=self._on_delete_clicked,
        )

        # レイアウト構築
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.complete_checkbox,
                            ft.Column(
                                [
                                    ft.Stack(
                                        [
                                            self.title_display,
                                            self.title_edit,
                                        ]
                                    ),
                                    ft.Stack(
                                        [
                                            self.description_display,
                                            self.description_edit,
                                        ]
                                    ),
                                    self.date_text,
                                ],
                                expand=True,
                            ),
                            ft.Row(
                                [
                                    self.edit_button,
                                    self.save_button,
                                    self.cancel_button,
                                    self.delete_button,
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            padding=10,
        )

    def _on_complete_toggled(self, _: ft.ControlEvent) -> None:
        """完了状態トグル時の処理"""
        try:
            updated_task = self.service.toggle_task_status(self.task.id)
            if updated_task:
                self.task = updated_task
                self._update_display()

                if self.on_task_updated:
                    self.on_task_updated(self.task)

        except Exception as ex:
            self._page.open(ft.SnackBar(content=ft.Text(f"更新に失敗しました: {ex!s}")))

    def _on_edit_clicked(self, _: ft.ControlEvent) -> None:
        """編集ボタンクリック時の処理"""
        self.is_editing = True
        self._toggle_edit_mode(editing=True)

    def _on_save_clicked(self, _: ft.ControlEvent) -> None:
        """保存ボタンクリック時の処理"""
        try:
            title = self.title_edit.value or ""
            description = self.description_edit.value or ""

            # バリデーション
            is_valid, error_message = self.ui_helper.validate_task_input(title, description)
            if not is_valid:
                self._page.open(ft.SnackBar(content=ft.Text(error_message)))
                return

            # タスク更新
            update_data = TaskUpdate(title=title, description=description)
            updated_task = self.service.update_task(self.task.id, update_data)

            if updated_task:
                self.task = updated_task
                self.is_editing = False
                self._toggle_edit_mode(editing=False)
                self._update_display()

                if self.on_task_updated:
                    self.on_task_updated(self.task)

                self._page.open(ft.SnackBar(content=ft.Text("タスクを更新しました")))

        except Exception as ex:
            self._page.open(ft.SnackBar(content=ft.Text(f"更新に失敗しました: {ex}")))

    def _on_cancel_clicked(self, _: ft.ControlEvent) -> None:
        """キャンセルボタンクリック時の処理"""
        # 編集内容を元に戻す
        self.title_edit.value = self.task.title
        self.description_edit.value = self.task.description

        self.is_editing = False
        self._toggle_edit_mode(editing=False)

    def _on_delete_clicked(self, _: ft.ControlEvent) -> None:
        """削除ボタンクリック時の処理"""

        def confirm_delete(_: ft.ControlEvent) -> None:
            try:
                self.service.remove_task(self.task.id)
                if self.on_task_deleted:
                    self.on_task_deleted(self.task)
                    self._page.open(ft.SnackBar(content=ft.Text("タスクを削除しました")))
                dialog.open = False
                self._page.update()

            except Exception as ex:
                self._page.open(ft.SnackBar(content=ft.Text(f"削除に失敗しました: {ex!s}")))

        def cancel_delete(_: ft.ControlEvent) -> None:
            dialog.open = False
            self._page.update()

        # 削除確認ダイアログ
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("削除の確認"),
            content=ft.Text(f"「{self.task.title}」を削除しますか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=cancel_delete),
                ft.TextButton("削除", on_click=confirm_delete),
            ],
        )

        self._page.open(dialog)
        self._page.update()

    def _toggle_edit_mode(self, *, editing: bool) -> None:
        """編集モードの切り替え"""
        # 表示/編集要素の表示切り替え
        self.title_display.visible = not editing
        self.title_edit.visible = editing
        self.description_display.visible = not editing
        self.description_edit.visible = editing

        # ボタンの表示切り替え
        self.edit_button.visible = not editing
        self.save_button.visible = editing
        self.cancel_button.visible = editing

        self.update()

    def _update_display(self) -> None:
        """表示内容を更新"""
        self.title_display.value = self.ui_helper.format_task_title(self.task)
        self.title_display.color = self.ui_helper.get_task_status_color(self.task)
        self.description_display.value = self.ui_helper.truncate_description(self.task.description)
        self.complete_checkbox.value = self.task.completed
        self.date_text.value = self.ui_helper.format_task_date(self.task)
        self.update()


class TaskFilter(Enum):
    """タスクフィルタの列挙型"""

    ALL = "all"
    COMPLETED = "completed"
    PENDING = "pending"


class TaskList(ft.Column):
    """タスク一覧コンポーネント

    複数のタスクを一覧表示し、フィルタリング機能を提供します。
    """

    def __init__(self, page: ft.Page, service: TaskService) -> None:
        """TaskListのコンストラクタ"""
        super().__init__()
        self.service = service
        self.tasks = []
        self.current_filter: TaskFilter = TaskFilter.ALL
        self._page = page

        # UI要素の初期化
        self._build_ui()
        self.load_tasks()

    def _build_ui(self) -> None:
        """UIを構築"""
        # フィルタボタン
        self.filter_buttons = ft.Row(
            [
                ft.ElevatedButton(
                    text="すべて",
                    on_click=lambda _: self._apply_filter(TaskFilter.ALL),
                ),
                ft.ElevatedButton(
                    text="未完了",
                    on_click=lambda _: self._apply_filter(TaskFilter.PENDING),
                ),
                ft.ElevatedButton(
                    text="完了済み",
                    on_click=lambda _: self._apply_filter(TaskFilter.COMPLETED),
                ),
            ]
        )

        # タスク統計表示
        self.stats_text = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)

        # タスクリスト表示領域
        self.task_container = ft.Column(scroll=ft.ScrollMode.AUTO)

        # レイアウト構築
        self.controls = [
            ft.Text("タスク一覧", style=ft.TextThemeStyle.HEADLINE_SMALL),
            self.filter_buttons,
            self.stats_text,
            ft.Divider(),
            self.task_container,
        ]

    def load_tasks(self) -> None:
        """タスクを読み込み"""
        try:
            self.tasks = self.service.get_task_list()
            self._update_display()
            # self.page.overlay.append(ft.SnackBar(content=ft.Text("タスクを読み込みました")))
            self._page.open(ft.SnackBar(content=ft.Text("タスクを読み込みました")))
        except Exception as ex:
            self._page.open(ft.SnackBar(content=ft.Text(f"タスクの読み込みに失敗しました: {ex}")))
        self._page.update()

    def _apply_filter(self, filter_type: TaskFilter) -> None:
        """フィルタを適用"""
        self.current_filter = filter_type
        self._update_display()

    def _update_display(self) -> None:
        """表示を更新"""
        # フィルタに基づいてタスクを絞り込み
        if self.current_filter == TaskFilter.COMPLETED:
            filtered_tasks = [task for task in self.tasks if task.completed]
        elif self.current_filter == TaskFilter.PENDING:
            filtered_tasks = [task for task in self.tasks if not task.completed]
        else:
            filtered_tasks = self.tasks

        # 統計情報を更新
        stats = self.service.get_task_count()
        self.stats_text.value = f"全{stats['total']}件 (未完了: {stats['pending']}件, 完了: {stats['completed']}件)"

        # タスクアイテムを生成
        self.task_container.controls.clear()

        if not filtered_tasks:
            self.task_container.controls.append(ft.Text("該当するタスクがありません", color=ft.colors.GREY_600))
        else:
            for task in filtered_tasks:
                task_item = TaskItem(
                    page=self._page,
                    service=self.service,
                    task=task,
                    on_task_updated=self._on_task_updated,
                    on_task_deleted=self._on_task_deleted,
                )
                self.task_container.controls.append(task_item)

        self._page.update()

    def _on_task_updated(self, updated_task: TaskRead) -> None:
        """タスク更新時の処理"""
        # タスクのIDが一致するものを更新
        self.tasks = [task if task.id != updated_task.id else updated_task for task in self.tasks]
        self._update_display()

    def _on_task_deleted(self, deleted_task: TaskRead) -> None:
        """タスク削除時の処理"""
        # タスクリストから削除
        self.tasks = [task for task in self.tasks if task.id != deleted_task.id]
        self._update_display()

    def add_task(self, new_task: TaskRead) -> None:
        """新しいタスクを追加"""
        self.tasks.insert(0, new_task)  # 先頭に追加
        self._update_display()
