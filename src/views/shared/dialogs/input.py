"""入力ダイアログコンポーネント。

テキスト入力、選択等のユーザー入力を受け取るダイアログです。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from views.theme import SPACING

from .base import BaseFormDialog

if TYPE_CHECKING:
    from collections.abc import Callable


class InputDialog(BaseFormDialog):
    """単一テキスト入力ダイアログクラス。

    名前の変更、新規作成等で単一のテキスト入力を受け取ります。
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        label: str,
        *,
        initial_value: str = "",
        on_result: Callable[[dict[str, Any] | None], None] | None = None,
    ) -> None:
        """InputDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            title: ダイアログのタイトル
            label: 入力フィールドのラベル
            initial_value: 初期値
            placeholder: プレースホルダーテキスト
            max_length: 最大文字数
            required: 必須入力かどうか
            multiline: 複数行入力かどうか
            on_result: 結果を受け取るコールバック関数
        """
        self.label = label
        self.initial_value = initial_value
        # 説明フィールドの場合は特別な設定
        is_description = "説明" in label
        self.placeholder = "説明を入力してください（任意）" if is_description else f"{label}を入力してください"
        self.max_length = 1000  # デフォルト値
        self.multiline = is_description  # 説明の場合はマルチライン

        # 入力フィールドを作成
        self.text_field = ft.TextField(
            label=label,
            value=initial_value,
            hint_text=self.placeholder,
            max_length=self.max_length,
            multiline=self.multiline,
            min_lines=3 if self.multiline else 1,
            max_lines=5 if self.multiline else 1,
            autofocus=True,
        )

        super().__init__(page, title, on_result=on_result)

        # フォームフィールドを追加
        self._add_form_field("text", self.text_field)

    def _build_content(self) -> ft.Control:
        """ダイアログのコンテンツを構築する。

        Returns:
            入力フィールドを含むコンテンツ
        """
        return ft.Container(
            content=ft.Column(
                [self.text_field],
                spacing=SPACING.md,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.sm),
            width=400,
        )

    def _build_actions(self) -> list[ft.Control]:
        """ダイアログのアクションボタンを構築する。

        Returns:
            キャンセルとOKボタンのリスト
        """
        return [
            self._create_button(
                "キャンセル",
                on_click=lambda _: self._on_cancel(),
            ),
            self._create_button(
                "OK",
                on_click=lambda _: self._on_form_submit(),
                is_primary=True,
            ),
        ]

    def _validate_form(self) -> bool:
        """フォームのバリデーションを実行する。

        Returns:
            バリデーション成功時True
        """
        self._validation_errors.clear()

        value = self.text_field.value or ""

        # 必須チェック（説明フィールドなど一部は任意にする必要がある場合は
        # プレースホルダーで判断）
        is_required = "任意" not in self.placeholder
        if is_required and not value.strip():
            self._validation_errors["text"] = f"{self.label}は必須です"

        # 長さチェック
        if self.max_length and len(value) > self.max_length:
            self._validation_errors["text"] = f"{self.label}は{self.max_length}文字以内で入力してください"

        return len(self._validation_errors) == 0

    def _get_form_data(self) -> dict[str, Any]:
        """フォームデータを取得する。

        Returns:
            入力されたテキストを含む辞書
        """
        return {
            "text": self.text_field.value or "",
        }


class CreateItemDialog(InputDialog):
    """新規項目作成ダイアログ。

    プロジェクト、タスク、タグ等の新規作成時に使用する専用ダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        item_type: str,
        *,
        on_result: Callable[[dict[str, Any] | None], None] | None = None,
    ) -> None:
        """CreateItemDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            item_type: 作成する項目の種類（プロジェクト、タスク、タグ等）
            on_result: 結果を受け取るコールバック関数
        """
        super().__init__(
            page,
            title=f"{item_type}の作成",
            label=f"{item_type}名",
            on_result=on_result,
        )


class RenameItemDialog(InputDialog):
    """項目名変更ダイアログ。

    既存項目の名前変更時に使用する専用ダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        item_type: str,
        current_name: str,
        *,
        on_result: Callable[[dict[str, Any] | None], None] | None = None,
    ) -> None:
        """RenameItemDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            item_type: 変更する項目の種類
            current_name: 現在の名前
            on_result: 結果を受け取るコールバック関数
        """
        super().__init__(
            page,
            title=f"{item_type}名の変更",
            label=f"新しい{item_type}名",
            initial_value=current_name,
            on_result=on_result,
        )


class DescriptionDialog(InputDialog):
    """説明入力ダイアログ。

    タスクやプロジェクトの説明を入力する専用ダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        item_type: str,
        *,
        initial_description: str = "",
        on_result: Callable[[dict[str, Any] | None], None] | None = None,
    ) -> None:
        """DescriptionDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            item_type: 説明を編集する項目の種類
            initial_description: 初期の説明文
            on_result: 結果を受け取るコールバック関数
        """
        super().__init__(
            page,
            title=f"{item_type}の説明",
            label="説明",
            initial_value=initial_description,
            on_result=on_result,
        )
