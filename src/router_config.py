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
    create_route_config,
    logging_middleware,
    performance_middleware,
)
from views.home.view import HomeView
from views.memo.components import MemoDetailView
from views.memo.view import MemoCreateView, MemoView
from views.shared import app_bar
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
        app_bar=app_bar(page),
        name="home",
    )

    task_route = create_route_config(
        path="/task",
        view_class=TaskView,
        app_bar=app_bar(page, "タスク管理"),
        name="task",
    )

    memo_route = create_route_config(
        path="/memo",
        view_class=MemoView,
        app_bar=app_bar(page, "メモ管理"),
        name="memo",
    )

    memo_create_route = create_route_config(
        path="/memo/create",
        view_class=MemoCreateView,
        app_bar=app_bar(page, "新規メモ作成"),
        name="memo_create",
    )

    memo_detail_route = create_route_config(
        path="/memo/detail",
        view_class=MemoDetailView,
        app_bar=app_bar(page, "メモ詳細"),
        name="memo_detail",
    )

    # [AI GENERATED] ルートを登録
    router.register_routes(home_route, task_route, memo_route, memo_create_route, memo_detail_route)

    # [AI GENERATED] ミドルウェアを追加
    router.add_middleware(logging_middleware)
    router.add_middleware(performance_middleware)

    # [AI GENERATED] 初期ルートに遷移
    page.go("/")

    logger.info("FletNativeRouter ルーティング設定完了")
