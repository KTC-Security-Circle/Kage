"""Review components for weekly retrospective visualization."""

from datetime import datetime
from typing import Any

import flet as ft


class WeeklyStatsCard(ft.Container):
    """Beautiful stats card showing weekly achievements."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        icon: str = ft.Icons.ANALYTICS,
        color: str = ft.Colors.PRIMARY,
        trend: str = "",
    ) -> None:
        """Initialize weekly stats card.

        Args:
            title: Card title
            value: Main value to display
            subtitle: Additional subtitle text
            icon: Icon to display
            color: Theme color for the card
            trend: Trend indicator (e.g., "+12%", "↑ 5")
        """
        super().__init__()
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.color = color
        self.trend = trend

        # 初期化時にコンテンツを構築
        self._build_card_content()

    def _build_card_content(self) -> None:
        """Build the stats card with gradient background."""
        # Main value with large font
        value_text = ft.Text(
            self.value,
            size=36,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )

        # Title and subtitle
        title_text = ft.Text(
            self.title,
            size=16,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
        )

        subtitle_text = (
            ft.Text(
                self.subtitle,
                size=12,
                color=ft.Colors.WHITE70,
            )
            if self.subtitle
            else ft.Container()
        )

        # Trend indicator
        trend_chip = (
            ft.Container(
                content=ft.Text(
                    self.trend,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=ft.Colors.WHITE24,
                border_radius=12,
            )
            if self.trend
            else ft.Container()
        )

        # Icon with subtle background
        icon_container = ft.Container(
            content=ft.Icon(
                self.icon,
                size=32,
                color=ft.Colors.WHITE,
            ),
            width=60,
            height=60,
            border_radius=30,
            bgcolor=ft.Colors.WHITE24,
            alignment=ft.alignment.center,
        )

        # Containerの設定を行う
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[icon_container, trend_chip],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=16),
                value_text,
                title_text,
                subtitle_text,
            ],
            spacing=4,
            tight=True,
        )
        self.padding = 24
        self.width = 280
        self.height = 180
        self.border_radius = 16
        self.gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[self.color, f"{self.color}80"],
        )
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.2, self.color),
        )


class TaskCompletionChart(ft.Container):
    """Visual chart showing task completion over the week."""

    def __init__(
        self,
        daily_data: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize task completion chart.

        Args:
            daily_data: List of daily completion data
        """
        super().__init__()
        self.daily_data = daily_data or self._generate_sample_data()

        # 初期化時にコンテンツを構築
        self._build_chart_content()

    def _build_chart_content(self) -> None:
        """Build the task completion chart."""
        chart_bars = []
        max_tasks = max(day["completed"] + day["pending"] for day in self.daily_data)

        for day in self.daily_data:
            total_height = 120
            completed_height = (day["completed"] / max_tasks) * total_height if max_tasks > 0 else 0
            pending_height = (day["pending"] / max_tasks) * total_height if max_tasks > 0 else 0

            # Completed tasks bar (green)
            completed_bar = ft.Container(
                width=32,
                height=completed_height,
                bgcolor=ft.Colors.GREEN_400,
                border_radius=ft.border_radius.only(top_left=4, top_right=4),
            )

            # Pending tasks bar (orange)
            pending_bar = ft.Container(
                width=32,
                height=pending_height,
                bgcolor=ft.Colors.ORANGE_300,
                border_radius=ft.border_radius.only(top_left=4, top_right=4),
            )

            # Stack bars
            bar_column = ft.Column(
                controls=[
                    ft.Container(height=total_height - completed_height - pending_height),
                    pending_bar,
                    completed_bar,
                    ft.Text(
                        day["day"],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            chart_bars.append(bar_column)

        # Containerの設定を行う
        self.content = ft.Column(
            controls=[
                ft.Text(
                    "📊 週間タスク完了状況",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=12),
                ft.Row(
                    controls=chart_bars,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                ft.Container(height=16),
                # Legend
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    width=16,
                                    height=16,
                                    bgcolor=ft.Colors.GREEN_400,
                                    border_radius=4,
                                ),
                                ft.Text("完了", size=14),
                            ],
                            spacing=8,
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    width=16,
                                    height=16,
                                    bgcolor=ft.Colors.ORANGE_300,
                                    border_radius=4,
                                ),
                                ft.Text("未完了", size=14),
                            ],
                            spacing=8,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=24,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.padding = 24
        self.border_radius = 16
        self.bgcolor = ft.Colors.SECONDARY_CONTAINER
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)

    def _generate_sample_data(self) -> list[dict[str, Any]]:
        """Generate sample data for demonstration."""
        return [
            {"day": "月", "completed": 8, "pending": 2},
            {"day": "火", "completed": 6, "pending": 4},
            {"day": "水", "completed": 9, "pending": 1},
            {"day": "木", "completed": 7, "pending": 3},
            {"day": "金", "completed": 10, "pending": 0},
            {"day": "土", "completed": 4, "pending": 1},
            {"day": "日", "completed": 3, "pending": 2},
        ]


class ProductivityInsights(ft.Container):
    """Insights panel showing productivity analysis."""

    def __init__(self) -> None:
        """Initialize productivity insights."""
        super().__init__()

        # 初期化時にコンテンツを構築
        self._build_insights_content()

    def _build_insights_content(self) -> None:
        """Build the insights panel."""
        insights = [
            {
                "icon": ft.Icons.TRENDING_UP,
                "title": "生産性向上",
                "description": "今週は先週比で15%タスク完了率が向上しました",
                "color": ft.Colors.GREEN,
            },
            {
                "icon": ft.Icons.ACCESS_TIME,
                "title": "最適な時間帯",
                "description": "午前中（9-11時）が最も集中できています",
                "color": ft.Colors.BLUE,
            },
            {
                "icon": ft.Icons.STAR,
                "title": "達成ハイライト",
                "description": "重要プロジェクトを3つ完了しました",
                "color": ft.Colors.AMBER,
            },
        ]

        insight_cards = []
        for insight in insights:
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                insight["icon"],
                                size=24,
                                color=ft.Colors.WHITE,
                            ),
                            width=48,
                            height=48,
                            border_radius=24,
                            bgcolor=insight["color"],
                            alignment=ft.alignment.center,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    insight["title"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    insight["description"],
                                    size=14,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=4,
                            tight=True,
                            expand=True,
                        ),
                    ],
                    spacing=16,
                ),
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
            insight_cards.append(card)

        # Containerの設定を行う
        self.content = ft.Column(
            controls=[
                ft.Text(
                    "💡 今週のインサイト",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=12),
                *insight_cards,
            ],
            spacing=12,
        )
        self.padding = 24
        self.border_radius = 16
        self.bgcolor = ft.Colors.SURFACE
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)


