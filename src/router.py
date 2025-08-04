# router.py
# ページルーティングの管理を専用モジュールに分離

from collections.abc import Callable

import flet as ft

from views import (
    # get_layout,
    create_home_view,
)
from views.layout import get_layout
from views.task.view import create_task_view

ROUTES: dict[str, Callable[[ft.Page], ft.Container]] = {
    "/": create_home_view,
    "/task": create_task_view,
    # 今後ページが増えた場合はここに追加
}


class Router:
    """ページルーティングを管理するクラス。

    ページのルーティングとビューの切り替えを行う。
    """

    def __init__(self, page: ft.Page) -> None:
        """Routerのコンストラクタ。

        Args:
            page: Fletのページオブジェクト
        """
        self.page = page
        self.page.on_route_change = self.route_change
        self.page.go(self.page.route)

    def route_change(self, _: ft.RouteChangeEvent) -> None:
        """ページルーティングイベントハンドラ。

        ROUTES辞書に基づきページを切り替える。
        """
        self.page.views.clear()
        view_func = ROUTES.get(self.page.route)
        if not view_func:
            self.page.go("/")
            return
        self.page.views.append(get_layout(self.page, view_func(self.page)))
        self.page.update()
