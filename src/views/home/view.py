"""ホーム画面のView実装。

このモジュールは、アプリケーションのホーム画面を提供します。
ユーザーのダッシュボード、最近のアクティビティ、クイックアクション等を表示します。
"""

from __future__ import annotations

import flet as ft

from views.sample import (
    SampleMemo,
    get_daily_review,
    get_sample_memos,
    get_sample_statistics,
    get_sample_tasks,
)
from views.shared.base_view import BaseView, BaseViewProps
from views.theme import SPACING, get_light_color


class HomeView(BaseView):
    """ホーム画面のView。

    ダッシュボード表示、最近のアクティビティ、クイックアクション等を提供します。
    """

    def __init__(self, props: BaseViewProps) -> None:
        """HomeViewを初期化する。

        Args:
            props: View共通プロパティ
        """
        super().__init__(props)
        self._initialize_dummy_data()

    def _initialize_dummy_data(self) -> None:
        """サンプルデータを初期化する。

        TODO: 統合フェーズでApplication Service経由の実データ取得に置換
        理由: Task/Project/Memo等の実データ取得APIが未実装のため
        置換先: DI経由でTaskApplicationService等を注入し、実データを取得
        """
        # sample.pyから統計データとタスクデータを取得
        stats = get_sample_statistics()
        sample_tasks = get_sample_tasks()
        sample_memos = get_sample_memos()

        # デイリーレビューデータを取得
        self.daily_review = get_daily_review()

        # Inboxメモを取得
        self.inbox_memos = [memo for memo in sample_memos if memo.status.value == "inbox"]

        # 最近のタスクデータを構築（サンプルタスクから上位3件）
        self.recent_tasks = []
        for task in sample_tasks[:3]:
            # 期限日の表示文字列を生成
            if task.due_date:
                from datetime import datetime, timezone

                today = datetime.now(tz=timezone.utc).date()  # noqa: UP017
                due_date = "今日" if task.due_date == today else str(task.due_date)
            else:
                due_date = "期限なし"

            self.recent_tasks.append(
                {
                    "title": task.title,
                    "project": "Kageプロジェクト",  # TODO: プロジェクト連携時に実データに置換
                    "due_date": due_date,
                }
            )

        # 統計データを設定
        self.project_stats = {
            "total_projects": stats["total_projects"],
            "active_tasks": stats["active_tasks"],
            "completed_tasks": stats["completed_tasks"],
            "pending_memos": stats["pending_memos"],
        }

    def build(self) -> ft.Control:
        """ホーム画面UIを構築する。

        Returns:
            構築されたコントロール
        """
        content_sections = [
            self._build_header(),
            ft.Divider(height=1, color=get_light_color("primary_variant")),
            self._build_daily_review(),
        ]

        # Inboxメモセクションを追加（メモがある場合のみ）
        if self.inbox_memos:
            content_sections.extend(
                [
                    ft.Container(height=SPACING.lg),
                    self._build_inbox_memos_section(),
                ]
            )

        content_sections.extend(
            [
                ft.Container(height=SPACING.lg),
                self._build_stats_cards(),
                ft.Container(height=SPACING.lg),
                self._build_recent_section(),
                ft.Container(height=SPACING.lg),
                self._build_quick_actions(),
            ]
        )

        return ft.Container(
            content=ft.Column(
                content_sections,
                spacing=SPACING.md,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=SPACING.lg,
            expand=True,
        )

    def _build_daily_review(self) -> ft.Control:
        """デイリーレビューセクションを構築する。

        Returns:
            デイリーレビューコントロール
        """
        review = self.daily_review

        # アイコンマッピング
        icon_map = {
            "error": ft.Icons.ERROR,
            "coffee": ft.Icons.COFFEE,
            "play_arrow": ft.Icons.PLAY_ARROW,
            "trending_up": ft.Icons.TRENDING_UP,
            "lightbulb": ft.Icons.LIGHTBULB,
            "check_circle": ft.Icons.CHECK_CIRCLE,
            "wb_sunny": ft.Icons.WB_SUNNY,
        }

        # 色マッピング
        color_map = {
            "amber": ft.Colors.AMBER,
            "blue": ft.Colors.BLUE,
            "green": ft.Colors.GREEN,
            "primary": get_light_color("primary"),
            "purple": ft.Colors.PURPLE,
        }

        icon = icon_map.get(review["icon"], ft.Icons.INFO)
        color = color_map.get(review["color"], get_light_color("primary"))

        return ft.Container(
            content=ft.Row(
                [
                    # アイコン部分
                    ft.Container(
                        content=ft.Icon(icon, size=32, color=color),
                        padding=SPACING.md,
                        bgcolor=get_light_color("surface"),
                        border_radius=50,
                        border=ft.border.all(2, color),
                    ),
                    # メッセージ部分
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    review["message"],
                                    size=16,
                                    weight=ft.FontWeight.NORMAL,
                                ),
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        text=review["action_text"],
                                        icon=ft.Icons.ARROW_FORWARD,
                                        on_click=lambda _e, route=review["action_route"]: (
                                            self._handle_action_click(route)
                                        ),
                                        style=ft.ButtonStyle(
                                            bgcolor=color,
                                            color=ft.Colors.WHITE,
                                        ),
                                    ),
                                    margin=ft.margin.only(top=SPACING.sm),
                                ),
                            ],
                            spacing=SPACING.xs,
                            expand=True,
                        ),
                        expand=True,
                    ),
                ],
                spacing=SPACING.md,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=SPACING.lg,
            bgcolor=get_light_color("surface"),
            border_radius=12,
            border=ft.border.all(1, color),
        )

    def _build_inbox_memos_section(self) -> ft.Control:
        """Inboxメモセクションを構築する。

        Returns:
            Inboxメモセクションコントロール
        """
        max_content_length = 100  # メモ内容の最大表示文字数

        def create_memo_item(memo: SampleMemo) -> ft.Container:
            """メモアイテムを作成する関数"""
            content_preview = (
                memo.content[:max_content_length] + "..." if len(memo.content) > max_content_length else memo.content
            )

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.NOTE, size=16, color=get_light_color("primary")),
                        ft.Column(
                            [
                                ft.Text(
                                    memo.title,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    content_preview,
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    max_lines=2,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=SPACING.sm,
                ),
                padding=SPACING.sm,
                bgcolor=get_light_color("surface"),
                border_radius=8,
                border=ft.border.all(1, get_light_color("primary_variant")),
                on_click=lambda _e, memo_id=memo.id: self._handle_memo_click(str(memo_id)),
                ink=True,
            )

        # リスト内包表記でメモアイテムを作成
        memo_items = [create_memo_item(memo) for memo in self.inbox_memos[:3]]

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.LIGHTBULB, size=20, color=get_light_color("primary")),
                                ft.Text(
                                    "Inboxメモ",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=SPACING.xs,
                        ),
                        ft.TextButton(
                            text="すべて見る",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda _: self._handle_action_click("/memos"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    "整理が必要なメモがあります。AIにタスクを生成させましょう。",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Column(
                    memo_items,
                    spacing=SPACING.sm,
                ),
            ],
            spacing=SPACING.sm,
        )

    def _handle_memo_click(self, memo_id: str) -> None:
        """メモクリック時の処理。

        Args:
            memo_id: クリックされたメモのID

        TODO: 統合フェーズでメモ詳細表示機能を実装
        理由: メモ詳細画面が未実装のため
        置換先: メモ詳細ダイアログまたは画面遷移
        """
        from loguru import logger

        logger.info(f"Memo clicked: {memo_id}")
        # とりあえずメモ画面に遷移
        self._handle_action_click("/memos")

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
        try:
            if self.page:
                self.page.go(route)
        except Exception as e:
            from loguru import logger

            logger.error(f"Navigation error: {e}")
