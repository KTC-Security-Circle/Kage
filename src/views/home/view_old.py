"""ホーム画面のView実装。

このモジュールは、アプリケーションのホーム画面を提供します。
ユーザーのダッシュボード、最近のアクティビティ、クイックアクション等を表示します。
"""

from __future__ import annotations

import flet as ft

from views.sample import (
    get_daily_review,
    get_sample_memos,
    get_sample_projects,
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
        import random

        from views.sample import SampleTaskStatus

        # sample.pyから統計データとタスクデータを取得
        sample_tasks = get_sample_tasks()
        sample_memos = get_sample_memos()
        sample_projects = get_sample_projects()

        # デイリーレビューデータを取得
        self.daily_review = get_daily_review()

        # Inboxメモを取得（AI提案ステータスを追加）
        self.inbox_memos = []
        for memo in sample_memos:
            if memo.status.value == "inbox":
                # サンプルとしてAI提案ステータスを追加（セキュリティ用途ではないためS311を抑制）
                ai_status = random.choice(["available", "pending", "not_requested"])  # noqa: S311
                memo_dict = {
                    "id": str(memo.id),
                    "title": memo.title,
                    "content": memo.content,
                    "ai_suggestion_status": ai_status,
                }
                self.inbox_memos.append(memo_dict)

        # 統計データを設定（テンプレートに合わせて3列表示）
        self.stats = {
            "todays_tasks": len([t for t in sample_tasks if t.status == SampleTaskStatus.TODAYS]),
            "todo_tasks": len([t for t in sample_tasks if t.status == SampleTaskStatus.TODO]),
            "active_projects": len([p for p in sample_projects if p.status.value == "active"]),
        }

    def build(self) -> ft.Control:
        """ホーム画面UIを構築する。

        Returns:
            構築されたコントロール
        """
        content_sections = [
            self._build_header(),
            ft.Container(height=SPACING.md),
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

    def _build_daily_review(self) -> ft.Control:
        """デイリーレビューセクションを構築する。

        Returns:
            デイリーレビューコントロール
        """
        review = self.daily_review

        # アイコンマッピング
        icon_map = {
            "error": ft.Icons.GITE_ROUNDED,
            "coffee": ft.Icons.COFFEE,
            "play_arrow": ft.Icons.BOLT,
            "trending_up": ft.Icons.TRENDING_UP,
            "lightbulb": ft.Icons.AUTO_AWESOME,
            "check_circle": ft.Icons.CHECK_CIRCLE,
            "wb_sunny": ft.Icons.WB_SUNNY,
        }

        # 背景色マッピング（淡い色）
        bg_color_map = {
            "amber": ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
            "blue": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
            "green": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
            "primary": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
            "purple": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
        }

        # ボーダー色マッピング
        border_color_map = {
            "amber": ft.Colors.AMBER_400,
            "blue": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
            "green": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
            "primary": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
            "purple": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
        }

        # アイコン色（濃い目の色）
        icon_color_map = {
            "amber": ft.Colors.BLUE_GREY_900,
            "blue": ft.Colors.BLUE_GREY_900,
            "green": ft.Colors.BLUE_GREY_900,
            "primary": ft.Colors.BLUE_GREY_900,
            "purple": ft.Colors.BLUE_GREY_900,
        }

        icon = icon_map.get(review["icon"], ft.Icons.INFO)
        bg_color = bg_color_map.get(review["color"], ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800))
        border_color = border_color_map.get(review["color"], ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800))
        icon_color = icon_color_map.get(review["color"], ft.Colors.BLUE_GREY_900)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            # アイコン部分
                            ft.Container(
                                content=ft.Icon(icon, size=24, color=icon_color),
                                padding=12,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=50,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=2,
                                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 1),
                                ),
                            ),
                            # メッセージ部分
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            review["message"],
                                            size=18,
                                            weight=ft.FontWeight.NORMAL,
                                            color=ft.Colors.BLUE_GREY_900,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=SPACING.md,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(
                        content=ft.OutlinedButton(
                            text=review["action_text"],
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda _e, route=review["action_route"]: (self._handle_action_click(route)),
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE_GREY_900,
                                bgcolor=ft.Colors.WHITE,
                                side=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800)),
                            ),
                        ),
                        margin=ft.margin.only(top=SPACING.sm),
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(24),
            bgcolor=bg_color,
            border_radius=12,
            border=ft.border.all(1, border_color),
        )

    def _build_inbox_memos_section(self) -> ft.Control:
        """Inboxメモセクションを構築する。

        Returns:
            Inboxメモセクションコントロール
        """
        max_content_length = 100  # メモ内容の最大表示文字数

        def create_memo_item(memo: dict[str, str]) -> ft.Container:
            """メモアイテムを作成する関数"""
            content_preview = (
                memo["content"][:max_content_length] + "..."
                if len(memo["content"]) > max_content_length
                else memo["content"]
            )

            # AI提案ステータスのバッジ
            status_badge = None
            if memo["ai_suggestion_status"] == "available":
                status_badge = ft.Container(
                    content=ft.Text(
                        "AI提案あり",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.BLUE_700,
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.BLUE_300),
                )
            elif memo["ai_suggestion_status"] == "pending":
                status_badge = ft.Container(
                    content=ft.Text(
                        "AI処理中",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.BLUE_GREY_700),
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_100),
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)),
                )
            elif memo["ai_suggestion_status"] == "not_requested":
                status_badge = ft.Container(
                    content=ft.Text(
                        "AI未実行",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.BLUE_GREY_700),
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.TRANSPARENT,
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)),
                )

            title_row = ft.Row(
                [
                    ft.Text(
                        memo["title"],
                        size=14,
                        weight=ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=SPACING.xs,
            )
            if status_badge:
                title_row.controls.append(status_badge)

            return ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        ft.Text(
                            content_preview,
                            size=14,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                            max_lines=2,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=12,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800)),
                on_click=lambda _e, memo_id=memo["id"]: self._handle_memo_click(memo_id),
                ink=True,
            )

        # リスト内包表記でメモアイテムを作成
        memo_items = [create_memo_item(memo) for memo in self.inbox_memos[:3]]

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
                            "今日のタスクとプロジェクトの概要",
                            size=16,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                    spacing=SPACING.xs,
                ),
                ft.ElevatedButton(
                    text="新しいメモ",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: self._handle_action_click("/memos"),
                    style=ft.ButtonStyle(
                        bgcolor=get_light_color("primary"),
                        color=ft.Colors.WHITE,
                    ),
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
            self._create_stat_card(
                "次のアクション",
                str(self.stats["todays_tasks"]),
                "件のタスク",
                ft.Icons.CHECK_BOX_OUTLINED,
                "/tasks",
            ),
            self._create_stat_card(
                "インボックス",
                str(self.stats["todo_tasks"]),
                "未処理のタスク",
                ft.Icons.SCHEDULE,
                "/tasks",
            ),
            self._create_stat_card(
                "進行中プロジェクト",
                str(self.stats["active_projects"]),
                "件のプロジェクト",
                ft.Icons.FOLDER_OPEN,
                "/projects",
            ),
        ]

        return ft.ResponsiveRow(
            stats_cards,
            spacing=SPACING.md,
            run_spacing=SPACING.md,
        )

    def _create_stat_card(self, title: str, value: str, subtitle: str, icon: str, route: str) -> ft.Control:
        """統計カードを作成する。

        Args:
            title: カードタイトル
            value: 表示値
            subtitle: サブタイトル
            icon: アイコン
            route: クリック時の遷移先

        Returns:
            統計カードコントロール
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                title,
                                size=18,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Icon(icon, size=20, color=ft.Colors.BLUE_GREY_900),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=SPACING.sm),
                    ft.Text(
                        value,
                        size=36,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        subtitle,
                        size=14,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                    ),
                ],
                spacing=0,
                tight=True,
            ),
            padding=ft.padding.all(24),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
            on_click=lambda _: self._handle_action_click(route),
            ink=True,
            col={"xs": 12, "sm": 6, "md": 4},
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
