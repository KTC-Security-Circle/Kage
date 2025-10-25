"""空の状態コンポーネント

タグが存在しない場合の空の状態UIコンポーネント。
アイコン、メッセージ、アクションボタンを含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


def create_empty_state(
    on_create: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
) -> ft.Control:  # type: ignore[name-defined]
    """空の状態を構築する。

    Args:
        on_create: 作成ボタンクリック時のコールバック

    Returns:
        空の状態コンポーネント
    """
    import flet as ft

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.LABEL_OUTLINE,
                    size=64,
                    color=ft.colors.GREY_400,
                ),
                ft.Text(
                    "タグがありません",
                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=ft.colors.GREY_600,
                ),
                ft.Text(
                    "新規タグを作成してタスクを分類しましょう",
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.ElevatedButton(
                    text="最初のタグを作成",
                    icon=ft.Icons.ADD,
                    on_click=on_create,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
