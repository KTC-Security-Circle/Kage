"""TextField component for string input.

Passive component that accepts value and callback only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


class TextField(ft.Column):
    """文字列入力用のテキストフィールド。

    受動的なコンポーネント：値とコールバックのみを受け取る。
    """

    def __init__(
        self,
        label: str,
        value: str = "",
        on_change: Callable[[str], None] | None = None,
        *,
        password: bool = False,
        multiline: bool = False,
        hint_text: str | None = None,
    ) -> None:
        """TextFieldを初期化する。

        Args:
            label: フィールドのラベル
            value: 初期値
            on_change: 値変更時のコールバック
            password: パスワード入力モードにするか
            multiline: 複数行入力を許可するか
            hint_text: ヒントテキスト
        """
        super().__init__()
        self.label = label
        self.value = value
        self.on_change_callback = on_change
        self.password = password
        self.multiline = multiline
        self.hint_text = hint_text

        self.text_field = ft.TextField(
            label=self.label,
            value=self.value,
            on_change=self._handle_change,
            password=self.password,
            multiline=self.multiline,
            hint_text=self.hint_text,
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=self.text_field,
                padding=ft.padding.symmetric(vertical=SPACING.sm),
            )
        ]
        self.tight = True

    def _handle_change(self, _: ft.ControlEvent) -> None:
        """値変更イベントを処理する。

        Args:
            _: イベントオブジェクト (未使用)
        """
        if self.on_change_callback and self.text_field:
            self.on_change_callback(self.text_field.value or "")

    def set_value(self, value: str) -> None:
        """値を設定する。

        Args:
            value: 新しい値
        """
        if self.text_field:
            self.text_field.value = value
            if self.page:
                self.update()
