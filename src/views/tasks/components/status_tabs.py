"""タスクステータスタブコンポーネント。"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

from .shared.constants import STATUS_ORDER, TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable


class TaskStatusTabs(ft.Container):
    """タスクステータスタブを表示するコンポーネント。

    「すべて」タブ + STATUS_ORDER に基づく各ステータスタブを表示し、
    件数バッジとアクティブ状態を管理する。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[str | None], None] | None = None,
        active_status: str | None = None,
        tab_counts: dict[str, int] | None = None,
        total_count: int = 0,
    ) -> None:
        """ステータスタブを初期化。

        Args:
            on_tab_change: タブ変更時のコールバック（ステータスまたはNone（すべて）を渡す）
            active_status: 現在アクティブなステータス（Noneは「すべて」）
            tab_counts: 各ステータスの件数
            total_count: 全タスク件数（「すべて」タブ用）
        """
        self.on_tab_change = on_tab_change
        self.active_status = active_status
        self.tab_counts = tab_counts or {}
        self.total_count = total_count

        # タブキー定義: [None（すべて）, ...STATUS_ORDER]
        self._tab_keys: list[str | None] = [None, *STATUS_ORDER]

        self._tabs: ft.Tabs | None = None

        super().__init__(
            content=self._build_tabs(),
            padding=0,
        )

    def _build_tabs(self) -> ft.Control:
        """タブを構築する。"""
        tab_texts = self._generate_tab_texts()
        selected_index = self._get_current_tab_index()

        self._tabs = ft.Tabs(
            selected_index=selected_index,
            tabs=[ft.Tab(text=t) for t in tab_texts],
            on_change=self._on_tabs_change,
            expand=True,
        )
        return ft.Row([self._tabs], spacing=0)

    def _generate_tab_texts(self) -> list[str]:
        """タブのテキストリストを生成する（件数バッジ付き）。"""
        tab_texts: list[str] = [f"すべて ({self.total_count})"]
        for status in STATUS_ORDER:
            label = TASK_STATUS_LABELS.get(status, status)
            count = self.tab_counts.get(status, 0)
            tab_texts.append(f"{label} ({count})")
        return tab_texts

    def _get_current_tab_index(self) -> int:
        """現在のアクティブステータスに対応するタブインデックスを返す。"""
        if self.active_status is None:
            return 0
        try:
            return 1 + STATUS_ORDER.index(self.active_status)
        except ValueError:
            return 0

    def _on_tabs_change(self, e: ft.ControlEvent) -> None:
        """タブ選択変更時のハンドラー。"""
        idx = e.control.selected_index
        if idx < 0 or idx >= len(self._tab_keys):
            return
        new_status = self._tab_keys[idx]
        self.active_status = new_status
        if self.on_tab_change:
            self.on_tab_change(new_status)

    def update_counts(
        self,
        tab_counts: dict[str, int],
        total_count: int,
    ) -> None:
        """タブの件数を更新する。

        Args:
            tab_counts: 各ステータスの件数
            total_count: 全タスク件数
        """
        self.tab_counts = tab_counts
        self.total_count = total_count

        if not self._tabs:
            return

        tab_texts = self._generate_tab_texts()
        for i, text in enumerate(tab_texts):
            if i < len(self._tabs.tabs):
                self._tabs.tabs[i].text = text

        with contextlib.suppress(AssertionError):
            self._tabs.update()

    def set_active(self, status: str | None) -> None:
        """アクティブなステータスを設定する。

        Args:
            status: アクティブにするステータス（Noneは「すべて」）
        """
        if self.active_status == status:
            return

        self.active_status = status
        if self._tabs:
            new_index = self._get_current_tab_index()
            self._tabs.selected_index = new_index
            with contextlib.suppress(AssertionError):
                self._tabs.update()
