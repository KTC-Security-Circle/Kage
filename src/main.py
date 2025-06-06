import flet as ft
from sqlmodel import SQLModel

from config import APP_TITLE, engine
from router import Router

# DB初期化（全テーブル作成）
SQLModel.metadata.create_all(engine)


def main(page: ft.Page) -> None:
    # ページの初期設定
    page.title = APP_TITLE
    Router(page)


ft.app(target=main, assets_dir="assets")
