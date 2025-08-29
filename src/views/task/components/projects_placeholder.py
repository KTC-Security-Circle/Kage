"""プロジェクトプレースホルダーコンポーネント

将来のプロジェクト機能実装までの一時的なプレースホルダーを提供します。
"""

from __future__ import annotations

import flet as ft
from loguru import logger


class ProjectsPlaceholder(ft.Container):
    """プロジェクトプレースホルダーコンポーネント

    プロジェクト機能が実装されるまでの間、プレースホルダーを表示します。
    """

    def __init__(self) -> None:
        """ProjectsPlaceholderのコンストラクタ"""
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
                            ft.Text(
                                "プロジェクト機能は開発中です",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "近日中にリリース予定です。\nタスクの整理やグループ化機能を提供します。",
                                size=14,
                                color=ft.Colors.GREY_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    padding=32,
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=0,
        )

    def refresh(self) -> None:
        """プレースホルダーをリフレッシュ"""
        logger.info("ProjectsPlaceholder リフレッシュ")
        # 将来: プロジェクトデータの更新処理を追加
