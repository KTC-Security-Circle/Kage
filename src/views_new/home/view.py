"""ホーム画面のView実装。

このモジュールは、アプリケーションのホーム画面を提供します。
ユーザーのダッシュボード、最近のアクティビティ、クイックアクション等を表示します。
"""

from __future__ import annotations

import flet as ft

from views_new.shared.base_view import BaseView
from views_new.theme import SPACING, get_light_color


class HomeView(BaseView):
    """ホーム画面のView。

    ダッシュボード表示、最近のアクティビティ、クイックアクション等を提供します。
    """

    def __init__(self, page: ft.Page) -> None:
        """HomeViewを初期化する。

        Args:
            page: Fletページオブジェクト
        """
        super().__init__(page)
        self._initialize_dummy_data()

    def _initialize_dummy_data(self) -> None:
        """ダミーデータを初期化する。

        TODO: 統合フェーズでApplication Service経由の実データ取得に置換
        理由: Task/Project/Memo等の実データ取得APIが未実装のため
        置換先: DI経由でTaskApplicationService等を注入し、実データを取得
        """
        self.recent_tasks = [
            {"title": "UIデザインの完成", "project": "Kageプロジェクト", "due_date": "今日"},
            {"title": "データベース設計", "project": "新プロジェクト", "due_date": "明日"},
            {"title": "テストコード作成", "project": "Kageプロジェクト", "due_date": "今週"},
        ]

        self.project_stats = {
            "total_projects": 3,
            "active_tasks": 12,
            "completed_tasks": 24,
            "pending_memos": 5,
        }

    def build(self) -> ft.Control:
        """ホーム画面UIを構築する。

        Returns:
            構築されたコントロール
        """
        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Divider(),
                    self._build_stats_cards(),
                    ft.Container(height=SPACING.lg),
                    self._build_recent_section(),
                    ft.Container(height=SPACING.lg),
                    self._build_quick_actions(),
                ],
                spacing=SPACING.md,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=SPACING.lg,
            expand=True,
        )

    def _build_header(self) -> ft.Control:
        """ヘッダー部分を構築する。

        Returns:
            ヘッダーコントロール
        """
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "ホーム",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "タスク管理の概要とクイックアクセス",
                            size=16,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=SPACING.xs,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _build_stats_cards(self) -> ft.Control:
        """統計カード群を構築する。

        Returns:
            統計カードコントロール
        """
        stats_cards = [
            self._create_stat_card("プロジェクト", str(self.project_stats["total_projects"]), ft.Icons.FOLDER),
            self._create_stat_card("進行中タスク", str(self.project_stats["active_tasks"]), ft.Icons.TASK),
            self._create_stat_card("完了タスク", str(self.project_stats["completed_tasks"]), ft.Icons.CHECK_CIRCLE),
            self._create_stat_card("未処理メモ", str(self.project_stats["pending_memos"]), ft.Icons.NOTE),
        ]

        return ft.Row(
            stats_cards,
            spacing=SPACING.md,
            wrap=True,
            run_spacing=SPACING.md,
        )

    def _create_stat_card(self, title: str, value: str, icon: str) -> ft.Control:
        """統計カードを作成する。

        Args:
            title: カードタイトル
            value: 表示値
            icon: アイコン

        Returns:
            統計カードコントロール
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, size=24, color=get_light_color("primary")),
                            ft.Text(
                                value,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=get_light_color("primary"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        title,
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=SPACING.sm,
                tight=True,
            ),
            padding=SPACING.md,
            bgcolor=get_light_color("surface"),
            border_radius=8,
            border=ft.border.all(1, get_light_color("primary_variant")),
            width=180,
        )

    def _build_recent_section(self) -> ft.Control:
        """最近のアクティビティセクションを構築する。

        Returns:
            最近のアクティビティコントロール
        """
        return ft.Column(
            [
                ft.Text(
                    "最近のタスク",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    content=ft.Column(
                        [self._create_task_item(task) for task in self.recent_tasks],
                        spacing=SPACING.sm,
                    ),
                    padding=SPACING.md,
                    bgcolor=get_light_color("surface"),
                    border_radius=8,
                    border=ft.border.all(1, get_light_color("primary_variant")),
                ),
            ],
            spacing=SPACING.sm,
        )

    def _create_task_item(self, task: dict[str, str]) -> ft.Control:
        """タスク項目を作成する。

        Args:
            task: タスクデータ

        Returns:
            タスク項目コントロール
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.TASK, size=16),
                    ft.Column(
                        [
                            ft.Text(
                                task["title"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{task['project']} • {task['due_date']}",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                    ),
                ],
                spacing=SPACING.sm,
            ),
            padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
            on_click=lambda _e, task_title=task["title"]: self._handle_task_click(task_title),
            ink=True,
            border_radius=4,
        )

    def _build_quick_actions(self) -> ft.Control:
        """クイックアクションセクションを構築する。

        Returns:
            クイックアクションコントロール
        """
        actions = [
            {"label": "新しいタスク", "icon": ft.Icons.ADD_TASK, "route": "/tasks"},
            {"label": "プロジェクト作成", "icon": ft.Icons.CREATE_NEW_FOLDER, "route": "/projects"},
            {"label": "メモ追加", "icon": ft.Icons.NOTE_ADD, "route": "/memos"},
            {"label": "週間レビュー", "icon": ft.Icons.ASSESSMENT, "route": "/weekly-review"},
        ]

        return ft.Column(
            [
                ft.Text(
                    "クイックアクション",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [self._create_action_button(action) for action in actions],
                    spacing=SPACING.md,
                    wrap=True,
                    run_spacing=SPACING.md,
                ),
            ],
            spacing=SPACING.sm,
        )

    def _create_action_button(self, action: dict[str, str]) -> ft.Control:
        """アクションボタンを作成する。

        Args:
            action: アクションデータ

        Returns:
            アクションボタンコントロール
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        action["icon"],
                        size=32,
                        color=get_light_color("primary"),
                    ),
                    ft.Text(
                        action["label"],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=SPACING.xs,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            padding=SPACING.md,
            bgcolor=get_light_color("surface"),
            border_radius=8,
            border=ft.border.all(1, get_light_color("primary")),
            width=120,
            height=100,
            on_click=lambda _e, route=action["route"]: self._handle_action_click(route),
            ink=True,
        )

    def _handle_task_click(self, task_title: str) -> None:
        """タスククリック時の処理。

        Args:
            task_title: クリックされたタスクのタイトル

        TODO: 統合フェーズでタスク詳細表示機能を実装
        理由: タスク詳細画面が未実装のため
        置換先: タスク詳細ダイアログまたは画面遷移
        """
        # ダミー実装：ログ出力のみ
        from loguru import logger

        logger.info(f"Task clicked: {task_title}")

    def _handle_action_click(self, route: str) -> None:
        """アクションクリック時の処理。

        Args:
            route: 遷移先ルート
        """
        self.page.go(route)