class ReflectionCard(ft.Container):
    """Interactive card for weekly reflection and planning."""

    def __init__(
        self,
        on_save_reflection: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize reflection card.

        Args:
            on_save_reflection: Callback when reflection is saved
        """
        super().__init__()
        self.on_save_reflection = on_save_reflection
        self.reflection_text = ""
        self.goals_text = ""

        # 初期化時にコンテンツを構築
        self._build_reflection_content()

    def _build_reflection_content(self) -> None:
        """Build the reflection card."""
        reflection_field = ft.TextField(
            label="今週の振り返り",
            hint_text="今週達成できたこと、学んだこと、改善点など...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            on_change=self._on_reflection_change,
            border_radius=8,
        )

        goals_field = ft.TextField(
            label="来週の目標",
            hint_text="来週取り組みたいこと、改善したい点など...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            on_change=self._on_goals_change,
            border_radius=8,
        )

        save_button = ft.ElevatedButton(
            text="振り返りを保存",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY,
            ),
            on_click=self._handle_save,
        )

        # Containerの設定を行う
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.PSYCHOLOGY,
                            size=24,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            "🤔 週次振り返り",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=16),
                reflection_field,
                ft.Container(height=16),
                goals_field,
                ft.Container(height=20),
                ft.Row(
                    controls=[save_button],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=8,
        )
        self.padding = 24
        self.border_radius = 16
        self.bgcolor = ft.Colors.SURFACE
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)

    def _on_reflection_change(self, e: ft.ControlEvent) -> None:
        """Handle reflection text change."""
        self.reflection_text = e.control.value

    def _on_goals_change(self, e: ft.ControlEvent) -> None:
        """Handle goals text change."""
        self.goals_text = e.control.value

    def _handle_save(self, _: ft.ControlEvent) -> None:
        """Handle save button click."""
        if self.on_save_reflection:
            self.on_save_reflection(
                {
                    "reflection": self.reflection_text,
                    "goals": self.goals_text,
                    "date": datetime.now(),
                }
            )
