"""GTDクイックアクションコンポーネント

GTDワークフローのクイックアクション部分を独立したコンポーネントとして提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable


class GTDQuickActions(ft.Container):
    """GTDクイックアクションコンポーネント

    ユーザーがタスクを素早く追加できるアクションボタンを提供します。
    """

    def __init__(
        self,
        on_action_click: Callable[[str], None],
    ) -> None:
        """GTDQuickActionsのコンストラクタ

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
        logger.info("GTDQuickActions コンテンツ構築開始")

        try:
            self.content = ft.Column(
                [
                    # セクションヘッダー
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.FLASH_ON,
                                color=ft.Colors.BLUE_600,
                                size=20,
                            ),
                            ft.Text(
                                "QUICK ACTIONS",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=8, color=ft.Colors.GREY_300),
                    # アクションボタンを横並びに配置
                    ft.Row(
                        [
                            self._create_action_button(
                                "📥 Inbox に追加",
                                "add_to_inbox",
                                ft.Colors.BLUE_600,
                                ft.Icons.INBOX,
                            ),
                            self._create_action_button(
                                "☑️ 本日のタスクを追加",
                                "add_today_task",
                                ft.Colors.GREEN_600,
                                ft.Icons.TODAY,
                            ),
                            self._create_action_button(
                                "⏳ 待ちタスクを追加",
                                "add_waiting_task",
                                ft.Colors.ORANGE_600,
                                ft.Icons.HOURGLASS_EMPTY,
                            ),
                        ],
                        spacing=12,
                        wrap=True,  # 画面幅に応じて折り返し
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=8,
            )
            logger.info("GTDQuickActions コンテンツ構築完了")
        except Exception as e:
            logger.error(f"GTDQuickActions コンテンツ構築エラー: {e}")
            # エラー時は簡単なテキストを表示
            self.content = ft.Text(
                f"クイックアクション読み込みエラー: {e}",
                color=ft.Colors.RED,
                size=16,
            )

    def _create_action_button(self, label: str, action: str, color: str, icon: ft.Icons) -> ft.Container:
        """アクションボタンを作成（横並び用のコンパクトデザイン）"""
        return ft.Container(
            content=ft.Column(
                [
                    # アイコン
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=24),
                        bgcolor=color,
                        border_radius=12,
                        padding=12,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=8),  # スペーサー
                    # ラベル
                    ft.Text(
                        label,
                        size=12,
                        color=ft.Colors.GREY_800,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_200),
            on_click=lambda _: self._handle_action_click(action),
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
            width=180,  # 固定幅で確実に表示
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
        )

    def _handle_action_click(self, action: str) -> None:
        """アクションクリック処理"""
        logger.info(f"クイックアクション実行: {action}")
        self.on_action_click(action)
