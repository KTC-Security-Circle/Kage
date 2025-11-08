"""Review wizard component for guided weekly retrospective."""

from datetime import datetime
from typing import Any

import flet as ft


class ReviewWizard(ft.Container):
    """Step-by-step wizard for conducting weekly reviews."""

    def __init__(
        self,
        on_complete: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize review wizard.

        Args:
            on_complete: Callback when review is completed
        """
        super().__init__()
        self.on_complete = on_complete
        self.current_step = 0
        self.total_steps = 4
        self.review_data: dict[str, Any] = {}

        # Step components
        self.progress_indicator: ft.ProgressBar | None = None
        self.step_content: ft.Container | None = None
        self.navigation_buttons: ft.Row | None = None

        # 初期化時にコンテンツを構築
        self._build_wizard_content()

    def _build_wizard_content(self) -> None:
        """Build the review wizard."""
        # Progress indicator
        self.progress_indicator = ft.ProgressBar(
            value=self.current_step / self.total_steps,
            color=ft.Colors.PRIMARY,
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=8,
        )

        # Step indicator dots
        step_dots = []
        for i in range(self.total_steps):
            is_current = i == self.current_step
            is_completed = i < self.current_step

            dot_color = (
                ft.Colors.PRIMARY if is_current else ft.Colors.GREEN if is_completed else ft.Colors.OUTLINE_VARIANT
            )

            dot = ft.Container(
                width=12,
                height=12,
                border_radius=6,
                bgcolor=dot_color,
                content=ft.Icon(
                    ft.Icons.CHECK,
                    size=8,
                    color=ft.Colors.WHITE,
                )
                if is_completed
                else None,
                alignment=ft.alignment.center,
            )
            step_dots.append(dot)

        # Header with progress
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "📝 週次振り返りウィザード",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"ステップ {self.current_step + 1} / {self.total_steps}",
                                size=16,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=16),
                    self.progress_indicator,
                    ft.Container(height=12),
                    ft.Row(
                        controls=step_dots,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                ],
            ),
            padding=24,
            bgcolor=ft.Colors.SURFACE,
            border_radius=ft.border_radius.only(top_left=16, top_right=16),
        )

        # Step content
        self.step_content = ft.Container(
            content=self._build_current_step(),
            padding=24,
            expand=True,
        )

        # Navigation buttons
        self.navigation_buttons = self._build_navigation()

        # Containerの設定を行う
        self.content = ft.Column(
            controls=[
                header,
                self.step_content,
                self.navigation_buttons,
            ],
            spacing=0,
            expand=True,
        )
        self.bgcolor = ft.Colors.SURFACE
        self.border_radius = 16
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
        )

    def _build_current_step(self) -> ft.Control:
        """Build content for the current step."""
        steps = [
            self._build_step_1_achievements,
            self._build_step_2_challenges,
            self._build_step_3_learnings,
            self._build_step_4_planning,
        ]

        if 0 <= self.current_step < len(steps):
            return steps[self.current_step]()

        return ft.Text("エラー: 無効なステップです")

    def _build_step_1_achievements(self) -> ft.Control:
        """Build step 1: Achievements and wins."""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.EMOJI_EVENTS,
                        size=64,
                        color=ft.Colors.AMBER,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "🎉 今週の成果",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "今週達成できたことや、うまくいったことを振り返ってみましょう",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.TextField(
                    label="達成したこと",
                    hint_text="完了したタスク、成功したプロジェクト、身につけたスキルなど...",
                    multiline=True,
                    min_lines=4,
                    max_lines=6,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("achievements", e.control.value),
                ),
                ft.Container(height=16),
                ft.TextField(
                    label="感じた成長",
                    hint_text="新しく学んだこと、改善された点、自信がついたことなど...",
                    multiline=True,
                    min_lines=3,
                    max_lines=4,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("growth", e.control.value),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

    def _build_step_2_challenges(self) -> ft.Control:
        """Build step 2: Challenges and obstacles."""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.FITNESS_CENTER,
                        size=64,
                        color=ft.Colors.ORANGE,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "💪 課題と困難",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "今週直面した課題や困難を振り返り、学びに変えましょう",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.TextField(
                    label="直面した課題",
                    hint_text="未完了のタスク、技術的な問題、時間管理の課題など...",
                    multiline=True,
                    min_lines=4,
                    max_lines=6,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("challenges", e.control.value),
                ),
                ft.Container(height=16),
                ft.TextField(
                    label="改善のアイデア",
                    hint_text="次回同じ課題に直面した時の対策や改善案...",
                    multiline=True,
                    min_lines=3,
                    max_lines=4,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("improvements", e.control.value),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

    def _build_step_3_learnings(self) -> ft.Control:
        """Build step 3: Key learnings and insights."""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.LIGHTBULB,
                        size=64,
                        color=ft.Colors.YELLOW,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "💡 学びと気づき",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "今週得られた重要な学びや気づきをまとめましょう",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.TextField(
                    label="重要な学び",
                    hint_text="新しい知識、効果的だった手法、避けるべき行動など...",
                    multiline=True,
                    min_lines=4,
                    max_lines=6,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("learnings", e.control.value),
                ),
                ft.Container(height=16),
                ft.TextField(
                    label="継続したいこと",
                    hint_text="効果的だった習慣、続けたい取り組みなど...",
                    multiline=True,
                    min_lines=3,
                    max_lines=4,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("continue", e.control.value),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

    def _build_step_4_planning(self) -> ft.Control:
        """Build step 4: Next week planning."""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ROCKET_LAUNCH,
                        size=64,
                        color=ft.Colors.BLUE,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "🚀 来週への準備",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "今週の振り返りを活かして、来週の目標と計画を立てましょう",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.TextField(
                    label="来週の目標",
                    hint_text="達成したいこと、集中したい分野、挑戦したいことなど...",
                    multiline=True,
                    min_lines=4,
                    max_lines=6,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("goals", e.control.value),
                ),
                ft.Container(height=16),
                ft.TextField(
                    label="具体的なアクション",
                    hint_text="目標達成のための具体的なステップや行動計画...",
                    multiline=True,
                    min_lines=3,
                    max_lines=4,
                    border_radius=12,
                    on_change=lambda e: self._save_step_data("actions", e.control.value),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

    def _build_navigation(self) -> ft.Row:
        """Build navigation buttons."""
        back_button = ft.OutlinedButton(
            text="戻る",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._handle_back,
            disabled=self.current_step == 0,
        )

        next_button = ft.ElevatedButton(
            text="完了" if self.current_step == self.total_steps - 1 else "次へ",
            icon=ft.Icons.CHECK if self.current_step == self.total_steps - 1 else ft.Icons.ARROW_FORWARD,
            icon_color=ft.Colors.ON_PRIMARY,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY,
            ),
            on_click=self._handle_next,
        )

        return ft.Row(
            controls=[back_button, next_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _handle_back(self, _: ft.ControlEvent) -> None:
        """Handle back button click."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_wizard()

    def _handle_next(self, _: ft.ControlEvent) -> None:
        """Handle next/complete button click."""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self._update_wizard()
        else:
            # Complete the review
            self.review_data["completed_at"] = datetime.now()
            if self.on_complete:
                self.on_complete(self.review_data)

    def _save_step_data(self, key: str, value: str) -> None:
        """Save data from current step."""
        self.review_data[key] = value

    def _update_wizard(self) -> None:
        """Update wizard display."""
        # Update progress
        if self.progress_indicator:
            self.progress_indicator.value = self.current_step / self.total_steps

        # Update step content
        if self.step_content:
            self.step_content.content = self._build_current_step()

        # Update navigation
        if self.navigation_buttons:
            new_nav = self._build_navigation()
            self.navigation_buttons.controls = new_nav.controls

        self.update()
