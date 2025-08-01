"""GTDタスクステータスコンポーネント

GTDステータス別のタスク表示機能を提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models.new_task import TaskStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.task_service import TaskService


class GTDStatusList(ft.Container):
    """GTDステータスリストコンポーネント

    GTDのステータス別タスク表示機能を提供します。
    """

    def __init__(
        self,
        task_service: TaskService,
        on_status_click: Callable[[TaskStatus], None],
    ) -> None:
        """GTDStatusListのコンストラクタ

        Args:
            task_service: タスクサービス
            on_status_click: ステータスクリック時のコールバック
        """
        super().__init__()
        self.task_service = task_service
        self.on_status_click = on_status_click

        # スタイル設定
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 12
        self.padding = 16
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        )

        # コンテンツの構築
        self._build_content()

    def _build_content(self) -> None:
        """コンテンツを構築"""
        self.content = ft.Column(
            [
                # INBOX セクション
                self._build_section(
                    "INBOX",
                    ft.Icons.INBOX,
                    ft.Colors.BLUE_600,
                    [
                        ("📥 整理用", TaskStatus.INBOX),
                        ("🎯 次に取るべき行動", TaskStatus.NEXT_ACTION),
                    ],
                ),
                ft.Divider(height=8, color=ft.Colors.GREY_300),
                # CLOSED セクション
                self._build_section(
                    "CLOSED",
                    ft.Icons.ARCHIVE,
                    ft.Colors.GREY_600,
                    [
                        ("📋 ToDo", TaskStatus.NEXT_ACTION),
                        ("🔄 InProgress", TaskStatus.DELEGATED),
                        ("✅ Done", TaskStatus.COMPLETED),
                    ],
                ),
            ],
            spacing=16,
        )

    def _build_section(
        self, title: str, icon: ft.Icons, color: str, status_items: list[tuple[str, TaskStatus]]
    ) -> ft.Column:
        """セクションを構築"""
        return ft.Column(
            [
                # セクションヘッダー
                ft.Row(
                    [
                        ft.Icon(icon, color=color, size=20),
                        ft.Text(
                            title,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800,
                        ),
                    ],
                    spacing=8,
                ),
                # ステータス項目
                ft.Column(
                    [self._create_status_item(label, status) for label, status in status_items],
                    spacing=4,
                ),
            ],
            spacing=8,
        )

    def _create_status_item(self, label: str, status: TaskStatus) -> ft.Container:
        """ステータス項目を作成"""
        # タスク数を取得（エラーハンドリング付き）
        task_count = self._get_task_count(status)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        label,
                        size=14,
                        color=ft.Colors.GREY_800,
                        expand=True,
                    ),
                    ft.Text(
                        str(task_count),
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD_IOS,
                        color=ft.Colors.GREY_400,
                        size=12,
                    ),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.GREY_200),
            on_click=lambda _, s=status: self._handle_status_click(s),
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _get_task_count(self, status: TaskStatus) -> int:
        """指定ステータスのタスク数を取得"""
        try:
            tasks = self.task_service.get_tasks_by_status(status)
            return len(tasks)
        except Exception as e:
            logger.error(f"タスク数取得エラー (status: {status.value}): {e}")
            return 0

    def _handle_status_click(self, status: TaskStatus) -> None:
        """ステータスクリック処理"""
        logger.info(f"ステータス選択: {status.value}")
        self.on_status_click(status)

    def refresh(self) -> None:
        """ステータスリストを再読み込み"""
        # タスク数を更新するため、コンテンツを再構築
        self._build_content()
        if self.page:
            self.update()
