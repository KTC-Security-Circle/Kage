import flet as ft
from sqlmodel import SQLModel

from config import APP_TITLE, engine
from router import route_change

# DB初期化（全テーブル作成）
SQLModel.metadata.create_all(engine)


def main(page: ft.Page) -> None:
    # ページの初期設定
    page.title = APP_TITLE
    page.on_route_change = route_change
    page.go(page.route)


# アプリ起動
ft.app(target=main)
