import flet as ft
from loguru import logger
from sqlmodel import SQLModel

from config import APP_TITLE, engine
from logging_conf import setup_logger
from router import route_change

# ログの設定
setup_logger()
logger.info("アプリケーションを起動します。")

# DB初期化（全テーブル作成）
SQLModel.metadata.create_all(engine)


def main(page: ft.Page) -> None:
    """Fletアプリケーションのメイン関数。

    Args:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ページの初期設定
    page.title = APP_TITLE
    page.on_route_change = route_change
    page.go(page.route)

    logger.info("セッションが開始されました。")


# アプリ起動
ft.app(target=main)
