import flet as ft

from views.shared.app_bar import app_bar


def get_layout(page: ft.Page, content: ft.Control) -> ft.View:
    """ページ全体のレイアウトを生成"""
    return ft.View(
        page.route,
        [
            app_bar(page),
            content,
        ],
    )
