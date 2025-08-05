"""クイックアクションコンポーネント

タスク管理ワークフローのクイックアクション部分を独立したコンポーネントとして提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models import QuickActionCommand

if TYPE_CHECKING:
    from collections.abc import Callable


class QuickActions(ft.Container):
    """クイックアクションコンポーネント

    ユーザーがタスクを素早く追加できるアクションボタンを提供します。
    """

    def __init__(
        self,
        on_action_click: Callable[[QuickActionCommand], None],
    ) -> None:
        """QuickActionsのコンストラクタ

        Args:
            on_action_click: アクションクリック時のコールバック
        """
        super().__init__()
        self.on_action_click = on_action_click

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
        logger.info("QuickActions コンテンツ構築開始")

        # アクションボタンリスト
        action_buttons = [
            self._create_action_button(
                icon=ft.Icons.ADD_CIRCLE,
                text="すぐにやる",
                action=QuickActionCommand.DO_NOW,
                color=ft.Colors.RED_500,
            ),
            self._create_action_button(
                icon=ft.Icons.SCHEDULE,
                text="次にやる",
                action=QuickActionCommand.DO_NEXT,
                color=ft.Colors.ORANGE_500,
            ),
            self._create_action_button(
                icon=ft.Icons.ACCESS_TIME,
                text="いつかやる",
                action=QuickActionCommand.DO_SOMEDAY,
                color=ft.Colors.BLUE_500,
            ),
            self._create_action_button(
                icon=ft.Icons.BOOKMARK,
                text="参考資料",
                action=QuickActionCommand.REFERENCE,
                color=ft.Colors.GREEN_500,
            ),
        ]

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "📋 クイックアクション",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_100),
                ft.Row(
                    action_buttons,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    wrap=True,
                ),
            ],
            spacing=12,
        )

    def _create_action_button(
        self,
        icon: str,
        text: str,
        action: QuickActionCommand,
        color: str,
    ) -> ft.Container:
        """アクションボタンを作成

        Args:
            icon: アイコン
            text: ボタンテキスト
            action: アクション名
            color: ボタンカラー

        Returns:
            作成されたアクションボタン
        """

        def on_click(_: ft.ControlEvent) -> None:
            """ボタンクリック時の処理"""
            logger.info(f"クイックアクション実行: {action}")
            self.on_action_click(action)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        icon,
                        size=28,
                        color=color,
                    ),
                    ft.Text(
                        text,
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_GREY_700,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            width=100,
            height=80,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
            padding=8,
            on_click=on_click,
            ink=True,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    def update_actions(self, actions: list[dict]) -> None:
        """アクションリストを更新

        Args:
            actions: 新しいアクションリスト
        """
        logger.info(f"QuickActions アクションリスト更新: {len(actions)}個のアクション")
        # 将来: 動的なアクションリスト更新をサポート
