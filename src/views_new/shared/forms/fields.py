"""具体的なフォームフィールド実装

各種入力タイプに対応した具体的なフォームフィールドクラス。
BaseFormFieldを継承し、Fletコントロールと統合。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

from .base import BaseFormField


class TextFieldConfig:
    """テキストフィールドの設定を管理するデータクラス。"""

    def __init__(
        self,
        hint_text: str = "",
        *,
        max_length: int | None = None,
        multiline: bool = False,
        password: bool = False,
    ) -> None:
        """設定を初期化。

        Args:
            hint_text: ヒントテキスト
            max_length: 最大文字数
            multiline: 複数行入力かどうか
            password: パスワード入力かどうか
        """
        self.hint_text = hint_text
        self.max_length = max_length
        self.multiline = multiline
        self.password = password


class TextFormField(BaseFormField):
    """テキスト入力フィールド。

    一般的なテキスト入力に使用。
    """

    def __init__(
        self,
        name: str,
        label: str,
        config: TextFieldConfig | None = None,
        *,
        required: bool = False,
        validators: list[Callable[[str], tuple[bool, str]]] | None = None,
    ) -> None:
        """テキストフィールドを初期化。

        Args:
            name: フィールド名
            label: 表示ラベル
            config: フィールドの設定
            required: 必須項目かどうか
            validators: バリデーター関数のリスト
        """
        super().__init__(name, label, required=required, validators=validators)
        self._config = config or TextFieldConfig()
        self._text_field = ft.TextField(
            label=label,
            hint_text=self._config.hint_text,
            multiline=self._config.multiline,
            password=self._config.password,
            max_length=self._config.max_length,
            on_change=self._on_change,
            on_blur=self._on_blur,
        )

    def _create_control(self) -> ft.Control:
        """Fletコントロールを作成。

        Returns:
            作成されたコントロール
        """
        return self._text_field

    def get_value(self) -> str:
        """現在の値を取得。

        Returns:
            現在の値
        """
        return self._text_field.value or ""

    def set_value(self, value: str | None) -> None:
        """値を設定。

        Args:
            value: 設定する値
        """
        self._text_field.value = str(value) if value is not None else ""
        self._update_control()

    def set_error(self, error: str) -> None:
        """エラーメッセージを設定。

        Args:
            error: エラーメッセージ
        """
        self._text_field.error_text = error if error else None
        self._update_control()

    def _on_change(self, _: ft.ControlEvent) -> None:
        """値変更時のハンドラー。"""
        self._notify_change()

    def _on_blur(self, _: ft.ControlEvent) -> None:
        """フォーカス失時のハンドラー。"""
        self.validate()


class DropdownFormField(BaseFormField):
    """ドロップダウン選択フィールド。

    選択肢から一つを選択する入力タイプ。
    """

    def __init__(
        self,
        name: str,
        label: str,
        options: list[tuple[str, str]],
        *,
        hint_text: str = "選択してください",
        required: bool = False,
        validators: list[Callable[[str], tuple[bool, str]]] | None = None,
    ) -> None:
        """ドロップダウンフィールドを初期化。

        Args:
            name: フィールド名
            label: 表示ラベル
            options: 選択肢（値, 表示名）のタプルリスト
            hint_text: ヒントテキスト
            required: 必須項目かどうか
            validators: バリデーター関数のリスト
        """
        super().__init__(name, label, required=required, validators=validators)
        self._options = options
        self._dropdown = ft.Dropdown(
            label=label,
            hint_text=hint_text,
            options=[ft.dropdown.Option(key=value, text=text) for value, text in options],
            on_change=self._on_change,
        )

    def _create_control(self) -> ft.Control:
        """Fletコントロールを作成。

        Returns:
            作成されたコントロール
        """
        return self._dropdown

    def get_value(self) -> str:
        """現在の値を取得。

        Returns:
            現在の値
        """
        return self._dropdown.value or ""

    def set_value(self, value: str | None) -> None:
        """値を設定。

        Args:
            value: 設定する値
        """
        self._dropdown.value = str(value) if value is not None else None
        self._update_control()

    def set_error(self, error: str) -> None:
        """エラーメッセージを設定。

        Args:
            error: エラーメッセージ
        """
        self._dropdown.error_text = error if error else None
        self._update_control()

    def _on_change(self, _: ft.ControlEvent) -> None:
        """値変更時のハンドラー。"""
        self._notify_change()


class DateFormField(BaseFormField):
    """日付入力フィールド。

    日付の入力に使用。
    """

    def __init__(
        self,
        name: str,
        label: str,
        *,
        required: bool = False,
        validators: list[Callable[[str], tuple[bool, str]]] | None = None,
    ) -> None:
        """日付フィールドを初期化。

        Args:
            name: フィールド名
            label: 表示ラベル
            required: 必須項目かどうか
            validators: バリデーター関数のリスト
        """
        super().__init__(name, label, required=required, validators=validators)
        self._text_field = ft.TextField(
            label=label,
            hint_text="YYYY-MM-DD",
            on_change=self._on_change,
            on_blur=self._on_blur,
        )

    def _create_control(self) -> ft.Control:
        """Fletコントロールを作成。

        Returns:
            作成されたコントロール
        """
        return self._text_field

    def get_value(self) -> str:
        """現在の値を取得。

        Returns:
            現在の値
        """
        return self._text_field.value or ""

    def set_value(self, value: str | None) -> None:
        """値を設定。

        Args:
            value: 設定する値
        """
        self._text_field.value = str(value) if value is not None else ""
        self._update_control()

    def set_error(self, error: str) -> None:
        """エラーメッセージを設定。

        Args:
            error: エラーメッセージ
        """
        self._text_field.error_text = error if error else None
        self._update_control()

    def _on_change(self, _: ft.ControlEvent) -> None:
        """値変更時のハンドラー。"""
        self._notify_change()

    def _on_blur(self, _: ft.ControlEvent) -> None:
        """フォーカス失時のハンドラー。"""
        self.validate()


class SwitchFormField(BaseFormField):
    """スイッチ（トグル）フィールド。

    オン/オフの二択入力に使用。
    """

    def __init__(
        self,
        name: str,
        label: str,
        *,
        required: bool = False,
        validators: list[Callable[[str], tuple[bool, str]]] | None = None,
    ) -> None:
        """スイッチフィールドを初期化。

        Args:
            name: フィールド名
            label: 表示ラベル
            required: 必須項目かどうか
            validators: バリデーター関数のリスト
        """
        super().__init__(name, label, required=required, validators=validators)
        self._switch = ft.Switch(
            label=label,
            on_change=self._on_change,
        )

    def _create_control(self) -> ft.Control:
        """Fletコントロールを作成。

        Returns:
            作成されたコントロール
        """
        return self._switch

    def get_value(self) -> bool:
        """現在の値を取得。

        Returns:
            現在の値（真偽値）
        """
        return self._switch.value or False

    def set_value(self, *, value: bool | str | None) -> None:
        """値を設定。

        Args:
            value: 設定する値（keyword-only引数）
        """
        self._switch.value = bool(value) if value is not None else False
        self._update_control()

    def set_error(self, error: str) -> None:
        """エラーメッセージを設定。

        Args:
            error: エラーメッセージ
        """
        # スイッチはエラー表示をサポートしていないため、何もしない

    def _on_change(self, _: ft.ControlEvent) -> None:
        """値変更時のハンドラー。"""
        self._notify_change()


class ColorFormField(BaseFormField):
    """カラー選択フィールド。

    色の選択に使用。
    """

    def __init__(
        self,
        name: str,
        label: str,
        *,
        required: bool = False,
        validators: list[Callable[[str], tuple[bool, str]]] | None = None,
    ) -> None:
        """カラーフィールドを初期化。

        Args:
            name: フィールド名
            label: 表示ラベル
            required: 必須項目かどうか
            validators: バリデーター関数のリスト
        """
        super().__init__(name, label, required=required, validators=validators)
        self._text_field = ft.TextField(
            label=label,
            hint_text="#RRGGBB",
            on_change=self._on_change,
            on_blur=self._on_blur,
        )

    def _create_control(self) -> ft.Control:
        """Fletコントロールを作成。

        Returns:
            作成されたコントロール
        """
        return ft.Row(
            controls=[
                self._text_field,
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=self.get_value() or "#ffffff",
                    border_radius=5,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                ),
            ],
            spacing=10,
        )

    def get_value(self) -> str:
        """現在の値を取得。

        Returns:
            現在の値
        """
        return self._text_field.value or ""

    def set_value(self, value: str | None) -> None:
        """値を設定。

        Args:
            value: 設定する値
        """
        self._text_field.value = str(value) if value is not None else ""
        self._update_control()

    def set_error(self, error: str) -> None:
        """エラーメッセージを設定。

        Args:
            error: エラーメッセージ
        """
        self._text_field.error_text = error if error else None
        self._update_control()

    def _on_change(self, _: ft.ControlEvent) -> None:
        """値変更時のハンドラー。"""
        self._notify_change()

    def _on_blur(self, _: ft.ControlEvent) -> None:
        """フォーカス失時のハンドラー。"""
        self.validate()
