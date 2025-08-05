"""ホーム画面のビューモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from logic.factory import get_application_service_container
from views.home.components import MainActionSection, create_welcome_message

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService


class HomeView(ft.Column):
    """ホーム画面のメインビューコンポーネント.

    タスク管理画面への遷移ボタンやダッシュボード情報を表示する。
    """

    page: ft.Page

    def __init__(self, page: ft.Page, task_app_service: TaskApplicationService) -> None:
        """HomeViewの初期化.

        Args:
            page: Fletのページオブジェクト
            task_app_service: タスクアプリケーションサービス（依存性注入）
        """
        super().__init__()
        self.page = page
        self.task_app_service = task_app_service
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
            MainActionSection(self.page, self.task_app_service),
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
    # ✅ GOOD: Application Serviceを使用（Session管理不要）
    container = get_application_service_container()
    task_app_service = container.get_task_application_service()

    return ft.Container(
        content=HomeView(page, task_app_service),
        expand=True,
        bgcolor=ft.Colors.GREY_50,  # 背景色を設定
        padding=ft.padding.all(20),  # 全体のパディング
        alignment=ft.alignment.center,
    )
