"""バリデーション機能

フォームフィールドで使用するバリデーションルールと
バリデーター関数を提供。
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class ValidationRule:
    """バリデーションルールの定義。

    よく使用されるバリデーションルールを静的メソッドとして提供。
    """

    @staticmethod
    def required(value: str) -> tuple[bool, str]:
        """必須チェック。

        Args:
            value: 検証する値

        Returns:
            バリデーション結果のタプル（成功/失敗, エラーメッセージ）
        """
        if not value.strip():
            return False, "この項目は必須です"
        return True, ""

    @staticmethod
    def min_length(min_len: int) -> Callable[[str], tuple[bool, str]]:
        """最小文字数チェック。

        Args:
            min_len: 最小文字数

        Returns:
            バリデーション関数
        """

        def validator(value: str) -> tuple[bool, str]:
            if len(value) < min_len:
                return False, f"最低{min_len}文字以上入力してください"
            return True, ""

        return validator

    @staticmethod
    def max_length(max_len: int) -> Callable[[str], tuple[bool, str]]:
        """最大文字数チェック。

        Args:
            max_len: 最大文字数

        Returns:
            バリデーション関数
        """

        def validator(value: str) -> tuple[bool, str]:
            if len(value) > max_len:
                return False, f"{max_len}文字以下で入力してください"
            return True, ""

        return validator

    @staticmethod
    def email(value: str) -> tuple[bool, str]:
        """メールアドレス形式チェック。

        Args:
            value: 検証する値

        Returns:
            バリデーション結果のタプル
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            return False, "有効なメールアドレスを入力してください"
        return True, ""

    @staticmethod
    def date_format(value: str) -> tuple[bool, str]:
        """日付形式チェック（YYYY-MM-DD）。

        Args:
            value: 検証する値

        Returns:
            バリデーション結果のタプル
        """
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if value and not re.match(pattern, value):
            return False, "YYYY-MM-DD 形式で入力してください"
        return True, ""

    @staticmethod
    def url(value: str) -> tuple[bool, str]:
        """URL形式チェック。

        Args:
            value: 検証する値

        Returns:
            バリデーション結果のタプル
        """
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if value and not re.match(pattern, value):
            return False, "有効なURLを入力してください"
        return True, ""

    @staticmethod
    def color_hex(value: str) -> tuple[bool, str]:
        """カラーコード形式チェック（#RRGGBB）。

        Args:
            value: 検証する値

        Returns:
            バリデーション結果のタプル
        """
        pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        if value and not re.match(pattern, value):
            return False, "#RRGGBB 形式で入力してください"
        return True, ""


class FormValidator:
    """フォームバリデーターのユーティリティクラス。

    複数のバリデーションルールを組み合わせた
    バリデーション関数を生成。
    """

    @staticmethod
    def combine(*validators: Callable[[str], tuple[bool, str]]) -> Callable[[str], tuple[bool, str]]:
        """複数のバリデーターを組み合わせる。

        Args:
            *validators: バリデーター関数のリスト

        Returns:
            組み合わせたバリデーター関数
        """

        def combined_validator(value: str) -> tuple[bool, str]:
            for validator in validators:
                is_valid, error = validator(value)
                if not is_valid:
                    return False, error
            return True, ""

        return combined_validator

    @staticmethod
    def create_task_title_validator() -> Callable[[str], tuple[bool, str]]:
        """タスクタイトル用のバリデーターを作成。

        Returns:
            タスクタイトルバリデーター
        """
        return FormValidator.combine(
            ValidationRule.required,
            ValidationRule.min_length(1),
            ValidationRule.max_length(100),
        )

    @staticmethod
    def create_project_name_validator() -> Callable[[str], tuple[bool, str]]:
        """プロジェクト名用のバリデーターを作成。

        Returns:
            プロジェクト名バリデーター
        """
        return FormValidator.combine(
            ValidationRule.required,
            ValidationRule.min_length(1),
            ValidationRule.max_length(200),
        )

    @staticmethod
    def create_tag_name_validator() -> Callable[[str], tuple[bool, str]]:
        """タグ名用のバリデーターを作成。

        Returns:
            タグ名バリデーター
        """
        return FormValidator.combine(
            ValidationRule.required,
            ValidationRule.min_length(1),
            ValidationRule.max_length(50),
        )

    @staticmethod
    def create_memo_title_validator() -> Callable[[str], tuple[bool, str]]:
        """メモタイトル用のバリデーターを作成。

        Returns:
            メモタイトルバリデーター
        """
        return FormValidator.combine(
            ValidationRule.required,
            ValidationRule.min_length(1),
            ValidationRule.max_length(200),
        )

    @staticmethod
    def create_term_key_validator() -> Callable[[str], tuple[bool, str]]:
        """用語キー用のバリデーターを作成。

        Returns:
            用語キーバリデーター
        """
        return FormValidator.combine(
            ValidationRule.required,
            ValidationRule.min_length(1),
            ValidationRule.max_length(100),
        )
