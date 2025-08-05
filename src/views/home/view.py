"""ホーム画面のビューモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from sqlmodel import Session

from config import engine
from logic.factory import create_service_factory
from views.home.components import MainActionSection, create_welcome_message

if TYPE_CHECKING:
    from logic.services.task_service import TaskService


class HomeView(ft.Column):
    """ホーム画面のメインビューコンポーネント.

    タスク管理画面への遷移ボタンやダッシュボード情報を表示する。
    """

    page: ft.Page

    def __init__(self, page: ft.Page, task_service: TaskService) -> None:
        """HomeViewの初期化.

        Args:
            page: Fletのページオブジェクト
            task_service: タスクサービス（依存性注入）
        """
        super().__init__()
        self.page = page
        self.task_service = task_service
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
            MainActionSection(self.page, self.task_service),
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
    # 依存性注入を使用してサービスを作成
    session = Session(engine)
    service_factory = create_service_factory(session)
    task_service = service_factory.create_task_service()

    return ft.Container(
        content=HomeView(page, task_service),
        expand=True,
        bgcolor=ft.Colors.GREY_50,  # 背景色を設定
        padding=ft.padding.all(20),  # 全体のパディング
        alignment=ft.alignment.center,
    )
