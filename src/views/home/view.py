"""ホーム画面のビューモジュール."""

from __future__ import annotations

import flet as ft

from views.home.components import MainActionSection, create_welcome_message


class HomeView(ft.Column):
    """ホーム画面のメインビューコンポーネント.

    タスク管理画面への遷移ボタンやダッシュボード情報を表示する。
    """

    page: ft.Page

    def __init__(self, page: ft.Page) -> None:
        """HomeViewの初期化.

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__()
        self.page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True
        self.spacing = 30

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            create_welcome_message(),
            MainActionSection(self.page),
        ]

    def _navigate_to_tasks(self, _: ft.ControlEvent) -> None:
        """タスク画面への遷移処理.

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/task")


def create_home_view(page: ft.Page) -> ft.Container:
    """ホーム画面ビューを作成する関数.

    Args:
        page: Fletのページオブジェクト

    Returns:
        構築されたホーム画面ビュー
    """
    return ft.Container(
        content=HomeView(page),
        expand=True,
        bgcolor=ft.colors.GREY_50,  # 背景色を設定
        padding=ft.padding.all(20),  # 全体のパディング
        alignment=ft.alignment.center,
    )
