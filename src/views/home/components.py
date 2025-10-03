"""ホーム画面のコンポーネントモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from logic.factory import get_application_service_container
from logic.queries.one_liner_queries import build_one_liner_context_auto
from logic.services.one_liner_service import OneLinerService

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.application.task_application_service import TaskApplicationService


class MainActionSection(ft.Column):
    """メインアクションセクションコンポーネント.

    タスク管理ボタンと統計情報を表示するセクション。
    """

    def __init__(self, page: ft.Page, task_app_service: TaskApplicationService) -> None:
        """MainActionSectionの初期化.

        Args:
            page: Fletのページオブジェクト
            task_app_service: タスクアプリケーションサービスインスタンス
        """
        super().__init__()
        self._page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.task_app_service = task_app_service

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.ElevatedButton(
                text="タスク管理",
                icon=ft.Icons.TASK_ALT,
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    # bgcolor=ft.Colors.BLUE_600,
                    # color=ft.Colors.WHITE,
                    text_style=ft.TextStyle(size=16),
                ),
                on_click=self._navigate_to_tasks,
            ),
            TaskStatsCard(task_count=self.get_today_task_count()),
        ]

    def _navigate_to_tasks(self, _: ft.ControlEvent) -> None:
        """タスク画面への遷移処理.

        Args:
            _: イベントオブジェクト
        """
        self._page.go("/task")

    def get_today_task_count(self) -> int:
        """今日のタスク件数を取得.

        Returns:
            今日のタスク件数
        """
        from logic.queries.task_queries import GetTodayTasksCountQuery

        query = GetTodayTasksCountQuery()
        return self.task_app_service.get_today_tasks_count(query)


class TaskStatsCard(ft.Container):
    """タスク統計情報カードコンポーネント.

    今日のタスク件数などの統計情報を表示するカード。
    """

    def __init__(self, task_count: int = 0) -> None:
        """TaskStatsCardの初期化.

        Args:
            task_count: タスク件数
        """
        super().__init__()
        self.task_count = task_count
        self.width = 200

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "今日のタスク",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{self.task_count}件",
                            size=24,
                            # color=ft.Colors.BLUE_600,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            elevation=2,
        )

    def update_task_count(self, count: int) -> None:
        """タスク件数を更新.

        Args:
            count: 新しいタスク件数
        """
        self.task_count = count
        self._build_card()
        self.update()


class QuickActionCard(ft.Container):
    """クイックアクション用のカードコンポーネント.

    ホーム画面で使用する再利用可能なアクションカード。
    """

    def __init__(
        self,
        title: str,
        icon: str,
        description: str,
        on_click_handler: Callable | None = None,
    ) -> None:
        """QuickActionCardの初期化.

        Args:
            title: カードのタイトル
            icon: 表示するアイコン
            description: カードの説明文
            on_click_handler: クリック時のハンドラー関数
        """
        super().__init__()
        self.title = title
        self.icon = icon
        self.description = description
        self.on_click = on_click_handler

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=self.icon,
                            size=40,
                            # color=ft.Colors.BLUE_600,
                        ),
                        ft.Text(
                            self.title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            self.description,
                            size=12,
                            # color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=20,
                width=150,
                height=120,
            ),
            elevation=2,
        )


class WelcomeMessage(ft.Container):
    """AIからのアドバイスを表示するウェルカムメッセージコンポーネント."""

    def __init__(self, page: ft.Page) -> None:
        """WelcomeMessageの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__()
        self._page = page
        self.alignment = ft.alignment.center

        # 初期状態はプログレスリングを表示
        self.content = ft.ProgressRing()

        # AIからのメッセージを非同期で取得
        self._load_ai_message()

    def _load_ai_message(self) -> None:
        """AIからのメッセージを非同期で取得し、表示を更新."""
        import threading

        def fetch_message() -> None:
            """[AI GENERATED] AIサービスからメッセージを取得する処理"""
            try:
                service_factory = get_application_service_container()
                service = service_factory.get_service(OneLinerService)
                ai_text = service.generate(build_one_liner_context_auto())

                # UIスレッドでメッセージを更新
                self._update_message(ai_text)
            except Exception:
                # エラー時はデフォルトメッセージを表示
                self._update_message("今日も一日頑張りましょう！")

        # バックグラウンドスレッドでAIメッセージを取得
        thread = threading.Thread(target=fetch_message)
        thread.daemon = True
        thread.start()

    def _update_message(self, message: str) -> None:
        """メッセージを更新してUIを再描画.

        Args:
            message: 表示するメッセージ
        """
        self.content = ft.Text(
            message,
            size=18,
            # color=ft.Colors.GREY_700,
        )
        # ページを更新してUIに反映
        if self._page:
            self._page.update()
