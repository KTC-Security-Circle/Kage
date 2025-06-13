import flet as ft
from loguru import logger
from sqlmodel import SQLModel

from config import APP_TITLE, engine
from env import setup_environment
from logging_conf import setup_logger
from router import Router

# 環境変数ファイルの作成
setup_environment()

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
    Router(page)

    logger.info("セッションが開始されました。")


ft.app(target=main, assets_dir="assets")
