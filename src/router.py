"""ページルーティングの管理 - 新Views対応版

Fletのネイティブルーティング機能を活用し、新しいviewsレイアウトシステムと統合。
AppBarを使用しない、サイドバーベースのナビゲーション体験を提供する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    import flet as ft

from views.layout import build_layout


def configure_routes(page: ft.Page) -> None:  # type: ignore[name-defined]
    """ページのルーティングを初期化する。

    Args:
        page: Fletのページオブジェクト

    Notes:
        新しいviewsレイアウトシステムを使用し、
        build_layout関数でサイドバー統合レイアウトを構築する。
    """
    import flet as ft  # noqa: F401

    def route_change(e: ft.RouteChangeEvent) -> None:
        """ルート変更イベントハンドラ。

        Args:
            e: ルート変更イベント
        """
        route = e.route
        logger.info(f"Route change: {route}")

        try:
            # Clear existing views
            page.views.clear()

            # Build new layout with sidebar
            new_view = build_layout(page, route)
            page.views.append(new_view)

            page.update()

        except Exception as error:
            logger.error(f"Route handling error: {error}")
            # Fallback to home route
            if route != "/":
                page.go("/")

    def view_pop(_: ft.ViewPopEvent) -> None:
        """ビューポップイベントハンドラ。

        Args:
            _: ビューポップイベント（未使用）
        """
        page.views.pop()
        if page.views:
            top_view = page.views[-1]
            if top_view.route:
                page.go(top_view.route)
        else:
            # Go to home if no views left
            page.go("/")

    # Set up Flet routing events
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Navigate to initial route
    page.go(page.route or "/")

    logger.info("New routing system initialized with views layout")
