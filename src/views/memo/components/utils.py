"""メモコンポーネント用のユーティリティ関数モジュール."""

from __future__ import annotations

import flet as ft


def create_memo_welcome_message() -> ft.Container:
    """メモ用ウェルカムメッセージを作成.

    Returns:
        ウェルカムメッセージのContainerコンポーネント
    """
    return ft.Container(
        content=ft.Text(
            "メモでアイデアを整理しよう！",
            size=18,
        ),
        alignment=ft.alignment.center,
    )
