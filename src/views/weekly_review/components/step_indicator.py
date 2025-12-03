"""週次レビュー用ステップインジケーター

ウィザードの進捗を視覚的に表示するコンポーネント。
"""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft
from loguru import logger


@dataclass(frozen=True, slots=True)
class StepIndicatorProps:
    """ステップインジケーターのプロパティ

    Attributes:
        current_step: 現在のステップ番号 (1-based)
        total_steps: 全ステップ数
        step_labels: 各ステップのラベル
        on_step_click: ステップクリック時のコールバック (step番号を引数に取る)
    """

    current_step: int
    total_steps: int
    step_labels: list[str]
    on_step_click: Callable[[int], None] | None = None


class StepIndicator(ft.Container):
    """ステップインジケーターコンポーネント

    進捗バーと各ステップのラベルを表示。
    """

    def __init__(self, props: StepIndicatorProps) -> None:
        """ステップインジケーターを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props

        # プログレスバー
        progress = (self.props.current_step / self.props.total_steps) * 100
        progress_bar = ft.ProgressBar(
            value=progress / 100,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.BLUE_100,
            height=8,
        )

        # ステップ情報
        current_label = (
            self.props.step_labels[self.props.current_step - 1]
            if 0 < self.props.current_step <= len(self.props.step_labels)
            else ""
        )

        step_info = ft.Row(
            controls=[
                ft.Text(
                    f"ステップ {self.props.current_step} / {self.props.total_steps}",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Text(
                    current_label,
                    size=14,
                    color=ft.Colors.GREY_600,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.content = ft.Column(
            controls=[step_info, progress_bar],
            spacing=8,
        )
        self.padding = ft.padding.symmetric(vertical=8)

    def set_props(self, new_props: StepIndicatorProps) -> None:
        """プロパティを更新して再描画

        Args:
            new_props: 新しいプロパティ
        """
        self.props = new_props
        self._rebuild()

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        # プログレスバー
        progress = (self.props.current_step / self.props.total_steps) * 100
        progress_bar = ft.ProgressBar(
            value=progress / 100,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.BLUE_100,
            height=8,
        )

        # ステップ情報
        current_label = (
            self.props.step_labels[self.props.current_step - 1]
            if 0 < self.props.current_step <= len(self.props.step_labels)
            else ""
        )

        step_info = ft.Row(
            controls=[
                ft.Text(
                    f"ステップ {self.props.current_step} / {self.props.total_steps}",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Text(
                    current_label,
                    size=14,
                    color=ft.Colors.GREY_600,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.content = ft.Column(
            controls=[step_info, progress_bar],
            spacing=8,
        )

        try:
            self.update()
        except AssertionError:
            logger.debug("ステップインジケーターが未マウント: update()をスキップ")
