"""ウィンドウ設定コンポーネント。

ウィンドウサイズと位置の設定UIを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable

    from settings.models import AppSettings, EditableAppSettings


class WindowSection(ft.Column):
    """ウィンドウ設定セクション。

    ウィンドウサイズと位置の設定機能を提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        on_change: Callable[[], None],
    ) -> None:
        """WindowSectionを初期化する。

        Args:
            page: Fletページオブジェクト
            on_change: 設定変更時のコールバック
        """
        super().__init__()

        self.page = page
        self.on_change = on_change

        # ウィンドウサイズ設定
        self.width_field = ft.TextField(
            label="幅",
            hint_text="1280",
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            on_change=self._on_value_changed,
        )

        self.height_field = ft.TextField(
            label="高さ",
            hint_text="720",
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            on_change=self._on_value_changed,
        )

        # ウィンドウ位置設定
        self.x_field = ft.TextField(
            label="X座標",
            hint_text="100",
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            on_change=self._on_value_changed,
        )

        self.y_field = ft.TextField(
            label="Y座標",
            hint_text="100",
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            on_change=self._on_value_changed,
        )

        # 現在のウィンドウサイズを取得ボタン
        self.get_current_button = ft.OutlinedButton(
            text="現在のサイズを取得",
            icon=ft.Icons.FULLSCREEN,
            on_click=self._on_get_current_size,
        )

        self.controls = [
            ft.Text("ウィンドウサイズ", size=16, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    self.width_field,
                    ft.Text("×", size=16),
                    self.height_field,
                    ft.Text("px", size=14),
                ],
                spacing=SPACING.sm,
            ),
            ft.Container(height=SPACING.md),
            ft.Text("ウィンドウ位置", size=16, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    self.x_field,
                    ft.Text(",", size=16),
                    self.y_field,
                    ft.Text("px", size=14),
                ],
                spacing=SPACING.sm,
            ),
            ft.Container(height=SPACING.md),
            self.get_current_button,
        ]

        self.spacing = SPACING.md

    def _on_value_changed(self, _: ft.ControlEvent) -> None:
        """値が変更された時の処理。"""
        self.on_change()

    def _on_get_current_size(self, _: ft.ControlEvent) -> None:
        """現在のウィンドウサイズを取得する。"""
        try:
            if hasattr(self.page, "window_width") and hasattr(self.page, "window_height"):
                self.width_field.value = str(int(self.page.window_width or 1280))
                self.height_field.value = str(int(self.page.window_height or 720))

            # 位置の取得は困難なため、デフォルトを維持
            if not self.x_field.value:
                self.x_field.value = "100"
            if not self.y_field.value:
                self.y_field.value = "100"

            if hasattr(self.page, "update"):
                self.page.update()

            self.on_change()

        except Exception as e:
            # エラーハンドリングは呼び出し元に委ねるが、ログ出力は行う
            import logging

            logging.getLogger(__name__).warning("Window size change error: %s", e)

    def apply_settings(self, settings: EditableAppSettings) -> None:
        """設定値を適用する。

        Args:
            settings: 編集可能な設定オブジェクト
        """
        try:
            # サイズ設定
            width = int(self.width_field.value or "1280")
            height = int(self.height_field.value or "720")
            settings.window.size = [width, height]

            # 位置設定
            x = int(self.x_field.value or "100")
            y = int(self.y_field.value or "100")
            settings.window.position = [x, y]

        except ValueError:
            # 無効な数値の場合はデフォルト値を使用
            settings.window.size = [1280, 720]
            settings.window.position = [100, 100]

    def reset_to_settings(self, settings: AppSettings) -> None:
        """現在の設定値にリセットする。

        Args:
            settings: 現在の設定オブジェクト
        """
        # サイズ設定
        self.width_field.value = str(settings.window.size[0])
        self.height_field.value = str(settings.window.size[1])

        # 位置設定
        self.x_field.value = str(settings.window.position[0])
        self.y_field.value = str(settings.window.position[1])

        if hasattr(self.page, "update"):
            self.page.update()
