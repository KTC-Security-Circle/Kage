"""ページルーティングの管理を専用モジュールに分離

Fletのネイティブルーティング機能を活用した改良版ルーター実装。
BaseViewクラスのライフサイクルと統合した効率的なナビゲーション体験を提供する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

    from views.shared.base_view import BaseView

import flet as ft

from views.shared.base_view import BaseView

T = TypeVar("T", bound=BaseView)


@dataclass(frozen=True)
class RouteConfig:
    """Fletルーティングに最適化されたルート設定。

    BaseViewのライフサイクル管理とFletのView機能を統合する。
    """

    path: str
    view_class: type[BaseView]
    name: str = ""
    title: str = ""
    app_bar: ft.AppBar | None = None
    requires_auth: bool = False
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """初期化後の処理。"""
        if not self.name:
            object.__setattr__(self, "name", self.path.strip("/") or "home")
        if not self.title:
            object.__setattr__(self, "title", self.name.title())


class ViewFactory:
    """BaseViewインスタンスを効率的に管理するファクトリー。

    ビューのキャッシングとライフサイクル管理を行う。
    """

    def __init__(self) -> None:
        """ViewFactoryのコンストラクタ。"""
        self._view_cache: dict[str, BaseView] = {}
        self._view_instances: dict[type[BaseView], BaseView] = {}

    def create_view(
        self, view_class: type[BaseView], page: ft.Page, route_path: str, *, force_new: bool = False
    ) -> BaseView:
        """ビューを作成または取得する。

        Args:
            view_class: ビュークラス
            page: Fletのページオブジェクト
            route_path: ルートパス
            force_new: 強制的に新しいインスタンスを作成するか（キーワード専用）

        Returns:
            BaseView: ビューインスタンス
        """
        cache_key = f"{view_class.__name__}:{route_path}"

        if not force_new and cache_key in self._view_cache:
            view = self._view_cache[cache_key]
            # [AI GENERATED] ページオブジェクトが変更されている場合は更新
            if view.page != page:
                view.page = page
            return view

        # [AI GENERATED] 新しいビューインスタンスを作成
        try:
            view = view_class(page)
            view.mount()  # BaseViewのマウント処理を実行
            self._view_cache[cache_key] = view
            self._view_instances[view_class] = view
            logger.info(f"ビュー作成完了: {view_class.__name__} -> {route_path}")
        except Exception as e:
            logger.error(f"ビュー作成エラー: {view_class.__name__} -> {e}")
            raise
        else:
            return view

    def get_cached_view(self, view_class: type[BaseView]) -> BaseView | None:
        """キャッシュされたビューを取得する。

        Args:
            view_class: ビュークラス

        Returns:
            BaseView | None: キャッシュされたビューまたはNone
        """
        return self._view_instances.get(view_class)

    def clear_cache(self, view_class: type[BaseView] | None = None) -> None:
        """ビューキャッシュをクリアする。

        Args:
            view_class: クリアするビュークラス（Noneで全てクリア）
        """
        if view_class is None:
            # [AI GENERATED] 全てのビューをアンマウント
            for view in self._view_cache.values():
                if view.is_mounted:
                    view.unmount()
            self._view_cache.clear()
            self._view_instances.clear()
            logger.info("全ビューキャッシュをクリア")
        else:
            # [AI GENERATED] 特定のビューのみクリア
            view = self._view_instances.get(view_class)
            if view and view.is_mounted:
                view.unmount()

            # キャッシュから削除
            keys_to_remove = [k for k in self._view_cache if k.startswith(f"{view_class.__name__}:")]
            for key in keys_to_remove:
                del self._view_cache[key]

            if view_class in self._view_instances:
                del self._view_instances[view_class]

            logger.info(f"ビューキャッシュをクリア: {view_class.__name__}")


class FletNativeRouter:
    """Fletのネイティブルーティング機能を活用したルーター。

    Fletの公式ルーティングAPIとBaseViewのライフサイクルを統合し、
    自然で効率的なナビゲーション体験を提供する。
    """

    def __init__(self, page: ft.Page) -> None:
        """FletNativeRouterのコンストラクタ。

        Args:
            page: Fletのページオブジェクト
        """
        self.page = page
        self._routes: dict[str, RouteConfig] = {}
        self._view_factory = ViewFactory()
        self._middleware: list[Callable[[ft.RouteChangeEvent], Any]] = []
        self._auth_checker: Callable[[ft.Page], bool] | None = None
        self._current_view: BaseView | None = None

        # [AI GENERATED] Fletのルーティングイベントを設定
        self.page.on_route_change = self._handle_route_change
        self.page.on_view_pop = self._handle_view_pop

        logger.info("FletNativeRouter初期化完了")

    def register_route(self, route_config: RouteConfig) -> None:
        """ルートを登録する。

        Args:
            route_config: ルート設定
        """
        self._routes[route_config.path] = route_config
        logger.debug(f"ルート登録: {route_config.path} -> {route_config.view_class.__name__}")

    def register_routes(self, *route_configs: RouteConfig) -> None:
        """複数のルートを一括登録する。

        Args:
            *route_configs: ルート設定群
        """
        for config in route_configs:
            self.register_route(config)

    def add_middleware(self, middleware: Callable[[ft.RouteChangeEvent], Any]) -> None:
        """ミドルウェアを追加する。

        Args:
            middleware: ミドルウェア関数
        """
        self._middleware.append(middleware)

    def set_auth_checker(self, checker: Callable[[ft.Page], bool]) -> None:
        """認証チェック関数を設定する。

        Args:
            checker: 認証チェック関数
        """
        self._auth_checker = checker

    def _handle_route_change(self, e: ft.RouteChangeEvent) -> None:
        """Fletのルート変更イベントハンドラ。

        Args:
            e: ルート変更イベント
        """
        logger.info(f"ルート変更: {e.route}")

        # [AI GENERATED] ミドルウェアを実行
        for middleware in self._middleware:
            try:
                middleware(e)
            except Exception as middleware_error:
                logger.error(f"ミドルウェアエラー: {middleware_error}")

        # [AI GENERATED] ルート設定を取得
        route_config = self._routes.get(e.route)
        if not route_config:
            logger.warning(f"未登録ルート: {e.route}")
            self._handle_not_found()
            return

        # [AI GENERATED] 認証チェック
        if route_config.requires_auth and self._auth_checker and not self._auth_checker(self.page):
            logger.warning(f"認証が必要なルートへの不正アクセス: {e.route}")
            self.page.go("/login")  # ログインページにリダイレクト
            return

        # [AI GENERATED] ビューを作成・表示
        try:
            self._display_view(route_config)
        except Exception as error:
            logger.error(f"ビュー表示エラー: {error}")
            self._handle_error(error)

    def _display_view(self, route_config: RouteConfig) -> None:
        """ビューを表示する。

        Args:
            route_config: ルート設定
        """
        try:
            view = self._view_factory.create_view(route_config.view_class, self.page, route_config.path)

            flet_view = ft.View(
                route=route_config.path,
                controls=[view],
                appbar=route_config.app_bar,
            )

            self.page.views.append(flet_view)
            self.page.update()

            # [AI GENERATED] 現在のビューを更新
            self._current_view = view
            logger.info(f"ビュー表示完了: {route_config.view_class.__name__}")
        except Exception as error:
            logger.error(f"ビュー表示処理エラー: {error}")
            raise

    def _handle_view_pop(self, _: ft.ViewPopEvent) -> None:
        """Fletのビューポップイベントハンドラ。

        Args:
            _: ビューポップイベント（未使用）
        """
        self.page.views.pop()
        if self.page.views:
            top_view = self.page.views[-1]
            if top_view.route:
                self.page.go(top_view.route)
        else:
            # [AI GENERATED] ルートビューに戻る
            self.page.go("/")

    def _handle_not_found(self) -> None:
        """404エラーハンドリング。"""
        logger.warning("404 - ページが見つかりません")
        # [AI GENERATED] 404ページまたはホームにリダイレクト
        default_route = "/" if "/" in self._routes else next(iter(self._routes.keys()))
        self.page.go(default_route)

    def _handle_error(self, error: Exception) -> None:
        """エラーハンドリング。

        Args:
            error: 発生したエラー
        """
        logger.error(f"ルーターエラー: {error}")
        # [AI GENERATED] エラーページまたはホームにリダイレクト
        self.page.go("/")

    def go(self, route: str) -> None:
        """指定されたルートに遷移する。

        Args:
            route: 遷移先ルート
        """
        self.page.go(route)

    def can_go_back(self) -> bool:
        """戻ることができるかどうかを判定する。

        Returns:
            bool: 戻ることができる場合True
        """
        return len(self.page.views) > 1

    def go_back(self) -> bool:
        """前のビューに戻る。

        Returns:
            bool: 戻ることができた場合True
        """
        if self.can_go_back():
            self.page.views.pop()
            if self.page.views:
                top_view = self.page.views[-1]
                if top_view.route:
                    self.page.go(top_view.route)
                return True
        return False

    def refresh_current_view(self) -> None:
        """現在のビューを再読み込みする。"""
        if self._current_view:
            self._current_view.refresh()

    def clear_view_cache(self, view_class: type[BaseView] | None = None) -> None:
        """ビューキャッシュをクリアする。

        Args:
            view_class: クリアするビュークラス（Noneで全てクリア）
        """
        self._view_factory.clear_cache(view_class)

    def get_registered_routes(self) -> list[str]:
        """登録されているルートの一覧を取得する。

        Returns:
            list[str]: ルートパスのリスト
        """
        return list(self._routes.keys())

    def get_route_config(self, path: str) -> RouteConfig | None:
        """指定されたパスのルート設定を取得する。

        Args:
            path: ルートパス

        Returns:
            RouteConfig | None: ルート設定またはNone
        """
        return self._routes.get(path)


# ============================================================================
# ヘルパー関数とファクトリー
# ============================================================================


def create_route_config(
    path: str,
    view_class: type[BaseView],
    name: str = "",
    *,
    app_bar: ft.AppBar | None = None,
    requires_auth: bool = False,
) -> RouteConfig:
    """ルート設定を作成するヘルパー関数。

    Args:
        path: ルートパス
        view_class: ビュークラス
        name: ルート名
        app_bar: アプリケーションバー
        requires_auth: 認証が必要かどうか

    Returns:
        RouteConfig: ルート設定
    """
    return RouteConfig(
        path=path,
        view_class=view_class,
        name=name,
        app_bar=app_bar,
        requires_auth=requires_auth,
    )


# ============================================================================
# ミドルウェア例
# ============================================================================


def logging_middleware(e: ft.RouteChangeEvent) -> None:
    """ログ出力ミドルウェア。

    Args:
        e: ルート変更イベント
    """
    logger.info(f"ナビゲーション: {e.route}")


def analytics_middleware(e: ft.RouteChangeEvent) -> None:
    """アナリティクスミドルウェア。

    Args:
        e: ルート変更イベント
    """
    # [AI GENERATED] 実際のアナリティクス実装はここに
    logger.debug(f"アナリティクス: ページビュー {e.route}")


def performance_middleware(e: ft.RouteChangeEvent) -> None:
    """パフォーマンス測定ミドルウェア。

    Args:
        e: ルート変更イベント
    """
    import time

    start_time = time.time()
    # [AI GENERATED] ルート処理完了後に測定結果をログ出力
    # 実際の実装では、ルート処理完了のタイミングを適切に捕捉する
    logger.debug(f"ルート処理開始: {e.route} at {start_time}")
