"""タスクボードコンポーネント

2カラム構成（CLOSED vs INBOX）でタスクボードを提供します。
将来的にドラッグアンドドロップ機能を追加予定。
Application Serviceパターンを使用してSession管理を分離。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.commands.task_commands import UpdateTaskStatusCommand
from logic.factory import get_application_service_container
from models import TaskStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.application.task_application_service import TaskApplicationService
    from models import TaskRead


class TasksBoard(ft.Container):
    """タスクボードコンポーネント

    CLOSED（左）とINBOX（右）の2カラム構成でタスクを表示します。
    """

    def __init__(
        self,
        on_task_click: Callable[[TaskRead], None] | None = None,
        on_task_status_change: Callable[[TaskRead, TaskStatus], None] | None = None,
        on_task_delete: Callable[[TaskRead], None] | None = None,
    ) -> None:
        """TasksBoardのコンストラクタ

        Args:
            on_task_click: タスククリック時のコールバック
            on_task_status_change: タスクステータス変更時のコールバック
            on_task_delete: タスク削除時のコールバック
        """
        super().__init__()
        self.on_task_click = on_task_click
        self.on_task_status_change = on_task_status_change
        self.on_task_delete = on_task_delete

        container = get_application_service_container()
        self._task_app_service: TaskApplicationService = container.get_task_application_service()

        # スタイル設定
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 12
        self.padding = 16
        self.margin = ft.margin.symmetric(vertical=8)
        self.expand = True  # 利用可能な縦スペースを最大限活用

        # タスクデータ
        self.tasks_by_status: dict[TaskStatus, list[TaskRead]] = {}

        # コンテンツの構築
        self._load_tasks()
        self._build_content()

    def _load_tasks(self) -> None:
        """タスクデータを読み込み"""
        try:
            from logic.queries.task_queries import GetAllTasksByStatusDictQuery

            query = GetAllTasksByStatusDictQuery()
            self.tasks_by_status = self._task_app_service.get_all_tasks_by_status_dict(query)

        except Exception as e:
            logger.error(f"タスク読み込みエラー: {e}")
            # エラー時は空のリストで初期化
            for status in TaskStatus:
                self.tasks_by_status[status] = []

    def _build_content(self) -> None:
        """コンテンツを構築"""
        logger.info("TasksBoard コンテンツ構築開始")

        try:
            self.content = ft.Row(
                [
                    # 左カラム: CLOSED
                    self._build_closed_column(),
                    # 右カラム: INBOX
                    self._build_inbox_column(),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,  # 上揃え
            )
            logger.info("TasksBoard コンテンツ構築完了")
        except Exception as e:
            logger.error(f"TasksBoard コンテンツ構築エラー: {e}")
            # エラー時は簡単なテキストを表示
            self.content = ft.Text(
                f"タスクボード読み込みエラー: {e}",
                color=ft.Colors.RED,
                size=16,
            )

    def _build_closed_column(self) -> ft.Container:
        """CLOSEDカラムを構築"""
        return ft.Container(
            content=ft.Column(
                [
                    # カラムヘッダー
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.ARCHIVE,
                                color=ft.Colors.GREY_600,
                                size=20,
                            ),
                            ft.Text(
                                "CLOSED",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(height=12),  # スペーサー
                    # [AI GENERATED] ステータスセクション（Application Serviceから表示ラベルを取得）
                    self._build_status_section_from_service("CLOSED", TaskStatus.NEXT_ACTION),
                    self._build_status_section_from_service("CLOSED", TaskStatus.DELEGATED),
                    self._build_status_section_from_service("CLOSED", TaskStatus.COMPLETED),
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,  # スクロール機能を追加
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            width=300,  # 明示的な幅を設定
            expand=True,  # 縦スペースを最大限活用
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def _build_inbox_column(self) -> ft.Container:
        """INBOXカラムを構築"""
        return ft.Container(
            content=ft.Column(
                [
                    # カラムヘッダー
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INBOX,
                                color=ft.Colors.BLUE_600,
                                size=20,
                            ),
                            ft.Text(
                                "INBOX",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(height=12),  # スペーサー
                    # [AI GENERATED] ステータスセクション（Application Serviceから表示ラベルを取得）
                    self._build_status_section_from_service("INBOX", TaskStatus.INBOX),
                    self._build_status_section_from_service("INBOX", TaskStatus.NEXT_ACTION),
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,  # スクロール機能を追加
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            width=300,  # 明示的な幅を設定
            expand=True,  # 縦スペースを最大限活用
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def _build_status_section(self, title: str, status: TaskStatus) -> ft.Container:
        """ステータスセクションを構築"""
        tasks = self.tasks_by_status.get(status, [])
        task_count = len(tasks)

        return ft.Container(
            content=ft.Column(
                [
                    # セクションヘッダー
                    ft.Row(
                        [
                            ft.Text(
                                title,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_800,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(task_count),
                                    size=12,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=ft.Colors.BLUE_600 if task_count > 0 else ft.Colors.GREY_400,
                                border_radius=10,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            ),
                        ]
                    ),
                    ft.Container(height=8),  # スペーサー
                    # タスクリスト
                    ft.Column(
                        [self._create_task_card(task) for task in tasks] if tasks else [self._create_empty_state()],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            padding=12,
            # 将来のドロップゾーン準備
            border=ft.border.all(2, ft.Colors.TRANSPARENT),
        )

    def _create_task_card(self, task: TaskRead) -> ft.Container:
        """タスクカードを作成（将来ドラッグ対応予定）"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Checkbox(
                        value=task.status == TaskStatus.COMPLETED,
                        on_change=lambda e, t=task: self._toggle_task_completion(t, is_completed=e.control.value),
                    ),
                    ft.Text(
                        task.title,
                        size=14,
                        color=ft.Colors.GREY_800,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=16,
                        tooltip="編集",
                        on_click=lambda _, t=task: self._handle_task_click(t),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip="削除",
                        on_click=lambda _, t=task: self._handle_task_delete(t),
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border=ft.border.all(1, ft.Colors.GREY_200),
            # 将来のドラッグ機能準備
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _create_empty_state(self) -> ft.Container:
        """空状態の表示"""
        return ft.Container(
            content=ft.Text(
                "タスクがありません",
                size=12,
                color=ft.Colors.GREY_500,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=16,
        )

    def _toggle_task_completion(self, task: TaskRead, *, is_completed: bool) -> None:
        """タスク完了状態の切り替え"""
        try:
            new_status = TaskStatus.COMPLETED if is_completed else TaskStatus.NEXT_ACTION

            # Application Serviceを使用（Session管理不要）
            command = UpdateTaskStatusCommand(
                task_id=task.id,
                new_status=new_status,
            )

            self._task_app_service.update_task_status(command)

            if self.on_task_status_change:
                self.on_task_status_change(task, new_status)

            # UI更新
            self.refresh()

        except Exception as e:
            logger.error(f"タスクステータス更新エラー: {e}")

    def _handle_task_click(self, task: TaskRead) -> None:
        """タスククリック処理"""
        if self.on_task_click:
            self.on_task_click(task)

    def _handle_task_delete(self, task: TaskRead) -> None:
        """タスク削除処理"""
        if self.on_task_delete:
            self.on_task_delete(task)

    def refresh(self) -> None:
        """ボードを再読み込み"""
        self._load_tasks()
        self._build_content()
        if self.page:
            self.update()

    def _build_status_section_from_service(self, section_name: str, status: TaskStatus) -> ft.Container:
        """Application Serviceから表示ラベルを取得してステータスセクションを構築

        Args:
            section_name: セクション名（"CLOSED" または "INBOX"）
            status: タスクステータス

        Returns:
            ステータスセクションのコンテナ
        """
        try:
            # [AI GENERATED] Application Serviceから表示ラベルを取得
            title = self._task_app_service.get_board_section_display(section_name, status)
            return self._build_status_section(title, status)
        except Exception as e:
            logger.error(f"表示ラベル取得エラー: {e}")
            # [AI GENERATED] エラー時はフォールバック表示を使用
            fallback_title = f"⚠️ {status.value}"
            return self._build_status_section(fallback_title, status)
