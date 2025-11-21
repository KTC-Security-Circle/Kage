"""BooleanField component for toggle/switch input.

Passive component that accepts value and callback only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


class BooleanField(ft.Column):
    """トグル/スイッチ用のフィールド。

    受動的なコンポーネント：値とコールバックのみを受け取る。
    """

    def __init__(
        self,
        label: str,
        *,
        value: bool,
        on_change: Callable[[bool], None] | None = None,
    ) -> None:
        """BooleanFieldを初期化する。

        Args:
            label: フィールドのラベル
            value: 初期値（キーワード引数）
            on_change: 値変更時のコールバック
        """
        super().__init__()
        self.label = label
        self.value = value
        self.on_change_callback = on_change

        self.switch = ft.Switch(
            label=self.label,
            value=self.value,
            on_change=self._handle_change,
        )

        self.controls = [
            ft.Container(
                content=self.switch,
                padding=ft.padding.symmetric(vertical=SPACING.sm),
            )
        ]
        self.tight = True

    def _handle_change(self, _: ft.ControlEvent) -> None:
        """値変更イベントを処理する。

        Args:
            _: イベントオブジェクト (未使用)
        """
        if self.on_change_callback and self.switch:
            self.on_change_callback(self.switch.value or False)

    def set_value(self, *, value: bool) -> None:
        """値を設定する。

        Args:
            value: 新しい値（キーワード引数）
        """
        if self.switch:
            self.switch.value = value
            if self.page:
                self.update()
