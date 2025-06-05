# router.py
# ページルーティングの管理を専用モジュールに分離
import flet as ft

from views import (
    get_layout,
    home_view,
    task_view,
)

ROUTES = {
    "/": home_view,
    "/task": task_view,
    # 今後ページが増えた場合はここに追加
}


def route_change(e: ft.RouteChangeEvent) -> None:
    """ページルーティングイベントハンドラ。

    ROUTES辞書に基づきページを切り替える。
    """
    page = e.page
    page.views.clear()
    view_func = ROUTES.get(page.route)
    if view_func:
        page.views.append(get_layout(page, view_func(page)))
    else:
        # 未定義ルートの場合はホームにリダイレクト
        page.views.append(get_layout(page, home_view(page)))
    page.update()
