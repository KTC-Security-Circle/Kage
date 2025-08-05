"""FletNativeRouterを使用したルーティング設定。

HomeViewとTaskViewの画面遷移を提供する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    import flet as ft

from router import (
    FletNativeRouter,
    create_app_bar,
    create_route_config,
    logging_middleware,
    performance_middleware,
)
from views.home.view import HomeView
from views.task.view import TaskView


def setup_enhanced_routing(page: ft.Page) -> None:
    """FletNativeRouterを使用したルーティングを設定する。

    Args:
        page: Fletのページオブジェクト
    """
    logger.info("FletNativeRouter を使用してルーティングを設定します")

    # [AI GENERATED] ルーターを初期化
    router = FletNativeRouter(page)

    # [AI GENERATED] ルート設定を作成
    home_route = create_route_config(
        path="/",
        view_class=HomeView,
        app_bar=create_app_bar("Kage"),
    )

    task_route = create_route_config(
        path="/task",
        view_class=TaskView,
        app_bar=create_app_bar("タスク管理"),
    )

    # [AI GENERATED] ルートを登録
    router.register_routes(home_route, task_route)

    # [AI GENERATED] ミドルウェアを追加
    router.add_middleware(logging_middleware)
    router.add_middleware(performance_middleware)

    # [AI GENERATED] 初期ルートに遷移
    page.go("/")

    logger.info("FletNativeRouter ルーティング設定完了")
