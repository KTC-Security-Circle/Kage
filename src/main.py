import flet as ft
from loguru import logger

from config import APP_TITLE, create_db_and_tables
from logging_conf import setup_logger
from router_config import setup_enhanced_routing
from settings.manager import apply_page_settings, get_config_manager  # [AI GENERATED] 設定管理を追加

# ログの設定
setup_logger()
logger.info("アプリケーションを起動します。")

# DB初期化（全テーブル作成）
create_db_and_tables()


def main(page: ft.Page) -> None:
    """Fletアプリケーションのメイン関数。

    Args:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ページの初期設定
    page.title = APP_TITLE
    # 設定ファイル読み込み（初期生成含む）
    get_config_manager()
    # 設定適用（テーマ等）
    apply_page_settings(page)
    page.padding = 0
    page.fonts = {
        "default": "/fonts/BIZ_UDGothic/BIZUDGothic-Regular.ttf",
        "bold": "/fonts/BIZ_UDGothic/BIZUDGothic-Bold.ttf",
    }
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREY_700,
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            android=ft.PageTransitionTheme.NONE,
        ),
        font_family="default",
    )

    # FletNativeRouterを使用したルーティング設定
    setup_enhanced_routing(page)

    logger.info("セッションが開始されました。設定適用済み。")


ft.app(target=main, assets_dir="assets")
