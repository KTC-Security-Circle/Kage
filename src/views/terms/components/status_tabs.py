"""Term status tabs component for filtering terms by status."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.sample import SampleTermStatus

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class StatusTabsProps:
    """StatusTabs用のプロパティ。"""

    approved_count: int = 0
    draft_count: int = 0
    deprecated_count: int = 0
    on_status_change: Callable[[SampleTermStatus], None] | None = None


class TermStatusTabs(ft.Tabs):
    """Status tabs for filtering terms by their approval status."""

    def __init__(self, props: StatusTabsProps) -> None:
        """Initialize term status tabs.

        Args:
            props: タブの設定プロパティ
        """
        super().__init__()
        self.props = props
        self.selected_status = SampleTermStatus.APPROVED

        self._build_tabs()
        self.on_change = self._on_tab_change
        self.selected_index = 0

    def _build_tabs(self) -> None:
        """タブを構築する。"""
        self.tabs = [
            ft.Tab(text=f"承認済み ({self.props.approved_count})"),
            ft.Tab(text=f"草案 ({self.props.draft_count})"),
            ft.Tab(text=f"非推奨 ({self.props.deprecated_count})"),
        ]

    def _on_tab_change(self, e: ft.ControlEvent) -> None:
        """タブ変更イベントをハンドリングする。"""
        tab_index = e.control.selected_index

        status_map = {
            0: SampleTermStatus.APPROVED,
            1: SampleTermStatus.DRAFT,
            2: SampleTermStatus.DEPRECATED,
        }

        self.selected_status = status_map.get(tab_index, SampleTermStatus.APPROVED)

        if self.props.on_status_change:
            self.props.on_status_change(self.selected_status)

    def set_props(self, props: StatusTabsProps) -> None:
        """新しいプロパティを設定する。

        Args:
            props: 新しいプロパティ
        """
        self.props = props
        if self.tabs:
            self.tabs[0].text = f"承認済み ({props.approved_count})"
            self.tabs[1].text = f"草案 ({props.draft_count})"
            self.tabs[2].text = f"非推奨 ({props.deprecated_count})"
        with contextlib.suppress(AssertionError):
            self.update()
