"""Action bar component for terms management."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class ActionBarProps:
    """ActionBar用のプロパティ。"""

    search_placeholder: str = "用語、キー、同義語で検索..."
    on_search: Callable[[str], None] | None = None
    on_create: Callable[[], None] | None = None


class TermActionBar(ft.Row):
    """Action bar with search and create functionality for terms."""

    def __init__(self, props: ActionBarProps) -> None:
        """Initialize term action bar.

        Args:
            props: ActionBarの設定プロパティ
        """
        super().__init__()
        self.props = props
        self.search_field: ft.TextField | None = None

        self._build_controls()

    def _build_controls(self) -> None:
        """コントロールを構築する。"""
        self.search_field = ft.TextField(
            hint_text=self.props.search_placeholder,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=8,
            on_change=self._handle_search,
            expand=True,
        )

        create_button = ft.ElevatedButton(
            text="新しい用語",
            icon=ft.Icons.ADD,
            on_click=self._handle_create,
        )

        self.controls = [
            self.search_field,
            create_button,
        ]
        self.spacing = 16
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def _handle_search(self, e: ft.ControlEvent) -> None:
        """検索入力の変更をハンドリングする。"""
        if self.props.on_search and hasattr(e.control, "value"):
            self.props.on_search(str(e.control.value))

    def _handle_create(self, _: ft.ControlEvent) -> None:
        """作成ボタンのクリックをハンドリングする。"""
        if self.props.on_create:
            self.props.on_create()

    def set_props(self, props: ActionBarProps) -> None:
        """新しいプロパティを設定する。

        Args:
            props: 新しいプロパティ
        """
        self.props = props
        if self.search_field:
            self.search_field.hint_text = props.search_placeholder

    def clear_search(self) -> None:
        """検索フィールドをクリアする。"""
        if self.search_field:
            self.search_field.value = ""
            # ページ未追加時は無視
            with contextlib.suppress(AssertionError):
                self.search_field.update()
