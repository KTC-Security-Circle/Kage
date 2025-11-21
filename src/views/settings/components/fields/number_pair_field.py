"""NumberPairField component for two numeric values.

Passive component that accepts value pair and callback only.
Useful for window size and position settings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


class NumberPairField(ft.Column):
    """2つの数値入力用のフィールド（サイズ、位置など）。

    受動的なコンポーネント：値ペアとコールバックのみを受け取る。
    """

    def __init__(
        self,
        label: str,
        first_label: str,
        second_label: str,
        values: tuple[int, int],
        on_change: Callable[[int, int], None] | None = None,
    ) -> None:
        """NumberPairFieldを初期化する。

        Args:
            label: フィールド全体のラベル
            first_label: 1つ目の値のラベル
            second_label: 2つ目の値のラベル
            values: 初期値のタプル (first, second)
            on_change: 値変更時のコールバック
        """
        super().__init__()
        self.label = label
        self.first_label = first_label
        self.second_label = second_label
        self.values = values
        self.on_change_callback = on_change

        self.first_field = ft.TextField(
            label=self.first_label,
            value=str(self.values[0]),
            on_change=self._handle_change,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
        )

        self.second_field = ft.TextField(
            label=self.second_label,
            value=str(self.values[1]),
            on_change=self._handle_change,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(self.label, weight=ft.FontWeight.W_500),
                        ft.Row(
                            [self.first_field, self.second_field],
                            spacing=SPACING.md,
                        ),
                    ],
                    spacing=SPACING.sm,
                    tight=True,
                ),
                padding=ft.padding.symmetric(vertical=SPACING.sm),
            )
        ]
        self.tight = True

    def _handle_change(self, _: ft.ControlEvent) -> None:
        """値変更イベントを処理する。

        Args:
            _: イベントオブジェクト (未使用)
        """
        if self.on_change_callback and self.first_field and self.second_field:
            try:
                first = int(self.first_field.value or "0")
                second = int(self.second_field.value or "0")
                self.on_change_callback(first, second)
            except ValueError:
                pass

    def set_values(self, first: int, second: int) -> None:
        """値を設定する。

        Args:
            first: 1つ目の値
            second: 2つ目の値
        """
        if self.first_field and self.second_field:
            self.first_field.value = str(first)
            self.second_field.value = str(second)
            if self.page:
                self.update()
