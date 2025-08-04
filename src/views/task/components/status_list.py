"""タスクステータスコンポーネント

ステータス別のタスク表示機能を提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models import TaskStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.task_service import TaskService


class StatusList(ft.Container):
    """ステータスリストコンポーネント

    ステータス別タスク表示機能を提供します。
    """

    def __init__(
        self,
        task_service: TaskService,
        on_status_select: Callable[[TaskStatus | None], None] | None = None,
    ) -> None:
        """StatusListのコンストラクタ

        Args:
            task_service: タスクサービス
            on_status_select: ステータス選択時のコールバック
        """
        super().__init__()
        self.task_service = task_service
        self.on_status_select = on_status_select

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

        # ステータスデータ
        self.status_counts: dict[TaskStatus, int] = {}
        self.selected_status: TaskStatus | None = None

        # コンテンツの構築
        self._load_status_counts()
        self._build_content()

    def _load_status_counts(self) -> None:
        """ステータス別のタスク数を読み込み"""
        try:
            for status in TaskStatus:
                tasks = self.task_service.get_tasks_by_status(status)
                self.status_counts[status] = len(tasks)
            logger.info(f"ステータス数読み込み完了: {self.status_counts}")
        except Exception as e:
            logger.error(f"ステータス数読み込みエラー: {e}")
            self.status_counts = dict.fromkeys(TaskStatus, 0)

    def _build_content(self) -> None:
        """コンテンツを構築"""
        logger.info("StatusList コンテンツ構築開始")

        # ステータス項目定義
        status_items = [
            ("📥 受信箱", TaskStatus.INBOX, ft.Colors.BLUE_600),
            ("🎯 次のアクション", TaskStatus.NEXT_ACTION, ft.Colors.ORANGE_600),
            ("🔄 進行中", TaskStatus.DELEGATED, ft.Colors.PURPLE_600),
            ("✅ 完了", TaskStatus.COMPLETED, ft.Colors.GREEN_600),
        ]

        self.content = ft.Column(
            [
                # ヘッダー
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LIST,
                            color=ft.Colors.BLUE_600,
                            size=20,
                        ),
                        ft.Text(
                            "ステータス",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),  # スペーサー
                # ステータスリスト
                ft.Column(
                    [self._create_status_item(title, status, color) for title, status, color in status_items],
                    spacing=4,
                ),
            ],
            spacing=0,
        )

    def _create_status_item(self, title: str, status: TaskStatus, color: str) -> ft.Container:
        """ステータスアイテムを作成

        Args:
            title: ステータスタイトル
            status: タスクステータス
            color: テーマカラー

        Returns:
            ステータスアイテムのコンテナ
        """
        count = self.status_counts.get(status, 0)
        is_selected = self.selected_status == status

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.RADIO_BUTTON_CHECKED if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        size=16,
                        color=color if is_selected else ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        title,
                        size=14,
                        color=ft.Colors.GREY_800 if is_selected else ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(count),
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=color if count > 0 else ft.Colors.GREY_400,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, color) if is_selected else ft.Colors.TRANSPARENT,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            on_click=lambda _, s=status: self._handle_status_select(s),
            ink=True,
        )

    def _handle_status_select(self, status: TaskStatus) -> None:
        """ステータス選択処理

        Args:
            status: 選択されたステータス
        """
        self.selected_status = status if self.selected_status != status else None

        if self.on_status_select:
            self.on_status_select(self.selected_status)

        # UI更新
        self._build_content()
        self.update()

    def refresh(self) -> None:
        """ステータスリストを再読み込み"""
        self._load_status_counts()
        self._build_content()
        if hasattr(self, "update"):
            self.update()
