"""Create memo form component.

左カラム（基本情報 + 内容編集/プレビュー）をまとめたコンポーネント。
親Viewから値とイベントコールバックを受け取り、UIの組み立てと
プレビューの更新を担当する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import flet as ft

from models import MemoStatus

from .markdown_preview import render_markdown_preview

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(slots=True)
class FormCallbacks:
    """フォームイベントのコールバック群。"""

    on_title_change: Callable[[str], None]
    on_status_change: Callable[[MemoStatus], None]
    on_content_change: Callable[[str], None]
    on_tab_change: Callable[[Literal["edit", "preview"]], None]


class CreateForm(ft.Container):
    """メモ作成フォーム（タイトル/ステータス/本文編集+プレビュー）。

    Args:
        title: 初期タイトル
        status: 初期ステータス
        content: 初期本文
        active_tab: 初期アクティブタブ ("edit" | "preview")
        callbacks: フォームイベントのコールバック群
    """

    def __init__(
        self,
        *,
        title: str,
        status: MemoStatus,
        content: str,
        active_tab: Literal["edit", "preview"],
        callbacks: FormCallbacks,
    ) -> None:
        super().__init__()
        self._callbacks = callbacks

        # controls
        self._title_input: ft.TextField | None = None
        self._status_select: ft.Dropdown | None = None
        self._tabs: ft.Tabs | None = None
        self._content_editor: ft.TextField | None = None
        self._preview_panel: ft.Container | None = None

        self.content = self._build_content(title, status, content, active_tab)

    def _build_content(
        self,
        title: str,
        status: MemoStatus,
        content: str,
        active_tab: Literal["edit", "preview"],
    ) -> ft.Control:
        self._title_input = ft.TextField(
            label="タイトル（任意）",
            hint_text="メモのタイトルを入力...",
            value=title,
            on_change=lambda e: self._callbacks.on_title_change(e.data or ""),
        )

        self._status_select = ft.Dropdown(
            label="ステータス",
            value=status.value,
            options=[
                ft.dropdown.Option(MemoStatus.INBOX.value, "INBOX"),
                ft.dropdown.Option(MemoStatus.ACTIVE.value, "ACTIVE"),
                ft.dropdown.Option(MemoStatus.IDEA.value, "IDEA"),
                ft.dropdown.Option(MemoStatus.ARCHIVE.value, "ARCHIVE"),
            ],
            on_change=lambda e: self._callbacks.on_status_change(MemoStatus(e.data or MemoStatus.INBOX.value)),
        )

        basic_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("基本情報", weight=ft.FontWeight.BOLD),
                        self._title_input,
                        self._status_select,
                    ],
                    spacing=10,
                ),
                padding=ft.padding.all(16),
            )
        )

        self._content_editor = ft.TextField(
            label="内容 (必須)",
            multiline=True,
            min_lines=12,
            max_lines=30,
            value=content,
            hint_text="メモの内容を入力してください...",
            on_change=lambda e: self._handle_content_change(e.data or ""),
        )

        self._preview_panel = ft.Container(
            content=ft.Column(controls=render_markdown_preview(content), spacing=8),
            bgcolor=ft.Colors.SURFACE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            padding=ft.padding.all(12),
        )

        edit_tab = ft.Container(content=self._content_editor)
        preview_tab = ft.Container(content=self._preview_panel)

        self._tabs = ft.Tabs(
            selected_index=0 if active_tab == "edit" else 1,
            on_change=lambda e: self._handle_tab_change(int(e.control.selected_index)),  # type: ignore[arg-type]
            tabs=[ft.Tab(text="編集"), ft.Tab(text="プレビュー")],
            expand=False,
        )

        content_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("内容", weight=ft.FontWeight.BOLD),
                        self._tabs,
                        ft.Container(
                            content=edit_tab if active_tab == "edit" else preview_tab,
                        ),
                        ft.Text("ヒント: Ctrl+Enter で送信", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.all(16),
            )
        )

        return ft.Column([basic_card, content_card], spacing=12, expand=True)

    # callbacks ---------------------------------------------------------
    def _handle_content_change(self, value: str) -> None:
        self._callbacks.on_content_change(value)
        if self._tabs and self._preview_panel and self._tabs.selected_index == 1:
            self._preview_panel.content = ft.Column(controls=render_markdown_preview(value), spacing=8)
            self.update()

    def _handle_tab_change(self, idx: int) -> None:
        tab = "edit" if idx == 0 else "preview"
        self._callbacks.on_tab_change(tab)
        # タブ切替時、プレビューが選択されたなら最新化
        if tab == "preview" and self._preview_panel and self._content_editor:
            self._preview_panel.content = ft.Column(
                controls=render_markdown_preview(self._content_editor.value or ""), spacing=8
            )
            self.update()
