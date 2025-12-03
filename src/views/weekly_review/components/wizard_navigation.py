"""週次レビューウィザードのナビゲーションボタン

前へ/次へボタンを提供するコンポーネント。
"""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft
from loguru import logger


@dataclass(frozen=True, slots=True)
class WizardNavigationProps:
    """ウィザードナビゲーションのプロパティ

    Attributes:
        current_step: 現在のステップ番号 (1-based)
        total_steps: 全ステップ数
        on_prev: 前へボタンのコールバック
        on_next: 次へボタンのコールバック
        next_label: 次へボタンのラベル (デフォルト: "次へ")
        prev_label: 前へボタンのラベル (デフォルト: "戻る")
        show_prev: 前へボタンを表示するか
        show_next: 次へボタンを表示するか
    """

    current_step: int
    total_steps: int
    on_prev: Callable[[], None] | None = None
    on_next: Callable[[], None] | None = None
    next_label: str = "次へ"
    prev_label: str = "戻る"
    show_prev: bool = True
    show_next: bool = True


class WizardNavigation(ft.Container):
    """ウィザードナビゲーションコンポーネント

    前へ/次へボタンを表示。
    """

    def __init__(self, props: WizardNavigationProps) -> None:
        """ウィザードナビゲーションを初期化

        Args:
            props: コンポーネントプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()
        self.padding = ft.padding.symmetric(vertical=16)

    def _handle_prev(self) -> None:
        """前へボタンのクリック処理"""
        if self.props.on_prev:
            try:
                self.props.on_prev()
            except Exception:
                logger.exception("前へボタンの処理に失敗")
                raise

    def _handle_next(self) -> None:
        """次へボタンのクリック処理"""
        if self.props.on_next:
            try:
                self.props.on_next()
            except Exception:
                logger.exception("次へボタンの処理に失敗")
                raise

    def set_props(self, new_props: WizardNavigationProps) -> None:
        """プロパティを更新して再描画

        Args:
            new_props: 新しいプロパティ
        """
        self.props = new_props
        self._rebuild()

    def _build_content(self) -> ft.Row:
        """ナビゲーションコンテンツを構築

        Returns:
            構築されたコンテンツ
        """
        controls: list[ft.Control] = []

        # 前へボタン
        if self.props.show_prev and self.props.current_step > 1:
            prev_button = ft.OutlinedButton(
                text=self.props.prev_label,
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: self._handle_prev(),
            )
            controls.append(prev_button)

        # 次へボタン
        if self.props.show_next and self.props.current_step < self.props.total_steps:
            next_button = ft.ElevatedButton(
                text=self.props.next_label,
                icon=ft.Icons.CHEVRON_RIGHT,
                icon_color=ft.Colors.WHITE,
                on_click=lambda _: self._handle_next(),
            )
            controls.append(next_button)
        elif self.props.show_next and self.props.current_step == self.props.total_steps:
            # 最終ステップの場合
            finish_button = ft.ElevatedButton(
                text="完了",
                icon=ft.Icons.CHECK_CIRCLE,
                icon_color=ft.Colors.WHITE,
                on_click=lambda _: self._handle_next(),
            )
            controls.append(finish_button)

        return ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )

    def _rebuild(self) -> None:
        """コンポーネントを再構築"""
        self.content = self._build_content()

        try:
            self.update()
        except AssertionError:
            logger.debug("ウィザードナビゲーションが未マウント: update()をスキップ")
