# router.py
# ページルーティングの管理を専用モジュールに分離
import flet as ft

from views import (
    # get_layout,
    create_home_view,
    # task_view,
)
from views.layout import get_layout

ROUTES = {
    "/": create_home_view,
    # "/task": task_view,
    # 今後ページが増えた場合はここに追加
}


def route_change(e: ft.RouteChangeEvent) -> None:
    """ページルーティングイベントハンドラ。

    ROUTES辞書に基づきページを切り替える。
    """
    page: ft.Page = e.page
    page.views.clear()
    view_func = ROUTES.get(page.route)
    if not view_func:
        page.go("/")
        return
    page.views.append(get_layout(page, view_func(page)))
    page.update()
