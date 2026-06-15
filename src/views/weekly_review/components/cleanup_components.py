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
    completed: bool = False


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
        self._apply_surface_style()

    def _apply_surface_style(self) -> None:
        completed = self.props.task_data.completed
        self.color = ft.Colors.GREY_100 if completed else ft.Colors.YELLOW_50
        self.elevation = 0 if completed else 2

    def _build_header(self) -> ft.Container:
        """ヘッダーを構築

        Returns:
            ヘッダーコンテナ
        """
        status_chip: ft.Control | None = None
        if self.props.task_data.completed:
            status_chip = ft.Chip(
                label=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=14),
                        ft.Text("処理済み", color=ft.Colors.WHITE),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
            )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.props.task_data.title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    status_chip if status_chip else ft.Container(height=0),
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
        if self.props.task_data.completed:
            return self._build_completed_content()
        header = self._build_header()
        action_buttons = self._build_action_buttons()

        return ft.Container(
            content=ft.Column(
                controls=[header, action_buttons],
                spacing=12,
            ),
            padding=ft.padding.only(left=16, right=16, bottom=16),
        )

    def _build_completed_content(self) -> ft.Container:
        message = ft.Text(
            "提案されたサブタスクの対応が完了しました。",
            size=13,
            color=ft.Colors.GREY_700,
        )
        status_row = ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20),
                ft.Text(
                    "処理済み",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.GREEN_700,
                ),
            ],
            spacing=8,
        )
        reason_text = (self.props.task_data.reason or "").strip()
        optional_reason: ft.Control | None = None
        if reason_text:
            optional_reason = ft.Text(
                reason_text,
                size=12,
                color=ft.Colors.GREY_600,
            )
        controls: list[ft.Control] = [
            ft.Text(
                self.props.task_data.title,
                size=16,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.GREY_800,
            ),
            status_row,
            message,
        ]
        if optional_reason is not None:
            controls.append(optional_reason)
        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=8,
            ),
            padding=ft.padding.all(16),
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

        is_subdivide = self.props.task_data.selected_action == "subdivide"
        is_someday = self.props.task_data.selected_action == "someday"
        is_delete = self.props.task_data.selected_action == "delete"

        subdivide_button = ft.ElevatedButton(
            text="細分化する",
            icon=ft.Icons.FORMAT_LIST_BULLETED,
            on_click=lambda _: self._handle_action("subdivide"),
            style=self._choice_button_style(
                is_selected=is_subdivide,
                selected_bg=ft.Colors.BLUE_600,
                default_color=ft.Colors.GREY_800,
            ),
        )

        someday_button = ft.ElevatedButton(
            text="いつか/多分へ",
            icon=ft.Icons.ARCHIVE_OUTLINED,
            on_click=lambda _: self._handle_action("someday"),
            style=self._choice_button_style(
                is_selected=is_someday,
                selected_bg=ft.Colors.BLUE_600,
                default_color=ft.Colors.GREY_800,
            ),
        )

        delete_button = ft.ElevatedButton(
            text="削除する",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=lambda _: self._handle_action("delete"),
            style=self._choice_button_style(
                is_selected=is_delete,
                selected_bg=ft.Colors.RED_600,
                default_color=ft.Colors.RED_600,
                selected_color=ft.Colors.WHITE,
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
        self.set_selected_action(action)
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
            completed=self.props.task_data.completed,
        )
        self.props = ZombieTaskCardProps(
            task_data=new_data,
            on_action_selected=self.props.on_action_selected,
        )
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        self.content = self._build_content()
        self._apply_surface_style()

        try:
            self.update()
        except AssertionError:
            logger.debug("ゾンビタスクカードが未マウント: update()をスキップ")

    @staticmethod
    def _choice_button_style(
        *,
        is_selected: bool,
        selected_bg: str,
        default_color: str,
        selected_color: str = ft.Colors.WHITE,
    ) -> ft.ButtonStyle:
        bgcolor = selected_bg if is_selected else ft.Colors.WHITE
        color = selected_color if is_selected else default_color
        return ft.ButtonStyle(bgcolor=bgcolor, color=color)


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
    completed: bool = False


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
        self._apply_surface_style()

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
        if self.props.memo_data.completed:
            return self._build_completed_content()
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

        question_text = ft.Text("どうしますか?", size=14, color=ft.Colors.GREY_700)

        return ft.Container(
            content=ft.Column(
                controls=[
                    question_text,
                    ft.Container(
                        content=ft.ResponsiveRow(
                            controls=[
                                ft.Container(create_task_button, col={"sm": 12, "md": 4}),
                                ft.Container(archive_button, col={"sm": 12, "md": 4}),
                                ft.Container(skip_button, col={"sm": 12, "md": 4}),
                            ],
                            spacing=8,
                        ),
                    ),
                ],
                spacing=6,
            ),
        )

    def _build_completed_content(self) -> ft.Container:
        status_row = ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20),
                ft.Text("処理済み", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
            ],
            spacing=8,
        )
        message = ft.Text(
            "このメモは整理済みです。必要に応じて他の項目を確認してください。",
            size=13,
            color=ft.Colors.GREY_700,
        )
        return ft.Container(
            content=ft.Column(
                controls=[status_row, message],
                spacing=8,
            ),
            padding=ft.padding.all(16),
        )

    def _handle_action(self, action: MemoAction) -> None:
        """アクション選択処理

        Args:
            action: 選択されたアクション
        """
        if self.props.memo_data.completed:
            return
        self.set_selected_action(action)
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
            completed=self.props.memo_data.completed,
        )
        self.props = UnprocessedMemoCardProps(
            memo_data=new_data,
            on_action_selected=self.props.on_action_selected,
        )
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        self.content = self._build_content()

        self._apply_surface_style()

        try:
            self.update()
        except AssertionError:
            logger.debug("未処理メモカードが未マウント: update()をスキップ")

    def _apply_surface_style(self) -> None:
        if self.props.memo_data.completed:
            self.color = ft.Colors.GREY_100
            self.elevation = 0
        else:
            self.color = ft.Colors.BLUE_50
            self.elevation = 2
