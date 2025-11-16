"""週次レビュービュー実装

GTD週次レビューの画面実装。
"""

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.shared.base_view import BaseView, BaseViewProps

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService


from .components import (
    AlertCard,
    AlertCardProps,
    ReviewChecklist,
    ReviewChecklistProps,
    StatsCard,
    StatsCardProps,
    TaskListCard,
    TaskListCardProps,
)
from .controller import WeeklyReviewController
from .presenter import WeeklyReviewPresenter
from .state import WeeklyReviewState


class WeeklyReviewView(BaseView):
    """週次レビューのメインビュー

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

        # 状態・コントローラー・プレゼンター初期化
        self.review_state = WeeklyReviewState()
        self.controller = WeeklyReviewController(
            task_app_service=self.task_app_service,
            state=self.review_state,
        )
        self.presenter = WeeklyReviewPresenter(state=self.review_state)

        # UIコンポーネント
        self.stats_cards: list[StatsCard] = []
        self.checklist_component: ReviewChecklist | None = None
        self.alert_card: AlertCard | None = None
        self.next_tasks_card: TaskListCard | None = None
        self.waiting_tasks_card: TaskListCard | None = None
        self.someday_tasks_card: TaskListCard | None = None

    def build_content(self) -> ft.Control:
        """メインコンテンツを構築

        Returns:
            構築されたコンテンツ
        """
        # ヘッダー
        header = self._build_header()

        # 統計カード行
        stats_row = self._build_stats_row()

        # メインコンテンツエリア（3カラム）
        main_content = ft.Row(
            controls=[
                # 左カラム: チェックリストとアラート
                ft.Column(
                    controls=[
                        self._build_checklist(),
                        self._build_alert_if_needed(),
                    ],
                    spacing=16,
                    expand=2,
                ),
                # 右カラム: タスクリスト
                ft.Column(
                    controls=[
                        self._build_next_tasks_card(),
                        self._build_waiting_tasks_card(),
                        self._build_someday_tasks_card(),
                    ],
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                    expand=1,
                ),
            ],
            spacing=16,
            expand=True,
        )

        # アクションボタン
        actions = self._build_actions()

        return ft.Column(
            controls=[
                header,
                ft.Container(height=20),
                stats_row,
                ft.Container(height=20),
                main_content,
                ft.Container(height=20),
                ft.Divider(),
                ft.Container(height=10),
                actions,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_header(self) -> ft.Container:
        """ヘッダーを構築

        Returns:
            ヘッダーコンテナ
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "週次レビュー",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "GTDの週次レビュー - システム全体を見直して整理する時間",
                                size=16,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(24),
        )

    def _build_stats_row(self) -> ft.ResponsiveRow:
        """統計カード行を構築

        Returns:
            統計カード行
        """
        stats_data = self.presenter.create_stats_cards_data()
        self.stats_cards = [
            StatsCard(
                props=StatsCardProps(
                    title=data.title,
                    value=data.value,
                    subtitle=data.subtitle,
                    icon_name=data.icon_name,
                )
            )
            for data in stats_data
        ]

        # ResponsiveRowで4カラムグリッドを実現
        for card in self.stats_cards:
            card.col = {"sm": 12, "md": 6, "lg": 3}

        return ft.ResponsiveRow(
            controls=self.stats_cards,
            spacing=16,
        )

    def _build_checklist(self) -> ft.Container:
        """チェックリストを構築

        Returns:
            チェックリストコンテナ
        """
        checklist_data = self.presenter.create_checklist_data()
        self.checklist_component = ReviewChecklist(
            props=ReviewChecklistProps(
                items=checklist_data,
                on_toggle=self._handle_checklist_toggle,
            )
        )
        return ft.Container(content=self.checklist_component, expand=True)

    def _build_alert_if_needed(self) -> ft.Container:
        """必要に応じてアラートカードを構築

        Returns:
            アラートカードコンテナ（不要な場合は空）
        """
        alert_message = self.presenter.get_inbox_alert_message()
        if not alert_message:
            return ft.Container()

        self.alert_card = AlertCard(
            props=AlertCardProps(
                title="要整理",
                message=alert_message,
                action_label="タスクを整理する",
                icon_name=ft.Icons.INBOX,
                on_action=self._handle_goto_tasks,
            )
        )
        return ft.Container(content=self.alert_card)

    def _build_next_tasks_card(self) -> ft.Container:
        """次のアクションタスクカードを構築

        Returns:
            タスクリストカードコンテナ
        """
        tasks = self.controller.get_tasks_by_status("next")
        task_data = self.presenter.create_task_list_data(tasks)

        self.next_tasks_card = TaskListCard(
            props=TaskListCardProps(
                title="次のアクション",
                icon_name=ft.Icons.CHECK_CIRCLE,
                tasks=task_data,
                on_task_click=self._handle_task_click,
                on_show_more=self._handle_goto_tasks,
            )
        )
        return ft.Container(content=self.next_tasks_card)

    def _build_waiting_tasks_card(self) -> ft.Container:
        """待機中タスクカードを構築

        Returns:
            タスクリストカードコンテナ
        """
        tasks = self.controller.get_tasks_by_status("waiting")
        task_data = self.presenter.create_task_list_data(tasks)

        self.waiting_tasks_card = TaskListCard(
            props=TaskListCardProps(
                title="待機中",
                icon_name=ft.Icons.SCHEDULE,
                tasks=task_data,
                on_task_click=self._handle_task_click,
                on_show_more=self._handle_goto_tasks,
            )
        )
        return ft.Container(content=self.waiting_tasks_card)

    def _build_someday_tasks_card(self) -> ft.Container:
        """いつか/多分タスクカードを構築

        Returns:
            タスクリストカードコンテナ
        """
        tasks = self.controller.get_tasks_by_status("someday")
        task_data = self.presenter.create_task_list_data(tasks)

        self.someday_tasks_card = TaskListCard(
            props=TaskListCardProps(
                title="いつか/多分",
                icon_name=ft.Icons.CALENDAR_MONTH,
                tasks=task_data,
                on_task_click=self._handle_task_click,
                on_show_more=self._handle_goto_tasks,
            )
        )
        return ft.Container(content=self.someday_tasks_card)

    def _build_actions(self) -> ft.Container:
        """アクションボタン行を構築

        Returns:
            アクションボタンコンテナ
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.OutlinedButton(
                        text="タスクを整理する",
                        on_click=lambda _: self._handle_goto_tasks(),
                    ),
                    ft.OutlinedButton(
                        text="プロジェクトを確認",
                        on_click=lambda _: self._handle_goto_projects(),
                    ),
                    ft.ElevatedButton(
                        text="レビュー完了",
                        on_click=lambda _: self._handle_complete_review(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.padding.all(24),
        )

    def _handle_checklist_toggle(self, item_id: str) -> None:
        """チェックリスト項目のトグル処理

        Args:
            item_id: 項目ID
        """
        try:
            self.controller.toggle_checklist_item(item_id)
            self._update_checklist()
        except Exception:
            logger.exception("チェックリスト更新に失敗")
            self.notify_error("チェックリスト更新に失敗しました")

    def _handle_start_wizard(self, _: ft.ControlEvent) -> None:
        """ウィザード開始処理

        Args:
            _: イベント
        """
        logger.info("レビューウィザードを開始（未実装）")
        self.show_info_snackbar("ウィザード機能は近日公開予定です")

    def _handle_task_click(self, task_id: str) -> None:
        """タスククリック処理

        Args:
            task_id: タスクID
        """
        self.page.go(f"/tasks/{task_id}")

    def _handle_goto_tasks(self) -> None:
        """タスク画面への遷移"""
        self.page.go("/tasks")

    def _handle_goto_projects(self) -> None:
        """プロジェクト画面への遷移"""
        self.page.go("/projects")

    def _handle_complete_review(self) -> None:
        """レビュー完了処理"""
        self.page.go("/home")

    def _update_checklist(self) -> None:
        """チェックリストを更新"""
        if self.checklist_component:
            checklist_data = self.presenter.create_checklist_data()
            self.checklist_component.update_items(checklist_data)

    def did_mount(self) -> None:
        """マウント時の初期化"""
        super().did_mount()
        try:
            self.controller.load_initial_data()
            self._refresh_all()
        except Exception:
            logger.exception("初期データ読み込みに失敗")
            self.notify_error("データの読み込みに失敗しました")

    def _refresh_all(self) -> None:
        """全コンポーネントをリフレッシュ"""
        # 統計カード更新
        stats_data = self.presenter.create_stats_cards_data()
        for i, card in enumerate(self.stats_cards):
            if i < len(stats_data):
                data = stats_data[i]
                card.set_props(
                    StatsCardProps(
                        title=data.title,
                        value=data.value,
                        subtitle=data.subtitle,
                        icon_name=data.icon_name,
                    )
                )

        # チェックリスト更新
        self._update_checklist()

        # ページ更新
        if self.page:
            self.page.update()
