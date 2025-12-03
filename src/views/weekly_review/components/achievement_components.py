"""週次レビューStep1: 成果レポート用コンポーネント

今週の達成内容を表示するコンポーネント群。
"""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft
from loguru import logger


@dataclass(frozen=True, slots=True)
class AchievementHeaderProps:
    """成果ヘッダーのプロパティ

    Attributes:
        message: メインメッセージ
        icon_name: アイコン名
        icon_color: アイコンの色
    """

    message: str
    icon_name: str = ft.Icons.CELEBRATION
    icon_color: str = ft.Colors.BLUE_600


class AchievementHeader(ft.Container):
    """成果レポートのヘッダー

    アイコンとメッセージを中央揃えで表示。
    """

    def __init__(self, props: AchievementHeaderProps) -> None:
        """ヘッダーを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # アイコン
        icon_container = ft.Container(
            content=ft.Icon(
                name=self.props.icon_name,
                size=48,
                color=self.props.icon_color,
            ),
            padding=ft.padding.all(16),
            bgcolor=f"{self.props.icon_color}1A",
            border_radius=50,
        )

        # メッセージ
        message_text = ft.Text(
            self.props.message,
            size=18,
            color=ft.Colors.GREY_700,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_400,
        )

        self.content = ft.Column(
            controls=[
                icon_container,
                ft.Container(height=16),
                ft.Text(
                    "今週の成果レポート",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                message_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
        self.padding = ft.padding.symmetric(vertical=24)


@dataclass(frozen=True, slots=True)
class HighlightsCardProps:
    """ハイライトカードのプロパティ

    Attributes:
        highlights: ハイライト項目のリスト
        title: カードタイトル
        icon_name: アイコン名
        icon_color: アイコンの色
    """

    highlights: list[str]
    title: str = "主な成果"
    icon_name: str = ft.Icons.TRENDING_UP
    icon_color: str = ft.Colors.BLUE_600


class HighlightsCard(ft.Card):
    """成果のハイライトカード

    今週の主な成果をリスト表示。
    """

    def __init__(self, props: HighlightsCardProps) -> None:
        """ハイライトカードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # ヘッダー
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=self.props.icon_name,
                        size=20,
                        color=self.props.icon_color,
                    ),
                    ft.Text(
                        self.props.title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
        )

        # ハイライトアイテム
        items = []
        for highlight in self.props.highlights:
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.CHECK_CIRCLE,
                            size=20,
                            color=self.props.icon_color,
                        ),
                        ft.Text(
                            highlight,
                            size=14,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                padding=ft.padding.all(12),
                bgcolor=f"{self.props.icon_color}0D",
                border_radius=8,
            )
            items.append(item)

        items_column = ft.Column(
            controls=items,
            spacing=8,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[header, items_column],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )
        self.elevation = 2


@dataclass(frozen=True, slots=True)
class CompletedTaskItemData:
    """完了タスクアイテムのデータ

    Attributes:
        task_id: タスクID
        title: タスクタイトル
        project_title: プロジェクトタイトル (任意)
    """

    task_id: str
    title: str
    project_title: str | None = None


@dataclass(frozen=True, slots=True)
class CompletedTasksListProps:
    """完了タスクリストのプロパティ

    Attributes:
        tasks: 完了タスクのリスト
        on_task_click: タスククリック時のコールバック
        max_display: 最大表示件数
    """

    tasks: list[CompletedTaskItemData]
    on_task_click: Callable[[str], None] | None = None
    max_display: int = 10


class CompletedTasksList(ft.Card):
    """完了タスクリストカード

    今週完了したタスクを一覧表示。
    """

    def __init__(self, props: CompletedTasksListProps) -> None:
        """完了タスクリストを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # ヘッダー
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "完了したタスク一覧",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(len(self.props.tasks)),
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_600,
                        ),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_600,
                        border_radius=12,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
        )

        # タスクアイテム
        items = []
        display_tasks = self.props.tasks[: self.props.max_display]

        for task_data in display_tasks:
            item = self._build_task_item(task_data)
            items.append(item)

        items_column = ft.Column(
            controls=items,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=320,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[header, items_column],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )
        self.elevation = 2

    def _build_task_item(self, task_data: CompletedTaskItemData) -> ft.Container:
        """タスクアイテムを構築

        Args:
            task_data: タスクデータ

        Returns:
            タスクアイテムコンテナ
        """
        # プロジェクト情報
        project_text = None
        if task_data.project_title:
            project_text = ft.Text(
                task_data.project_title,
                size=12,
                color=ft.Colors.GREY_600,
            )

        # タイトルとプロジェクト
        text_column = ft.Column(
            controls=[
                ft.Text(
                    task_data.title,
                    size=14,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                project_text,
            ]
            if project_text
            else [
                ft.Text(
                    task_data.title,
                    size=14,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=4,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=ft.Icons.CHECK_CIRCLE,
                        size=16,
                        color=ft.Colors.GREEN_600,
                    ),
                    text_column,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(12),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            on_click=lambda _, tid=task_data.task_id: self._handle_task_click(tid),
            ink=True,
        )

    def _handle_task_click(self, task_id: str) -> None:
        """タスククリック処理

        Args:
            task_id: タスクID
        """
        if self.props.on_task_click:
            try:
                self.props.on_task_click(task_id)
            except Exception:
                logger.exception(f"タスククリック処理に失敗: {task_id}")
                raise

    def update_tasks(self, tasks: list[CompletedTaskItemData]) -> None:
        """タスクリストを更新

        Args:
            tasks: 新しいタスクリスト
        """
        self.props = CompletedTasksListProps(
            tasks=tasks,
            on_task_click=self.props.on_task_click,
            max_display=self.props.max_display,
        )
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        # ヘッダー
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "完了したタスク一覧",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(len(self.props.tasks)),
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_600,
                        ),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_600,
                        border_radius=12,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
        )

        # タスクアイテム
        items = []
        display_tasks = self.props.tasks[: self.props.max_display]

        for task_data in display_tasks:
            item = self._build_task_item(task_data)
            items.append(item)

        items_column = ft.Column(
            controls=items,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=320,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[header, items_column],
                spacing=8,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )

        try:
            self.update()
        except AssertionError:
            logger.debug("完了タスクリストが未マウント: update()をスキップ")
