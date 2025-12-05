"""週次レビュービュー実装（ウィザード形式）

GTD週次レビューの3ステップウィザード画面実装。
Step1: 成果の振り返り
Step2: システムの整理
Step3: 来週の計画
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.shared.base_view import BaseView, BaseViewProps

from .components import (
    AchievementHeader,
    AchievementHeaderProps,
    CompletedTaskItemData,
    CompletedTasksList,
    CompletedTasksListProps,
    CompletionCard,
    CompletionCardProps,
    EmptyStateCard,
    EmptyStateCardProps,
    HighlightsCard,
    HighlightsCardProps,
    MemoAction,
    RecommendationCard,
    RecommendationCardProps,
    StepIndicator,
    StepIndicatorProps,
    UnprocessedMemoCard,
    UnprocessedMemoCardProps,
    UnprocessedMemoData,
    WizardNavigation,
    WizardNavigationProps,
    ZombieTaskAction,
    ZombieTaskCard,
    ZombieTaskCardProps,
    ZombieTaskData,
)
from .controller import WeeklyReviewController
from .presenter import WeeklyReviewPresenter
from .state import WeeklyReviewState

if TYPE_CHECKING:
    from logic.application.memo_application_service import MemoApplicationService
    from logic.application.review_application_service import WeeklyReviewApplicationService
    from logic.application.task_application_service import TaskApplicationService

# View step constants
STEP_ACHIEVEMENT = 1
STEP_CLEANUP = 2
STEP_PLANNING = 3


class WeeklyReviewView(BaseView):
    """週次レビューのメインビュー（ウィザード形式）

    Controller/Presenter/State パターンで構築。
    """

    def __init__(self, props: BaseViewProps) -> None:
        """ビューを初期化

        Args:
            props: ビュー共通プロパティ
        """
        super().__init__(props)

        # 依存性注入
        self.task_app_service: TaskApplicationService = props.apps.task
        self.review_app_service: WeeklyReviewApplicationService = props.apps.review
        self.memo_app_service: MemoApplicationService = props.apps.memo

        # 状態・コントローラー・プレゼンター初期化
        self.review_state = WeeklyReviewState()
        self.controller = WeeklyReviewController(
            task_app_service=self.task_app_service,
            review_app_service=self.review_app_service,
            memo_app_service=self.memo_app_service,
            state=self.review_state,
        )
        self.presenter = WeeklyReviewPresenter(state=self.review_state)

        # UIコンポーネント
        self.step_indicator: StepIndicator | None = None
        self.wizard_navigation: WizardNavigation | None = None
        self.step_content_container: ft.Container | None = None
        self.body_container: ft.Container | None = None

    def build_content(self) -> ft.Control:
        """メインコンテンツを構築"""
        header = self._build_header()
        body = self._render_flow_content()

        if self.body_container is None:
            self.body_container = ft.Container(expand=True, content=body)
        else:
            self.body_container.content = body

        content = ft.Column(
            controls=[
                header,
                ft.Container(height=16),
                self.body_container,
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.did_mount()
        return content

    def _build_header(self) -> ft.Control:
        """ヘッダーを構築

        Returns:
            ヘッダーコントロール
        """
        return self.create_header(
            title="週次レビュー",
            subtitle="AIがサポートする週次レビュー - 事務作業はAI、意思決定は人間",
            show_search=False,
        )

    def _render_flow_content(self) -> ft.Control:
        """現在の状態に応じて表示するコンテンツを切り替える。"""
        if not self.review_state.has_started:
            return self._render_start_page()
        if not self.review_state.data_loaded:
            return self._render_loading_view()
        return self._render_wizard_content()

    def _render_start_page(self) -> ft.Control:
        """開始前のスタート画面を構築する。"""
        bullet_points = [
            "成果・課題をAIが集計して要約",
            "ゾンビタスクと未処理メモを自動抽出",
            "次週に向けた推奨アクションを提示",
        ]
        bullet_controls = [
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.BLUE_400, size=20),
                    ft.Text(point, size=14),
                ],
                spacing=8,
            )
            for point in bullet_points
        ]

        start_button = ft.ElevatedButton(
            text="AIレビューを開始",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._handle_start_button,
            height=48,
            width=220,
        )

        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("週次レビューを開始", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "1週間の記録をAIが整理し、次のアクションづくりを支援します。",
                            size=14,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Column(controls=bullet_controls, spacing=8),
                        ft.Container(height=8),
                        start_button,
                    ],
                    spacing=16,
                ),
                padding=ft.padding.all(24),
                expand=True,
            ),
            elevation=3,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("AIが週次レビューを実行します", size=16, color=ft.Colors.GREY_600),
                    card,
                ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _render_loading_view(self) -> ft.Control:
        """AI集計中のローディングビューを構築する。"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(width=64, height=64),
                    ft.Text("AIが週次レビューを準備しています...", size=16),
                    ft.Text(
                        "数十秒かかる場合があります。アプリを閉じずにお待ちください。",
                        size=13,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                        width=320,
                    ),
                ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _render_wizard_content(self) -> ft.Control:
        """本来のウィザードUIを構築する。"""
        self.step_indicator = StepIndicator(
            props=StepIndicatorProps(
                current_step=self.review_state.current_step,
                total_steps=self.review_state.total_steps,
                step_labels=self.presenter.get_step_labels(),
            )
        )
        self.step_content_container = ft.Container(
            content=self._render_current_step(),
            expand=True,
        )
        self.wizard_navigation = WizardNavigation(
            props=WizardNavigationProps(
                current_step=self.review_state.current_step,
                total_steps=self.review_state.total_steps,
                on_prev=self._handle_prev_step,
                on_next=self._handle_next_step,
            )
        )

        return ft.Column(
            controls=[
                self.step_indicator,
                ft.Divider(),
                ft.Container(height=8),
                self.step_content_container,
                ft.Container(height=8),
                ft.Divider(),
                self.wizard_navigation,
            ],
            spacing=0,
            expand=True,
        )

    def _render_current_step(self) -> ft.Control:
        """現在のステップコンテンツをレンダリング

        Returns:
            ステップコンテンツ
        """
        step = self.review_state.current_step

        if step == STEP_ACHIEVEMENT:
            return self._render_step1_achievement()
        if step == STEP_CLEANUP:
            return self._render_step2_cleanup()
        if step == STEP_PLANNING:
            return self._render_step3_planning()
        return ft.Container()

    def _build_step_header(
        self,
        title: str,
        subtitle: str,
        icon_name: str,
        icon_color: str,
    ) -> ft.Container:
        """ステップヘッダーを構築

        Args:
            title: ヘッダータイトル
            subtitle: サブタイトル
            icon_name: アイコン名
            icon_color: アイコンカラー

        Returns:
            構築されたヘッダーコンテナ
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            name=icon_name,
                            size=48,
                            color=icon_color,
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=f"{icon_color}1A",
                        border_radius=50,
                    ),
                    ft.Container(height=16),
                    ft.Text(
                        title,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        subtitle,
                        size=16,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=24),
        )

    def _render_step1_achievement(self) -> ft.Control:
        """Step1: 成果の振り返りをレンダリング

        Returns:
            Step1コンテンツ
        """
        # ヘッダー
        summary_message = self.presenter.generate_achievement_summary_message()
        header = AchievementHeader(
            props=AchievementHeaderProps(
                message=summary_message,
                icon_name=ft.Icons.CELEBRATION,
                icon_color=ft.Colors.BLUE_600,
            )
        )

        controls: list[ft.Control] = [header, ft.Container(height=24)]

        # ハイライトカード (データがあれば)
        if self.review_state.achievement_highlights:
            highlights_card = HighlightsCard(
                props=HighlightsCardProps(
                    highlights=self.review_state.achievement_highlights,
                    title="主な成果",
                    icon_name=ft.Icons.TRENDING_UP,
                    icon_color=ft.Colors.BLUE_600,
                )
            )
            controls.append(highlights_card)
            controls.append(ft.Container(height=16))

        # 完了タスクリスト (データがあれば)
        if self.review_state.completed_tasks_this_week:
            # タスクデータをコンポーネント用に変換
            completed_task_data = [
                CompletedTaskItemData(
                    task_id=str(task.id),
                    title=task.title,
                    # TODO: TaskReadモデルにprojectリレーション(project_id, project_title)を追加し、
                    # task.project.titleで取得。または、TaskApplicationService.get_task_with_project()
                    # メソッドを実装してプロジェクト情報を含めて取得
                    project_title=None,
                )
                for task in self.review_state.completed_tasks_this_week
            ]

            completed_list = CompletedTasksList(
                props=CompletedTasksListProps(
                    tasks=completed_task_data,
                    on_task_click=self._handle_task_click,
                    max_display=10,
                )
            )
            controls.append(completed_list)

        return ft.Column(
            controls=controls,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )

    def _render_step2_cleanup(self) -> ft.Control:
        """Step2: システムの整理をレンダリング

        Returns:
            Step2コンテンツ
        """
        # ヘッダー
        header_container = self._build_step_header(
            title="システムの整理",
            subtitle="AIが気になる項目をピックアップしました。それぞれについて判断をお願いします。",
            icon_name=ft.Icons.AUTO_AWESOME,
            icon_color=ft.Colors.YELLOW_700,
        )

        controls: list[ft.Control] = [header_container, ft.Container(height=24)]

        total_items = len(self.review_state.zombie_tasks) + len(self.review_state.unprocessed_memos)

        if total_items == 0:
            # 整理項目なし
            empty_card = EmptyStateCard(
                props=EmptyStateCardProps(
                    title="素晴らしい！",
                    message="整理が必要な項目はありません。システムは良好な状態です。",
                    icon_name=ft.Icons.CHECK_CIRCLE,
                    icon_color=ft.Colors.GREEN_600,
                )
            )
            controls.append(empty_card)
        else:
            # ゾンビタスクセクション
            if self.review_state.zombie_tasks:
                zombie_header = ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.WARNING_AMBER,
                            size=20,
                            color=ft.Colors.YELLOW_700,
                        ),
                        ft.Text(
                            f"長期滞留タスク ({len(self.review_state.zombie_tasks)}件)",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=8,
                )
                controls.append(zombie_header)
                controls.append(ft.Container(height=12))

                for task in self.review_state.zombie_tasks:
                    reason_text = task.reason or "停滞中のタスクです"
                    zombie_data = ZombieTaskData(
                        task_id=task.id,
                        title=task.title,
                        reason=reason_text,
                        selected_action=self.review_state.get_zombie_task_decision(task.id),
                    )
                    zombie_card = ZombieTaskCard(
                        props=ZombieTaskCardProps(
                            task_data=zombie_data,
                            on_action_selected=self._handle_zombie_task_action,
                        )
                    )
                    controls.append(zombie_card)
                    controls.append(ft.Container(height=12))

            # 未処理メモセクション
            if self.review_state.unprocessed_memos:
                memo_header = ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.DESCRIPTION,
                            size=20,
                            color=ft.Colors.BLUE_700,
                        ),
                        ft.Text(
                            f"未処理メモ ({len(self.review_state.unprocessed_memos)}件)",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=8,
                )
                controls.append(memo_header)
                controls.append(ft.Container(height=12))

                for memo in self.review_state.unprocessed_memos:
                    suggestion_text = memo.suggestion or self.presenter.generate_memo_analysis(
                        memo.content,
                        memo.title,
                    )
                    memo_data = UnprocessedMemoData(
                        memo_id=memo.id,
                        title=memo.title,
                        content=memo.content,
                        suggestion=suggestion_text,
                        selected_action=self.review_state.get_memo_decision(memo.id),
                    )
                    memo_card = UnprocessedMemoCard(
                        props=UnprocessedMemoCardProps(
                            memo_data=memo_data,
                            on_action_selected=self._handle_memo_action,
                        )
                    )
                    controls.append(memo_card)
                    controls.append(ft.Container(height=12))

        return ft.Column(
            controls=controls,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )

    def _render_step3_planning(self) -> ft.Control:
        """Step3: 来週の計画をレンダリング

        Returns:
            Step3コンテンツ
        """
        # ヘッダー
        header_container = self._build_step_header(
            title="次週のプランニング",
            subtitle="AIが来週注力すべき項目を提案します。承認または調整してください。",
            icon_name=ft.Icons.CALENDAR_TODAY,
            icon_color=ft.Colors.GREEN_700,
        )

        controls: list[ft.Control] = [header_container, ft.Container(height=24)]

        if not self.review_state.recommendations:
            # 推奨事項なし
            empty_card = EmptyStateCard(
                props=EmptyStateCardProps(
                    title="すべて順調です！",
                    message="特に緊急性の高いタスクはありません。新しいチャレンジに取り組む良い機会です。",
                    icon_name=ft.Icons.CHECK_CIRCLE,
                    icon_color=ft.Colors.BLUE_600,
                )
            )
            controls.append(empty_card)
        else:
            # 推奨事項カード
            for recommendation in self.review_state.recommendations:
                rec_card = RecommendationCard(
                    props=RecommendationCardProps(
                        recommendation=recommendation,
                        on_task_click=self._handle_task_click,
                    )
                )
                controls.append(rec_card)
                controls.append(ft.Container(height=16))

        # 完了カード
        controls.append(ft.Container(height=8))
        completion_card = CompletionCard(
            props=CompletionCardProps(
                title="レビュー完了",
                message="今週も良い1週間にしていきましょう!",
                on_finish=self._handle_complete_review,
            )
        )
        controls.append(completion_card)

        return ft.Column(
            controls=controls,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )

    def _handle_start_button(self, _: ft.ControlEvent) -> None:
        """スタートボタン押下時の処理。"""
        if self.state.loading:
            return
        if self.review_state.data_loaded:
            return

        self.review_state.has_started = True
        self.review_state.data_loaded = False
        self._refresh_flow_content()

        def _load() -> None:
            """レビュー初期データの読み込みと完了後の状態更新を一括で行う。"""
            try:
                self.controller.load_initial_data()
                # 成功時: 読み込み完了フラグを立て、UIを更新
                self.review_state.data_loaded = True
                self._refresh_flow_content()
                self._refresh_wizard()
            except Exception as e:
                # 失敗時: 開始状態を巻き戻してスタート画面へ復帰
                logger.exception("週次レビューデータの取得に失敗")
                self.notify_error(f"エラーが発生しました: {type(e).__name__}")
                self.review_state.has_started = False
                self._refresh_flow_content()

        # 非同期実行であっても、完了後の状態更新は _load 内で行う
        self.with_loading(_load, user_error_message="週次レビューデータの取得に失敗しました")

    def _handle_prev_step(self) -> None:
        """前のステップへ戻る"""
        try:
            self.controller.prev_step()
            self._refresh_wizard()
        except Exception as e:
            logger.exception("前のステップへの遷移に失敗")
            self.notify_error(f"エラーが発生しました: {type(e).__name__}")

    def _handle_next_step(self) -> None:
        """次のステップへ進む"""
        try:
            if self.review_state.current_step == self.review_state.total_steps:
                # 最終ステップなら完了処理
                self._handle_complete_review()
            else:
                self.controller.next_step()
                self._refresh_wizard()
        except Exception as e:
            logger.exception("次のステップへの遷移に失敗")
            self.notify_error(f"エラーが発生しました: {type(e).__name__}")

    def _handle_zombie_task_action(self, task_id: str, action: ZombieTaskAction) -> None:
        """ゾンビタスクのアクション選択処理

        Args:
            task_id: タスクID
            action: 選択されたアクション
        """
        try:
            self.controller.set_zombie_task_decision(task_id, action)
            logger.info(f"ゾンビタスクアクション選択: {task_id} -> {action}")
        except Exception as e:
            logger.exception("ゾンビタスクアクション選択に失敗")
            self.notify_error(f"エラーが発生しました: {type(e).__name__}")

    def _handle_memo_action(self, memo_id: str, action: MemoAction) -> None:
        """メモアクション選択処理

        Args:
            memo_id: メモID
            action: 選択されたアクション
        """
        try:
            self.controller.set_memo_decision(memo_id, action)
            logger.info(f"メモアクション選択: {memo_id} -> {action}")
        except Exception as e:
            logger.exception("メモアクション選択に失敗")
            self.notify_error(f"エラーが発生しました: {type(e).__name__}")

    def _handle_task_click(self, task_id: str) -> None:
        """タスククリック処理

        Args:
            task_id: タスクID
        """
        self.page.go(f"/tasks/{task_id}")

    def _handle_complete_review(self) -> None:
        """レビュー完了処理"""
        self.show_info_snackbar("レビューを完了しました！")
        self.page.go("/")

    def _refresh_flow_content(self) -> None:
        """スタート/ローディング/ウィザード表示を最新にする。"""
        if not self.body_container:
            return
        self.body_container.content = self._render_flow_content()
        self.safe_update()

    def _refresh_wizard(self) -> None:
        """ウィザード全体をリフレッシュ"""
        # ステップインジケーター更新
        if self.step_indicator:
            self.step_indicator.set_props(
                StepIndicatorProps(
                    current_step=self.review_state.current_step,
                    total_steps=self.review_state.total_steps,
                    step_labels=self.presenter.get_step_labels(),
                )
            )

        # コンテンツ更新
        if self.step_content_container:
            self.step_content_container.content = self._render_current_step()

        # ナビゲーション更新
        if self.wizard_navigation:
            self.wizard_navigation.set_props(
                WizardNavigationProps(
                    current_step=self.review_state.current_step,
                    total_steps=self.review_state.total_steps,
                    on_prev=self._handle_prev_step,
                    on_next=self._handle_next_step,
                )
            )

        # ページ更新
        if self.page:
            self.page.update()

    def did_mount(self) -> None:
        """マウント時の初期化"""
        super().did_mount()
        logger.info("週次レビュービューをマウントしました。ユーザー操作待ちです。")
