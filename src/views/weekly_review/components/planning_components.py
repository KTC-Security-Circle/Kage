"""週次レビューStep3: 来週の計画用コンポーネント

来週の推奨事項と計画を表示するコンポーネント群。
"""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft
from loguru import logger


@dataclass(frozen=True, slots=True)
class PlanTaskData:
    """計画タスクのデータ

    Attributes:
        task_id: タスクID
        title: タスクタイトル
        due_date: 期限 (任意、日本語フォーマット)
    """

    task_id: str
    title: str
    due_date: str | None = None


@dataclass(frozen=True, slots=True)
class RecommendationData:
    """推奨事項のデータ

    Attributes:
        title: 推奨事項のタイトル
        count: 該当アイテム数
        description: 詳細説明
        tasks: 関連タスクリスト
    """

    title: str
    count: int
    description: str
    tasks: list[PlanTaskData]


@dataclass(frozen=True, slots=True)
class RecommendationCardProps:
    """推奨事項カードのプロパティ

    Attributes:
        recommendation: 推奨事項データ
        on_task_click: タスククリック時のコールバック
    """

    recommendation: RecommendationData
    on_task_click: Callable[[str], None] | None = None


class RecommendationCard(ft.Card):
    """推奨事項カード

    AI提案による来週の推奨事項を表示。
    """

    def __init__(self, props: RecommendationCardProps) -> None:
        """推奨事項カードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # ヘッダー
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.ARROW_FORWARD,
                                size=20,
                                color=ft.Colors.BLUE_600,
                            ),
                            ft.Text(
                                self.props.recommendation.title,
                                size=16,
                                weight=ft.FontWeight.W_600,
                            ),
                        ],
                        spacing=8,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(self.props.recommendation.count),
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

        # 説明
        description = ft.Container(
            content=ft.Text(
                self.props.recommendation.description,
                size=14,
                color=ft.Colors.GREY_600,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )

        # タスクリスト (あれば)
        task_list_controls: list[ft.Control] = [header, description]

        if self.props.recommendation.tasks:
            tasks_items = []
            for task in self.props.recommendation.tasks:
                item = self._build_task_item(task)
                tasks_items.append(item)

            tasks_column = ft.Column(
                controls=tasks_items,
                spacing=8,
            )

            tasks_container = ft.Container(
                content=tasks_column,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            )
            task_list_controls.append(tasks_container)

        self.content = ft.Container(
            content=ft.Column(
                controls=task_list_controls,
                spacing=8,
            ),
            padding=ft.padding.only(bottom=8),
        )
        self.elevation = 2

    def _build_task_item(self, task: PlanTaskData) -> ft.Container:
        """タスクアイテムを構築

        Args:
            task: タスクデータ

        Returns:
            タスクアイテムコンテナ
        """
        # タイトル
        title_text = ft.Text(
            task.title,
            size=14,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True,
        )

        # 期限情報
        due_date_text = None
        if task.due_date:
            due_date_text = ft.Text(
                f"期限: {task.due_date}",
                size=12,
                color=ft.Colors.GREY_600,
            )

        text_controls = [title_text]
        if due_date_text:
            text_controls.append(due_date_text)

        text_column = ft.Column(
            controls=text_controls,
            spacing=4,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=ft.Icons.SCHEDULE,
                        size=16,
                        color=ft.Colors.GREY_400,
                    ),
                    text_column,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(12),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            on_click=lambda _, tid=task.task_id: self._handle_task_click(tid),
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


@dataclass(frozen=True, slots=True)
class CompletionCardProps:
    """レビュー完了カードのプロパティ

    Attributes:
        title: カードタイトル
        message: 完了メッセージ
        on_finish: 完了ボタンのコールバック
    """

    title: str = "レビュー完了"
    message: str = "今週も良い1週間にしていきましょう!"
    on_finish: Callable[[], None] | None = None


class CompletionCard(ft.Card):
    """レビュー完了カード

    ウィザード完了時の最終メッセージとボタン。
    """

    def __init__(self, props: CompletionCardProps) -> None:
        """完了カードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # タイトル
        title = ft.Text(
            self.props.title,
            size=16,
            weight=ft.FontWeight.W_600,
        )

        # メッセージ
        message = ft.Text(
            self.props.message,
            size=14,
            color=ft.Colors.GREY_700,
        )

        # 完了ボタン
        finish_button = ft.ElevatedButton(
            text="ホームに戻る",
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.WHITE,
            on_click=lambda _: self._handle_finish(),
            width=float("inf"),
            height=48,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    title,
                    ft.Container(height=4),
                    message,
                    ft.Container(height=16),
                    finish_button,
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
        )
        self.elevation = 2
        self.color = ft.Colors.BLUE_50

    def _handle_finish(self) -> None:
        """完了ボタンのクリック処理"""
        if self.props.on_finish:
            try:
                self.props.on_finish()
            except Exception:
                logger.exception("完了ボタンの処理に失敗")
                raise


@dataclass(frozen=True, slots=True)
class EmptyStateCardProps:
    """空状態カードのプロパティ

    Attributes:
        title: カードタイトル
        message: メッセージ
        icon_name: アイコン名
        icon_color: アイコンの色
    """

    title: str
    message: str
    icon_name: str = ft.Icons.CHECK_CIRCLE
    icon_color: str = ft.Colors.GREEN_600


class EmptyStateCard(ft.Card):
    """空状態カード

    推奨事項がない場合の表示。
    """

    def __init__(self, props: EmptyStateCardProps) -> None:
        """空状態カードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # アイコン
        icon = ft.Icon(
            name=self.props.icon_name,
            size=48,
            color=self.props.icon_color,
        )

        # タイトル
        title = ft.Text(
            self.props.title,
            size=18,
            weight=ft.FontWeight.W_600,
        )

        # メッセージ
        message = ft.Text(
            self.props.message,
            size=14,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    icon,
                    ft.Container(height=16),
                    title,
                    ft.Container(height=8),
                    message,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=48, horizontal=24),
        )
        self.elevation = 1
