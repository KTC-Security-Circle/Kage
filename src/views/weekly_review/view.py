"""Weekly review view implementation."""

from datetime import datetime, timedelta

import flet as ft

from views.shared.base_view import BaseView

from .components.review_components import (
    ProductivityInsights,
    ReflectionCard,
    TaskCompletionChart,
    WeeklyStatsCard,
)

# ReviewWizardは一時的に無効化
# from .components.review_wizard import ReviewWizard


class WeeklyReviewView(BaseView):
    """Main view for weekly retrospective and planning."""

    def __init__(self, page: ft.Page) -> None:
        """Initialize weekly review view.

        Args:
            page: Flet page instance
        """
        super().__init__(page)
        self.title = "週次振り返り"
        self.description = "今週の振り返りと来週の計画"

        # View state
        self.show_wizard = False
        self.current_week = self._get_current_week()

        # Components
        self.main_content: ft.Container | None = None
        self.wizard_container: ft.Container | None = None

    def build_content(self) -> ft.Control:
        """Build the main content area."""
        if self.show_wizard:
            return self._build_wizard_view()
        return self._build_dashboard_view()

    def _build_dashboard_view(self) -> ft.Control:
        """Build the main dashboard view."""
        # Header with week info
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        self.title,
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{self.current_week} • {self.description}",
                                        size=16,
                                        color=ft.Colors.OUTLINE,
                                    ),
                                ],
                                spacing=4,
                            ),
                            ft.ElevatedButton(
                                text="振り返りを開始",
                                icon=ft.Icons.PSYCHOLOGY,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.PRIMARY,
                                    color=ft.Colors.ON_PRIMARY,
                                ),
                                on_click=self._start_review_wizard,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
            ),
            padding=ft.padding.all(24),
        )

        # Stats cards row
        stats_row = ft.Row(
            controls=[
                WeeklyStatsCard(
                    title="完了タスク",
                    value="47",
                    subtitle="今週",
                    icon=ft.Icons.CHECK_CIRCLE,
                    color=ft.Colors.GREEN,
                    trend="↑ 15%",
                ),
                WeeklyStatsCard(
                    title="集中時間",
                    value="28.5h",
                    subtitle="深い作業",
                    icon=ft.Icons.ACCESS_TIME,
                    color=ft.Colors.BLUE,
                    trend="↑ 3.2h",
                ),
                WeeklyStatsCard(
                    title="達成率",
                    value="87%",
                    subtitle="目標達成",
                    icon=ft.Icons.TRENDING_UP,
                    color=ft.Colors.PURPLE,
                    trend="↑ 12%",
                ),
                WeeklyStatsCard(
                    title="新しい学び",
                    value="5",
                    subtitle="記録された気づき",
                    icon=ft.Icons.LIGHTBULB,
                    color=ft.Colors.AMBER,
                    trend="+2",
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        # Main content grid
        content_grid = ft.Row(
            controls=[
                # Left column - Charts and insights
                ft.Column(
                    controls=[
                        TaskCompletionChart(),
                        ft.Container(height=20),
                        ProductivityInsights(),
                    ],
                    expand=2,
                    spacing=16,
                ),
                # Right column - Reflection
                ft.Column(
                    controls=[
                        ReflectionCard(
                            on_save_reflection=self._handle_save_reflection,
                        ),
                        ft.Container(height=20),
                        self._build_previous_reviews(),
                    ],
                    expand=1,
                    spacing=16,
                ),
            ],
            spacing=24,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        return ft.Column(
            controls=[
                header,
                ft.Container(
                    content=stats_row,
                    padding=ft.padding.symmetric(horizontal=24),
                ),
                ft.Container(height=20),
                ft.Container(
                    content=content_grid,
                    padding=ft.padding.symmetric(horizontal=24),
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_wizard_view(self) -> ft.Control:
        """Build the wizard view."""
        # Header with back button
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="ダッシュボードに戻る",
                        on_click=self._close_wizard,
                    ),
                    ft.Text(
                        "週次振り返りウィザード",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.all(24),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
        )

        # 一時的にシンプルなプレースホルダーを表示
        placeholder = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "週次振り返りウィザードは準備中です",
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "現在開発中のため、しばらくお待ちください。",
                        size=14,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.padding.all(48),
            alignment=ft.alignment.center,
        )

        return ft.Column(
            controls=[
                header,
                placeholder,
            ],
            expand=True,
        )

    def _build_previous_reviews(self) -> ft.Control:
        """Build previous reviews section."""
        # Sample previous reviews
        previous_reviews = [
            {
                "week": "10月14日 - 10月20日",
                "highlights": "新機能のプロトタイプ完成、チーム研修実施",
                "date": "2日前",
            },
            {
                "week": "10月7日 - 10月13日",
                "highlights": "APIドキュメント更新、バグ修正5件",
                "date": "9日前",
            },
            {
                "week": "9月30日 - 10月6日",
                "highlights": "要件定義完了、UI設計レビュー",
                "date": "16日前",
            },
        ]

        review_cards = []
        for review in previous_reviews:
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    review["week"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    review["date"],
                                    size=12,
                                    color=ft.Colors.OUTLINE,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            review["highlights"],
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
            review_cards.append(card)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "📋 過去の振り返り",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=12),
                    *review_cards,
                ],
                spacing=8,
            ),
            padding=24,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _get_current_week(self) -> str:
        """Get current week date range string."""
        today = datetime.now()
        # Get Monday of current week
        monday = today - timedelta(days=today.weekday())
        # Get Sunday of current week
        sunday = monday + timedelta(days=6)

        return f"{monday.strftime('%m月%d日')} - {sunday.strftime('%m月%d日')}"

    def _start_review_wizard(self, _: ft.ControlEvent) -> None:
        """Start the review wizard."""
        self.show_wizard = True
        self.update()

    def _close_wizard(self, _: ft.ControlEvent) -> None:
        """Close the wizard and return to dashboard."""
        self.show_wizard = False
        self.update()

    def _handle_wizard_complete(self, _: dict) -> None:
        """Handle wizard completion."""
        # TODO: Save review data to database
        self.show_snack_bar("週次振り返りが完了しました！")
        self.show_wizard = False
        self.update()

    def _handle_save_reflection(self, _: dict) -> None:
        """Handle reflection save."""
        # TODO: Save reflection to database
        self.show_snack_bar("振り返りを保存しました")
