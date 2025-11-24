"""Home View Layer.

【責務】
    View層はFletのUI描画とイベント配線のみに集中する。
    ロジックはController/Presenterに委譲する。

    - UIレイアウトの構築
    - イベントハンドラの配線
    - Controller経由でのデータ取得
    - Presenter経由でのUI要素生成

【責務外（他層の担当）】
    - データの取得・永続化 → Controller
    - 状態の保持 → State
    - UI要素の生成ロジック → Presenter

【アーキテクチャ上の位置づけ】
    User Event → View → Controller → State
                    ↓
                Presenter → UI Components

【設計上の特徴】
    - BaseViewを継承
    - Controller/Presenterを組み合わせた設計
    - 最小限のロジック（描画とイベント配線のみ）
"""

from __future__ import annotations

from typing import cast

import flet as ft
from loguru import logger

from logic.application.apps import ApplicationServicesError
from logic.application.memo_application_service import MemoApplicationService
from logic.application.one_liner_application_service import OneLinerApplicationService
from logic.application.project_application_service import ProjectApplicationService
from logic.application.task_application_service import TaskApplicationService
from views.shared.base_view import BaseView, BaseViewProps
from views.theme import SPACING

from .controller import HomeController
from .presenter import build_daily_review_card, build_inbox_memo_item, build_stat_card
from .query import ApplicationHomeQuery, HomeQuery, InMemoryHomeQuery
from .state import HomeViewState


class HomeView(BaseView):
    """ホーム画面のView。

    MVP+State+Query方式でリファクタリング済み。
    """

    def __init__(self, props: BaseViewProps, query: HomeQuery | None = None) -> None:
        """HomeViewを初期化する。

        Args:
            props: View共通プロパティ
            query: データ取得用Query（テスト時に注入可能）
        """
        super().__init__(props)

        # State/Controller の初期化
        self.state = HomeViewState()

        # Queryが指定されていない場合はApplicationService経由で生成
        if query is None:
            query = self._create_application_query()

        self.controller = HomeController(state=self.home_state, query=query)

        # 初期データ読み込み
        try:
            self.controller.load_initial_data()
        except ApplicationServicesError as e:
            # サービスが未登録 (テスト/軽量環境) の場合は Home を空の状態で表示する。
            # これは異常ではなく、INFOレベルで記録する。
            logger.info(
                "Application services unavailable for HomeView, falling back to empty data: {}",
                e,
            )
        except Exception:
            # 予期せぬエラーは従来通り再送出してUIに表示されるようにする
            raise

    def _create_application_query(self) -> ApplicationHomeQuery:
        """ApplicationServicesを利用したHomeQueryを生成する。"""
        try:
            memo_service = self.apps.get_service(MemoApplicationService)
            task_service = self.apps.get_service(TaskApplicationService)
            project_service = self.apps.get_service(ProjectApplicationService)
            one_liner_service = self.apps.get_service(OneLinerApplicationService)
            return ApplicationHomeQuery(
                memo_service=memo_service,
                task_service=task_service,
                project_service=project_service,
                one_liner_service=one_liner_service,
            )
        except Exception as e:
            # ApplicationServices が利用できない場合はエラーとして扱わず
            # デフォルトの空データ(HomeQueryのInMemory実装)を使う
            logger.info("HomeView: Application services missing, using InMemoryHomeQuery: {}", e)
            # InMemoryHomeQueryはHomeQueryProtocolを実装しているため、型的に安全
            return InMemoryHomeQuery()  # type: ignore[return-value]

    @property
    def home_state(self) -> HomeViewState:
        """Home専用Stateを取得する。"""
        return cast("HomeViewState", self.state)

    def build(self) -> ft.Control:
        """ホーム画面UIを構築する。

        Returns:
            構築されたコントロール
        """
        content_sections = [
            self._build_header(),
            ft.Container(height=SPACING.md),
            self._build_daily_review_section(),
        ]

        # Inboxメモセクションを追加（メモがある場合のみ）
        if self.home_state.has_inbox_memos():
            content_sections.extend(
                [
                    ft.Container(height=SPACING.lg),
                    self._build_inbox_memos_section(),
                ]
            )

        content_sections.extend(
            [
                ft.Container(height=SPACING.lg),
                self._build_stats_section(),
            ]
        )

        return ft.Container(
            content=ft.Column(
                content_sections,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=ft.padding.all(32),
            expand=True,
        )

    def _build_header(self) -> ft.Control:
        """ヘッダー部分を構築する。

        Returns:
            ヘッダーコントロール
        """
        return self.create_header(
            title="ホーム",
            subtitle="今日のタスクとプロジェクトの概要",
        )

    def _build_daily_review_section(self) -> ft.Control:
        """デイリーレビューセクションを構築する。

        Returns:
            デイリーレビューコントロール
        """
        return build_daily_review_card(self.home_state.daily_review, self._handle_action_click)

    def _build_inbox_memos_section(self) -> ft.Control:
        """Inboxメモセクションを構築する。

        Returns:
            Inboxメモセクションコントロール
        """
        memo_items = [build_inbox_memo_item(memo, self._handle_memo_click) for memo in self.home_state.inbox_memos[:3]]

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.AUTO_AWESOME, size=20, color=ft.Colors.BLUE_GREY_900),
                                    ft.Text(
                                        "Inboxメモ",
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                spacing=SPACING.xs,
                            ),
                            ft.TextButton(
                                text="すべて見る",
                                icon=ft.Icons.ARROW_FORWARD,
                                icon_color=ft.Colors.BLUE_GREY_900,
                                style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_900),
                                on_click=lambda _: self._handle_action_click("/memos"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        "整理が必要なメモがあります。AIにタスクを生成させましょう。",
                        size=14,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                    ),
                    ft.Column(
                        memo_items,
                        spacing=SPACING.xs,
                    ),
                ],
                spacing=SPACING.sm,
            ),
            padding=ft.padding.all(24),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)),
        )

    def _build_stats_section(self) -> ft.Control:
        """統計カード群を構築する。

        Returns:
            統計カードコントロール
        """
        stats_cards = [
            build_stat_card(
                "次のアクション",
                str(self.home_state.stats.get("todays_tasks", 0)),
                "件のタスク",
                ft.Icons.CHECK_BOX_OUTLINED,
                lambda: self._handle_action_click("/tasks"),
            ),
            build_stat_card(
                "インボックス",
                str(self.home_state.stats.get("todo_tasks", 0)),
                "未処理のタスク",
                ft.Icons.SCHEDULE,
                lambda: self._handle_action_click("/tasks"),
            ),
            build_stat_card(
                "進行中プロジェクト",
                str(self.home_state.stats.get("active_projects", 0)),
                "件のプロジェクト",
                ft.Icons.FOLDER_OPEN,
                lambda: self._handle_action_click("/projects"),
            ),
        ]

        return ft.ResponsiveRow(
            stats_cards,
            spacing=SPACING.md,
            run_spacing=SPACING.md,
        )

    def _handle_memo_click(self, memo_id: str) -> None:
        """メモクリック時の処理。

        Args:
            memo_id: クリックされたメモのID
        """
        from loguru import logger

        logger.info(f"Memo clicked: {memo_id}")
        self._handle_action_click("/memos")

    def _handle_action_click(self, route: str) -> None:
        """アクションクリック時の処理。

        Args:
            route: 遷移先ルート
        """
        try:
            if self.page:
                self.page.go(route)
        except Exception as e:
            from loguru import logger

            logger.error(f"Navigation error: {e}")
