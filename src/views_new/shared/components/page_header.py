"""ページヘッダーコンポーネント

一般的なページヘッダーUIコンポーネント。
カスタマイズ可能なタイトルとサブタイトルを表示。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft


def create_page_header(title: str, subtitle: str) -> ft.Control:  # type: ignore[name-defined]
    """ページヘッダーを構築する。

    Args:
        title: メインタイトル
        subtitle: サブタイトル（アイテム数など）

    Returns:
        ヘッダーコンポーネント
    """
    import flet as ft

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            title,
                            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            subtitle,
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.colors.GREY_600,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(bottom=16),
    )
