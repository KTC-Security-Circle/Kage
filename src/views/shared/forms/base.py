"""フォーム基盤クラス

全フォームの基底クラスと共通フィールドインターフェース。
バリデーション、エラー表示、フォーカス管理を統一的に提供。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


class BaseFormField(ABC):
    """フォームフィールドの基底クラス。

    全てのフォームフィールドが実装すべきインターフェース。
    値の取得・設定、バリデーション、エラー表示を標準化。
    """

    def __init__(
        self,
        label: str,
        value: str = "",
        *,
        required: bool = False,
        validator: Callable[[str], tuple[bool, str]] | None = None,
        help_text: str = "",
    ) -> None:
        """BaseFormFieldを初期化する。

        Args:
            label: フィールドのラベル
            value: 初期値
            required: 必須フィールドかどうか
            validator: バリデーション関数
            help_text: ヘルプテキスト
        """
        self.label = label
        self.value = value
        self.required = required
        self.validator = validator
        self.help_text = help_text
        self.error_message = ""
        self._control: ft.Control | None = None

    @abstractmethod
    def build(self) -> ft.Control:
        """フィールドのUIコントロールを構築する。

        Returns:
            Fletコントロール
        """

    def get_value(self) -> str:
        """フィールドの現在値を取得する。

        Returns:
            現在の値
        """
        return self.value

    def set_value(self, value: str) -> None:
        """フィールドの値を設定する。

        Args:
            value: 設定する値
        """
        self.value = value
        if self._control:
            self._update_control_value(value)

    @abstractmethod
    def _update_control_value(self, value: str) -> None:
        """コントロールの値を更新する。

        Args:
            value: 新しい値
        """

    def validate(self) -> bool:
        """フィールドのバリデーションを実行する。

        Returns:
            バリデーション成功の場合True
        """
        self.error_message = ""

        # 必須チェック
        if self.required and not self.value.strip():
            self.error_message = f"{self.label}は必須です"
            return False

        # カスタムバリデーション
        if self.validator:
            is_valid, error = self.validator(self.value)
            if not is_valid:
                self.error_message = error
                return False

        return True

    def show_error(self, message: str) -> None:
        """エラーメッセージを表示する。

        Args:
            message: エラーメッセージ
        """
        self.error_message = message
        if self._control:
            self._update_error_display()

    @abstractmethod
    def _update_error_display(self) -> None:
        """エラー表示を更新する。"""


class BaseForm:
    """フォームの基底クラス。

    複数のフィールドを管理し、一括バリデーション、
    データ取得、エラー表示機能を提供。
    """

    def __init__(self) -> None:
        """BaseFormを初期化する。"""
        self.fields: dict[str, BaseFormField] = {}
        self.on_submit: Callable[[dict[str, str]], None] | None = None
        self.on_cancel: Callable[[], None] | None = None

    def add_field(self, name: str, field: BaseFormField) -> None:
        """フィールドを追加する。

        Args:
            name: フィールド名
            field: フィールドインスタンス
        """
        self.fields[name] = field

    def get_field(self, name: str) -> BaseFormField | None:
        """フィールドを取得する。

        Args:
            name: フィールド名

        Returns:
            フィールドインスタンス
        """
        return self.fields.get(name)

    def validate_all(self) -> bool:
        """全フィールドのバリデーションを実行する。

        Returns:
            全フィールドが有効な場合True
        """
        is_valid = True
        for field in self.fields.values():
            if not field.validate():
                is_valid = False
        return is_valid

    def get_data(self) -> dict[str, str]:
        """全フィールドのデータを取得する。

        Returns:
            フィールド名をキーとするデータ辞書
        """
        return {name: field.get_value() for name, field in self.fields.items()}

    def set_data(self, data: dict[str, str]) -> None:
        """フォームにデータを設定する。

        Args:
            data: 設定するデータ
        """
        for name, value in data.items():
            field = self.get_field(name)
            if field:
                field.set_value(value=value)

    def clear_errors(self) -> None:
        """全フィールドのエラーをクリアする。"""
        for field in self.fields.values():
            field.error_message = ""

    def build_form_controls(self) -> list[ft.Control]:
        """フォームの全コントロールを取得。

        Returns:
            フォームコントロールのリスト
        """
        return [field.build() for field in self.fields.values()]

    def handle_submit(self) -> None:
        """フォーム送信を処理する。"""
        if self.validate_all() and self.on_submit:
            data = self.get_data()
            self.on_submit(data)

    def handle_cancel(self) -> None:
        """フォームキャンセルを処理する。"""
        if self.on_cancel:
            self.on_cancel()
