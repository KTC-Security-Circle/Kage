import flet as ft
from loguru import logger

from config import APP_TITLE, create_db_and_tables
from env import setup_environment
from logging_conf import setup_logger
from router_config import setup_enhanced_routing

# 環境変数ファイルの作成
setup_environment()

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
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREY_700,
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # FletNativeRouterを使用したルーティング設定
    setup_enhanced_routing(page)

    logger.info("セッションが開始されました。")


ft.app(target=main, assets_dir="assets")
