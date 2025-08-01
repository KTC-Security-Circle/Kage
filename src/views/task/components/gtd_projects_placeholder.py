"""GTDプロジェクトプレースホルダーコンポーネント

将来のプロジェクト機能実装までの一時的なプレースホルダーを提供します。
"""

from __future__ import annotations

import flet as ft
from loguru import logger


class GTDProjectsPlaceholder(ft.Container):
    """GTDプロジェクトプレースホルダーコンポーネント

    プロジェクト機能が実装されるまでの間、プレースホルダーを表示します。
    """

    def __init__(self) -> None:
        """GTDProjectsPlaceholderのコンストラクタ"""
        super().__init__()

        # スタイル設定
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 12
        self.padding = 20
        self.margin = ft.margin.symmetric(vertical=8)
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
                # セクションヘッダー
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.FOLDER_OUTLINED,
                            color=ft.Colors.GREY_500,
                            size=24,
                        ),
                        ft.Text(
                            "PROJECTS",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Container(height=16),  # スペーサー
                # プレースホルダーメッセージ
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.CONSTRUCTION,
                                size=48,
                                color=ft.Colors.GREY_400,
                            ),
                            ft.Container(height=12),
                            ft.Text(
                                "プロジェクト機能は近日実装予定です",
                                size=14,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "現在、基本的なタスク管理機能をご利用いただけます",
                                size=12,
                                color=ft.Colors.GREY_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                ),
            ],
            spacing=0,
        )

    def on_click_placeholder(self) -> None:
        """プレースホルダークリック時の処理"""
        logger.info("プロジェクト機能は未実装のため、プレースホルダーが表示されています")
