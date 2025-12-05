"""週次レビューStep2: システム整理用コンポーネント

ゾンビタスクや未処理メモの整理を支援するコンポーネント群。
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import flet as ft
from loguru import logger

ZombieTaskAction = Literal["subdivide", "someday", "delete"] | None
MemoAction = Literal["create_task", "archive", "skip"] | None


@dataclass(frozen=True, slots=True)
class ZombieTaskData:
    """ゾンビタスクのデータ

    Attributes:
        task_id: タスクID
        title: タスクタイトル
        reason: AI分析による理由
        selected_action: 選択されたアクション
    """

    task_id: str
    title: str
    reason: str
    selected_action: ZombieTaskAction = None


@dataclass(frozen=True, slots=True)
class ZombieTaskCardProps:
    """ゾンビタスクカードのプロパティ

    Attributes:
        task_data: タスクデータ
        on_action_selected: アクション選択時のコールバック
    """

    task_data: ZombieTaskData
    on_action_selected: Callable[[str, ZombieTaskAction], None] | None = None


class ZombieTaskCard(ft.Card):
    """ゾンビタスクカード

    長期滞留タスクとAI分析結果、アクション選択ボタンを表示。
    """

    def __init__(self, props: ZombieTaskCardProps) -> None:
        """ゾンビタスクカードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()
        self.elevation = 2
        self.color = ft.Colors.YELLOW_50

    def _build_header(self) -> ft.Container:
        """ヘッダーを構築

        Returns:
            ヘッダーコンテナ
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.props.task_data.title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.AUTO_AWESOME,
                                size=16,
                                color=ft.Colors.YELLOW_700,
                            ),
                            ft.Text(
                                f"AIの分析: {self.props.task_data.reason}",
                                size=14,
                                color=ft.Colors.GREY_700,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
        )

    def _build_content(self) -> ft.Container:
        """カードコンテンツを構築

        Returns:
            コンテンツコンテナ
        """
        header = self._build_header()
        action_buttons = self._build_action_buttons()

        return ft.Container(
            content=ft.Column(
                controls=[header, action_buttons],
                spacing=12,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )

    def _build_action_buttons(self) -> ft.Container:
        """アクションボタンを構築

        Returns:
            アクションボタンコンテナ
        """
        # どうしますか?テキスト
        question_text = ft.Text(
            "どうしますか?",
            size=14,
            color=ft.Colors.GREY_700,
        )

        # 細分化ボタン
        subdivide_button = ft.ElevatedButton(
            text="細分化する",
            icon=ft.Icons.FORMAT_LIST_BULLETED,
            on_click=lambda _: self._handle_action("subdivide"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600 if self.props.task_data.selected_action == "subdivide" else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.task_data.selected_action == "subdivide" else ft.Colors.GREY_800,
            ),
        )

        # いつか/多分へボタン
        someday_button = ft.ElevatedButton(
            text="いつか/多分へ",
            icon=ft.Icons.ARCHIVE_OUTLINED,
            on_click=lambda _: self._handle_action("someday"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600 if self.props.task_data.selected_action == "someday" else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.task_data.selected_action == "someday" else ft.Colors.GREY_800,
            ),
        )

        # 削除ボタン
        delete_button = ft.ElevatedButton(
            text="削除する",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=lambda _: self._handle_action("delete"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600 if self.props.task_data.selected_action == "delete" else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.task_data.selected_action == "delete" else ft.Colors.RED_600,
            ),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    question_text,
                    ft.Container(height=4),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(subdivide_button, col={"sm": 12, "md": 4}),
                            ft.Container(someday_button, col={"sm": 12, "md": 4}),
                            ft.Container(delete_button, col={"sm": 12, "md": 4}),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
        )

    def _handle_action(self, action: ZombieTaskAction) -> None:
        """アクション選択処理

        Args:
            action: 選択されたアクション
        """
        if self.props.on_action_selected:
            try:
                self.props.on_action_selected(self.props.task_data.task_id, action)
            except Exception:
                logger.exception(f"アクション選択処理に失敗: {action}")
                raise

    def set_selected_action(self, action: ZombieTaskAction) -> None:
        """選択されたアクションを更新

        Args:
            action: 新しいアクション
        """
        new_data = ZombieTaskData(
            task_id=self.props.task_data.task_id,
            title=self.props.task_data.title,
            reason=self.props.task_data.reason,
            selected_action=action,
        )
        self.props = ZombieTaskCardProps(
            task_data=new_data,
            on_action_selected=self.props.on_action_selected,
        )
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        self.content = self._build_content()

        try:
            self.update()
        except AssertionError:
            logger.debug("ゾンビタスクカードが未マウント: update()をスキップ")


@dataclass(frozen=True, slots=True)
class UnprocessedMemoData:
    """未処理メモのデータ

    Attributes:
        memo_id: メモID
        title: メモタイトル
        content: メモ内容
        suggestion: AI提案メッセージ
        selected_action: 選択されたアクション
    """

    memo_id: str
    title: str
    content: str
    suggestion: str
    selected_action: MemoAction = None


@dataclass(frozen=True, slots=True)
class UnprocessedMemoCardProps:
    """未処理メモカードのプロパティ

    Attributes:
        memo_data: メモデータ
        on_action_selected: アクション選択時のコールバック
    """

    memo_data: UnprocessedMemoData
    on_action_selected: Callable[[str, MemoAction], None] | None = None


class UnprocessedMemoCard(ft.Card):
    """未処理メモカード

    未処理のメモとAI提案、アクション選択ボタンを表示。
    """

    def __init__(self, props: UnprocessedMemoCardProps) -> None:
        """未処理メモカードを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()
        self.elevation = 2
        self.color = ft.Colors.BLUE_50

    def _build_header(self) -> ft.Container:
        """ヘッダーを構築

        Returns:
            ヘッダーコンテナ
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.props.memo_data.title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.LIGHTBULB_OUTLINE,
                                size=16,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Text(
                                f"AIの提案: {self.props.memo_data.suggestion}",
                                size=14,
                                color=ft.Colors.GREY_700,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
        )

    def _build_content_preview(self) -> ft.Container:
        """メモ内容プレビューを構築

        Returns:
            内容プレビューコンテナ
        """
        return ft.Container(
            content=ft.Text(
                self.props.memo_data.content,
                size=14,
                color=ft.Colors.GREY_600,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    def _build_content(self) -> ft.Container:
        """カードコンテンツを構築

        Returns:
            コンテンツコンテナ
        """
        header = self._build_header()
        content_preview = self._build_content_preview()
        action_buttons = self._build_action_buttons()

        return ft.Container(
            content=ft.Column(
                controls=[header, content_preview, action_buttons],
                spacing=12,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )

    def _build_action_buttons(self) -> ft.Container:
        """アクションボタンを構築

        Returns:
            アクションボタンコンテナ
        """
        # タスクにするボタン
        create_task_button = ft.ElevatedButton(
            text="タスクにする",
            icon=ft.Icons.ADD_TASK,
            on_click=lambda _: self._handle_action("create_task"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600
                if self.props.memo_data.selected_action == "create_task"
                else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.memo_data.selected_action == "create_task" else ft.Colors.GREY_800,
            ),
        )

        # 資料として保存ボタン
        archive_button = ft.ElevatedButton(
            text="資料として保存",
            icon=ft.Icons.ARCHIVE_OUTLINED,
            on_click=lambda _: self._handle_action("archive"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600 if self.props.memo_data.selected_action == "archive" else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.memo_data.selected_action == "archive" else ft.Colors.GREY_800,
            ),
        )

        # スキップボタン
        skip_button = ft.ElevatedButton(
            text="スキップ",
            on_click=lambda _: self._handle_action("skip"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600 if self.props.memo_data.selected_action == "skip" else ft.Colors.WHITE,
                color=ft.Colors.WHITE if self.props.memo_data.selected_action == "skip" else ft.Colors.GREY_800,
            ),
        )

        return ft.Container(
            content=ft.ResponsiveRow(
                controls=[
                    ft.Container(create_task_button, col={"sm": 12, "md": 4}),
                    ft.Container(archive_button, col={"sm": 12, "md": 4}),
                    ft.Container(skip_button, col={"sm": 12, "md": 4}),
                ],
                spacing=8,
            ),
        )

    def _handle_action(self, action: MemoAction) -> None:
        """アクション選択処理

        Args:
            action: 選択されたアクション
        """
        if self.props.on_action_selected:
            try:
                self.props.on_action_selected(self.props.memo_data.memo_id, action)
            except Exception:
                logger.exception(f"アクション選択処理に失敗: {action}")
                raise

    def set_selected_action(self, action: MemoAction) -> None:
        """選択されたアクションを更新

        Args:
            action: 新しいアクション
        """
        new_data = UnprocessedMemoData(
            memo_id=self.props.memo_data.memo_id,
            title=self.props.memo_data.title,
            content=self.props.memo_data.content,
            suggestion=self.props.memo_data.suggestion,
            selected_action=action,
        )
        self.props = UnprocessedMemoCardProps(
            memo_data=new_data,
            on_action_selected=self.props.on_action_selected,
        )
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        self.content = self._build_content()

        try:
            self.update()
        except AssertionError:
            logger.debug("未処理メモカードが未マウント: update()をスキップ")
