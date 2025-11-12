"""ChoiceField component for dropdown selection.

Passive component that accepts options and callback only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


class ChoiceField(ft.Column):
    """ドロップダウン選択用のフィールド。

    受動的なコンポーネント：選択肢、選択値、コールバックのみを受け取る。
    """

    def __init__(
        self,
        label: str,
        options: list[tuple[str, str]],
        selected: str = "",
        on_select: Callable[[str], None] | None = None,
    ) -> None:
        """ChoiceFieldを初期化する。

        Args:
            label: フィールドのラベル
            options: (value, label) のタプルのリスト
            selected: 選択中の値
            on_select: 選択変更時のコールバック
        """
        super().__init__()
        self.label = label
        self.options = options
        self.selected = selected
        self.on_select_callback = on_select

        self.dropdown = ft.Dropdown(
            label=self.label,
            options=[ft.dropdown.Option(key=value, text=label) for value, label in self.options],
            value=self.selected,
            on_change=self._handle_change,
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=self.dropdown,
                padding=ft.padding.symmetric(vertical=SPACING.sm),
            )
        ]
        self.tight = True

    def _handle_change(self, _: ft.ControlEvent) -> None:
        """選択変更イベントを処理する。

        Args:
            _: イベントオブジェクト (未使用)
        """
        if self.on_select_callback and self.dropdown:
            self.on_select_callback(self.dropdown.value or "")

    def set_value(self, value: str) -> None:
        """選択値を設定する。

        Args:
            value: 新しい選択値
        """
        if self.dropdown:
            self.dropdown.value = value
            if self.page:
                self.update()

    def set_options(self, options: list[tuple[str, str]], selected: str | None = None) -> None:
        """選択肢を更新する。

        Args:
            options: (value, label) のタプルのリスト
            selected: 新しい選択値（Noneの場合は現在の値を維持）
        """
        if self.dropdown:
            self.dropdown.options = [ft.dropdown.Option(key=value, text=label) for value, label in options]
            if selected is not None:
                self.dropdown.value = selected
            self.update()
