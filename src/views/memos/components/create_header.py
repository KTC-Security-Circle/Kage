"""Create memo header component.

ヘッダー行（戻る/タイトル/サブ/キャンセル/保存）をまとめたコンポーネント。
既存のコンポーネント設計に合わせ、Fletコントロール継承で再利用可能にする。
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

from views.theme import get_outline_color, get_surface_color, get_text_secondary_color

if TYPE_CHECKING:
    from collections.abc import Callable


class CreateHeader(ft.Container):
    """メモ作成ページの固定ヘッダー。

    Args:
        on_back: 戻るボタン押下時のコールバック
        on_cancel: キャンセル押下時のコールバック
        on_save: 保存押下時のコールバック
    """

    def __init__(
        self,
        *,
        on_back: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        on_save: Callable[[], None] | None = None,
        can_save: bool = False,
    ) -> None:
        self._on_back = on_back
        self._on_cancel = on_cancel
        self._on_save = on_save
        self._save_button: ft.FilledButton | None = None

        super().__init__(
            content=self._build_content(),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor=get_surface_color(),
            border=ft.border.only(bottom=ft.BorderSide(1, get_outline_color())),
        )
        if can_save:
            # 初期状態で保存可能なら能動的にボタンを有効化
            self.enable_save()

    def _build_content(self) -> ft.Control:
        self._save_button = ft.FilledButton(
            "保存",
            icon=ft.Icons.SAVE,
            on_click=lambda _: self._handle_save(),
            disabled=True,  # 初期は無効。enable_save()/disable_save()で切替。
        )
        return ft.Row(
            controls=[
                ft.Row(
                    [
                        ft.OutlinedButton(
                            "戻る",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: self._handle_back(),
                        ),
                        ft.Column(
                            [
                                ft.Text("新しいメモを作成", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "マークダウン形式で記述できます",
                                    size=12,
                                    color=get_text_secondary_color(),
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.OutlinedButton("キャンセル", on_click=lambda _: self._handle_cancel()),
                        self._save_button,
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _handle_back(self) -> None:
        if self._on_back:
            self._on_back()

    def _handle_cancel(self) -> None:
        if self._on_cancel:
            self._on_cancel()

    def _handle_save(self) -> None:
        if self._on_save:
            self._on_save()

    # Public API ----------------------------------------------------------
    def enable_save(self) -> None:
        """保存ボタンを有効にする。"""
        if self._save_button is not None:
            self._save_button.disabled = False
            if getattr(self, "page", None) is not None:
                with contextlib.suppress(AssertionError):
                    self.update()

    def disable_save(self) -> None:
        """保存ボタンを無効にする。"""
        if self._save_button is not None:
            self._save_button.disabled = True
            if getattr(self, "page", None) is not None:
                with contextlib.suppress(AssertionError):
                    self.update()
