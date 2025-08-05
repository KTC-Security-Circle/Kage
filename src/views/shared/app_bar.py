import flet as ft

from config import APP_TITLE


def app_bar(page: ft.Page) -> ft.AppBar:
    """アプリケーションのヘッダーを生成"""
    return ft.AppBar(
        leading=ft.IconButton(ft.Icons.HOME, on_click=lambda _: page.go("/")),
        title=ft.Text(APP_TITLE),
        center_title=False,
        actions=[
            ft.IconButton(ft.Icons.HOME, on_click=lambda _: page.go("/")),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text="タスク",
                        on_click=lambda _: page.go("/task"),
                    ),
                    # ft.PopupMenuItem(
                    #     text="ログアウト",
                    #     on_click=lambda _: page.go("/logout"),
                    # ),
                ],
            ),
        ],
    )
