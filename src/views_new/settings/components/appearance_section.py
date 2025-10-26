"""外観設定コンポーネント。

テーマ選択等の外観に関する設定UIを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views_new.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable

    from settings.models import AppSettings, EditableAppSettings


class AppearanceSection(ft.Column):
    """外観設定セクション。

    テーマ（ライト/ダーク）の選択機能を提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        on_change: Callable[[], None],
    ) -> None:
        """AppearanceSectionを初期化する。

        Args:
            page: Fletページオブジェクト
            on_change: 設定変更時のコールバック
        """
        super().__init__()

        self.page = page
        self.on_change = on_change

        # テーマ選択
        self.theme_radio = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value="light", label="ライトテーマ"),
                    ft.Radio(value="dark", label="ダークテーマ"),
                ]
            ),
            on_change=self._on_theme_changed,
        )

        # ユーザー名設定
        self.user_name_field = ft.TextField(
            label="ユーザー名",
            hint_text="表示名を入力（任意）",
            on_change=self._on_user_name_changed,
        )

        self.controls = [
            ft.Text("テーマ", size=16, weight=ft.FontWeight.BOLD),
            self.theme_radio,
            ft.Container(height=SPACING.md),
            ft.Text("ユーザー設定", size=16, weight=ft.FontWeight.BOLD),
            self.user_name_field,
        ]

        self.spacing = SPACING.md

    def _on_theme_changed(self, _: ft.ControlEvent) -> None:
        """テーマ選択が変更された時の処理。"""
        self.on_change()

    def _on_user_name_changed(self, _: ft.ControlEvent) -> None:
        """ユーザー名が変更された時の処理。"""
        self.on_change()

    def apply_settings(self, settings: EditableAppSettings) -> None:
        """設定値を適用する。

        Args:
            settings: 編集可能な設定オブジェクト
        """
        # テーマ設定
        settings.user.theme = self.theme_radio.value or "light"

        # ユーザー名設定
        settings.user.user_name = self.user_name_field.value or ""

    def reset_to_settings(self, settings: AppSettings) -> None:
        """現在の設定値にリセットする。

        Args:
            settings: 現在の設定オブジェクト
        """
        # テーマ設定
        self.theme_radio.value = settings.user.theme

        # ユーザー名設定
        self.user_name_field.value = settings.user.user_name

        if hasattr(self.page, "update"):
            self.page.update()
