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

import threading
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

from .components import DailyReviewCard, InboxMemosSection, StatsCards
from .components.stats_cards import StatCardData
from .controller import HomeController
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

        # デイリーレビューカードへの参照（更新用）
        self._daily_review_card: DailyReviewCard | None = None

        # 初期データ読み込み(AI一言生成は除く)
        try:
            logger.info("[HomeView] 初期データ読み込み開始")
            self.controller.load_initial_data()
            logger.info("[HomeView] 初期データ読み込み完了")
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

        # AI一言生成をバックグラウンドで開始(起動をブロックしない)
        logger.info("[HomeView] AI一言生成をバックグラウンドで開始")
        self._start_one_liner_generation_async()
        logger.info("[HomeView] __init__完了（UI操作可能）")

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
        if self._daily_review_card is None:
            self._daily_review_card = DailyReviewCard(
                review=self.home_state.daily_review,
                on_action_click=self._handle_action_click,
                is_loading=self.home_state.is_loading_one_liner,
            )
        return self._daily_review_card

    def _rebuild_daily_review_card(self) -> None:
        """デイリーレビューカードを最新の状態で再構築する。

        State から最新のデータとローディング状態を取得し、カードを更新する。
        """
        if self._daily_review_card is None:
            logger.warning("[UI更新] デイリーレビューカード参照が未初期化です")
            return

        self._daily_review_card.update_review(
            self.home_state.daily_review,
            is_loading=self.home_state.is_loading_one_liner,
        )

    def _build_inbox_memos_section(self) -> ft.Control:
        """Inboxメモセクションを構築する。

        Returns:
            Inboxメモセクションコントロール
        """
        return InboxMemosSection(
            memos=self.home_state.inbox_memos,
            on_memo_click=self._handle_memo_click,
            on_see_all_click=lambda: self._handle_action_click("/memos"),
            max_display=3,
        )

    def _build_stats_section(self) -> ft.Control:
        """統計カード群を構築する。

        Returns:
            統計カードコントロール
        """
        stats = [
            StatCardData(
                title="次のアクション",
                value=str(self.home_state.stats.get("todays_tasks", 0)),
                subtitle="件のタスク",
                icon=ft.Icons.CHECK_BOX_OUTLINED,
                on_click=lambda: self._handle_action_click("/tasks"),
            ),
            StatCardData(
                title="インボックス",
                value=str(self.home_state.stats.get("todo_tasks", 0)),
                subtitle="未処理のタスク",
                icon=ft.Icons.SCHEDULE,
                on_click=lambda: self._handle_action_click("/tasks"),
            ),
            StatCardData(
                title="進行中プロジェクト",
                value=str(self.home_state.stats.get("active_projects", 0)),
                subtitle="件のプロジェクト",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda: self._handle_action_click("/projects"),
            ),
        ]

        return StatsCards(stats=stats)

    def _handle_memo_click(self, memo_id: str) -> None:
        """メモクリック時の処理。

        Args:
            memo_id: クリックされたメモのID
        """
        from loguru import logger

        logger.info(f"Memo clicked: {memo_id}")
        self._handle_action_click("/memos")

    def _start_one_liner_generation_async(self) -> None:
        """AI一言生成をバックグラウンドで開始する。

        別スレッドで実行し、完了時にUI更新を行う。
        """
        logger.info("[非同期] AI一言生成ローディング状態に設定")
        self.controller.start_loading_one_liner()

        def generate_and_update() -> None:
            import time

            start_time = time.time()
            logger.info("[非同期スレッド] AI一言生成開始")
            try:
                message = self.controller.generate_one_liner_sync()
                elapsed = time.time() - start_time
                msg_preview = message[:50] if message else "None"
                logger.info(f"[非同期スレッド] AI一言生成完了（{elapsed:.2f}秒）: {msg_preview}...")
                self.controller.set_one_liner_message(message)
                # [AI GENERATED] Flet のUI更新はメインスレッドで行う必要があるため、
                # バックグラウンドスレッドから直接UIを更新するのは推奨されません。
                # Flet公式のasyncパターン（page.run_task等）の利用を推奨します。
                logger.info("[非同期スレッド] UI更新開始")
                self._update_one_liner_display()
                logger.info("[非同期スレッド] UI更新完了")
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[非同期スレッド] AI一言生成失敗（{elapsed:.2f}秒）: {e}")
                self.controller.set_one_liner_message(None)

        thread = threading.Thread(target=generate_and_update, daemon=True)
        thread.start()
        logger.info(f"[非同期] バックグラウンドスレッド起動完了（Thread ID: {thread.ident}）")

    def _update_one_liner_display(self) -> None:
        """AI一言生成完了時にデイリーレビューカードを更新する。

        Stateから最新の状態を取得し、既存のCardを再構築して内容を置き換える。
        build()実行前の場合は状態のみ更新し、カード作成時に反映される。
        """
        try:
            logger.info(f"[UI更新] デイリーレビューカード更新開始（loading={self.home_state.is_loading_one_liner}）")

            # カード参照がまだない場合（build()実行前）は状態のみ更新して終了
            if self._daily_review_card is None:
                logger.info("[UI更新] カードが未作成のため状態のみ更新（build時に反映されます）")
                return

            # カード再構築を共通メソッドに委譲
            self._rebuild_daily_review_card()

            # UI更新を実行
            try:
                if getattr(self._daily_review_card, "page", None) is not None:
                    self._daily_review_card.update()
                    logger.info("[UI更新] デイリーレビューカード更新完了 (control.update)")
                elif self.page is not None:
                    self.page.update()
                    logger.info("[UI更新] デイリーレビューカード更新完了 (page.update fallback)")
                else:
                    logger.warning("[UI更新] page が見つからないため更新をスキップ")
            except Exception as ex:
                logger.error(f"[UI更新] 個別更新に失敗したため page.update にフォールバックします: {ex}")
                if self.page is not None:
                    self.page.update()
                    logger.info("[UI更新] page.update による再描画完了")
        except Exception as e:
            logger.error(f"[UI更新] AI一言表示の更新に失敗しました: {e}")

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
