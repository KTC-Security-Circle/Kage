"""タスク管理ビュー

このモジュールは、タスク管理機能のメインビューを提供します。
TaskCreateForm、TaskList等のコンポーネントを統合してタスク管理UIを構築します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from logic.old_task import TaskRepository, TaskService
from views.task.components import TaskCreateForm, TaskList

if TYPE_CHECKING:
    from models.task import OldTaskRead as TaskRead


class TaskView(ft.Column):
    """タスク管理のメインビュー

    タスクの作成、一覧表示、編集、削除機能を統合したメインUIを提供します。
    """

    def __init__(self, page: ft.Page) -> None:
        """TaskViewのコンストラクタ"""
        super().__init__()
        self._page = page
        self.spacing = 20
        self.expand = True

        self.task_repository = TaskRepository()
        self.task_service = TaskService(repository=self.task_repository)

        # コンポーネントの初期化
        self._initialize_components()

        # レイアウトの構築
        self._build_layout()

    def _initialize_components(self) -> None:
        """各コンポーネントを初期化"""
        # タスク一覧コンポーネント
        self.task_list = TaskList(page=self._page, service=self.task_service)

        # タスク作成フォームコンポーネント
        self.task_create_form = TaskCreateForm(
            page=self._page, service=self.task_service, on_task_created=self._on_task_created
        )

    def _build_layout(self) -> None:
        """レイアウトを構築"""
        # メインコンテンツエリア
        main_content = ft.Row(
            [
                # 左側: タスク一覧
                ft.Container(
                    content=self.task_list,
                    expand=2,
                    padding=10,
                ),
                # 右側: タスク作成フォーム
                ft.Container(
                    content=self.task_create_form,
                    expand=1,
                    padding=10,
                    bgcolor=ft.colors.GREY_50,
                    border_radius=10,
                ),
            ],
            expand=True,
        )

        # ページタイトル
        page_title = ft.Container(
            content=ft.Text(
                "タスク管理",
                style=ft.TextThemeStyle.HEADLINE_LARGE,
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.only(left=10, top=10, bottom=10),
        )

        # 全体レイアウト
        self.controls = [
            page_title,
            ft.Divider(),
            main_content,
        ]

    def _on_task_created(self, new_task: TaskRead) -> None:
        """タスク作成時のコールバック処理

        Args:
            new_task: 作成されたタスクオブジェクト
        """
        # タスク一覧に新しいタスクを追加
        self.task_list.add_task(new_task)

    def refresh_tasks(self) -> None:
        """タスク一覧を再読み込み"""
        self.task_list.load_tasks()


def create_task_view(page: ft.Page) -> ft.Container:
    """タスクビューを作成

    Returns:
        TaskView: 作成されたタスクビューインスタンス
    """
    return ft.Container(content=TaskView(page=page))
