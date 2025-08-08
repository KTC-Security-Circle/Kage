"""ホーム画面のビューモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.home.components import MainActionSection, create_welcome_message
from views.shared import BaseView, ErrorHandlingMixin

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService


class HomeView(BaseView, ErrorHandlingMixin):
    """ホーム画面のメインビューコンポーネント

    タスク管理画面への遷移ボタンやダッシュボード情報を表示する。
    """

    def __init__(self, page: ft.Page) -> None:
        """HomeViewの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__(page)

        # 依存性注入
        self.task_app_service: TaskApplicationService = self.container.get_task_application_service()

    def build_content(self) -> ft.Control:
        """ホーム画面のコンテンツを構築

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        return ft.Column(
            [
                create_welcome_message(),
                MainActionSection(self.page, self.task_app_service),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            spacing=30,
        )

    def _navigate_to_tasks(self, _: ft.ControlEvent) -> None:
        """タスク画面への遷移処理

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/task")


def create_home_view(page: ft.Page) -> ft.Container:
    """ホーム画面ビューを作成する関数

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Container: 構築されたホーム画面ビュー
    """
    home_view = HomeView(page)
    home_view.mount()  # コンテンツを構築
    return home_view
