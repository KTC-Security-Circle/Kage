"""PathField component for file/directory path input.

Passive component that accepts path and callback only.
Dialog integration is a placeholder for future implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


class PathField(ft.Column):
    """ファイル/ディレクトリパス入力用のフィールド。

    受動的なコンポーネント：パスとコールバックのみを受け取る。
    ダイアログ連携は将来実装予定。
    """

    def __init__(
        self,
        label: str,
        path: str = "",
        on_select: Callable[[str], None] | None = None,
        hint_text: str | None = None,
    ) -> None:
        """PathFieldを初期化する。

        Args:
            label: フィールドのラベル
            path: 初期パス
            on_select: パス選択時のコールバック
            hint_text: ヒントテキスト
        """
        super().__init__()
        self.label = label
        self.path = path
        self.on_select_callback = on_select
        self.hint_text = hint_text

        self.text_field = ft.TextField(
            label=self.label,
            value=self.path,
            on_change=self._handle_change,
            hint_text=self.hint_text,
            expand=True,
        )

        browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="参照...",
            on_click=self._handle_browse,
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [self.text_field, browse_button],
                    spacing=SPACING.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
        if self.on_select_callback and self.text_field:
            self.on_select_callback(self.text_field.value or "")

    def _handle_browse(self, _: ft.ControlEvent) -> None:
        """参照ボタンクリックイベントを処理する。

        Args:
            _: イベントオブジェクト (未使用)

        Note:
            現在は未実装。将来的にファイル選択ダイアログを表示する。
        """
        # TODO: ファイル選択ダイアログの実装

    def set_path(self, path: str) -> None:
        """パスを設定する。

        Args:
            path: 新しいパス
        """
        if self.text_field:
            self.text_field.value = path
            if self.page:
                self.update()
