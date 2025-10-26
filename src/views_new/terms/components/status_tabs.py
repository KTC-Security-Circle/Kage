"""Term status tabs component for filtering terms by status."""

import flet as ft

from views_new.sample import SampleTermStatus


class TermStatusTabs(ft.Tabs):
    """Status tabs for filtering terms by their approval status."""

    def __init__(
        self,
        approved_count: int = 0,
        draft_count: int = 0,
        deprecated_count: int = 0,
        on_status_change: ft.OptionalEventCallable = None,
    ) -> None:
        """Initialize term status tabs.

        Args:
            approved_count: Number of approved terms
            draft_count: Number of draft terms
            deprecated_count: Number of deprecated terms
            on_status_change: Callback when status tab changes
        """
        super().__init__()
        self.approved_count = approved_count
        self.draft_count = draft_count
        self.deprecated_count = deprecated_count
        self.on_status_change = on_status_change
        self.selected_status = SampleTermStatus.APPROVED

        # 初期化時にタブを構築
        self._build_tabs()
        self.on_change = self._on_tab_change
        self.selected_index = 0

    def _build_tabs(self) -> None:
        """Build the tabs."""
        self.tabs = [
            ft.Tab(
                text=f"承認済み ({self.approved_count})",
                # contentを削除してTransformLayerエラーを回避
            ),
            ft.Tab(
                text=f"草案 ({self.draft_count})",
                # contentを削除してTransformLayerエラーを回避
            ),
            ft.Tab(
                text=f"非推奨 ({self.deprecated_count})",
                # contentを削除してTransformLayerエラーを回避
            ),
        ]

    def build(self) -> ft.Control:
        """Build the status tabs control."""
        # この方法は使用しない（ft.Tabsを継承しているため）
        return self

    def _on_tab_change(self, e: ft.ControlEvent) -> None:
        """Handle tab change event."""
        tab_index = e.control.selected_index

        status_map = {
            0: SampleTermStatus.APPROVED,
            1: SampleTermStatus.DRAFT,
            2: SampleTermStatus.DEPRECATED,
        }

        self.selected_status = status_map.get(tab_index, SampleTermStatus.APPROVED)

        if self.on_status_change:
            self.on_status_change(self.selected_status)

    def update_counts(
        self,
        approved_count: int,
        draft_count: int,
        deprecated_count: int,
    ) -> None:
        """Update the counts displayed in tabs.

        Args:
            approved_count: Number of approved terms
            draft_count: Number of draft terms
            deprecated_count: Number of deprecated terms
        """
        self.approved_count = approved_count
        self.draft_count = draft_count
        self.deprecated_count = deprecated_count

        # Update tab text
        if self.tabs:
            self.tabs[0].text = f"承認済み ({approved_count})"
            self.tabs[1].text = f"草案 ({draft_count})"
            self.tabs[2].text = f"非推奨 ({deprecated_count})"

        self.update()

    def get_selected_status(self) -> SampleTermStatus:
        """Get the currently selected status.

        Returns:
            Currently selected terminology status
        """
        return self.selected_status
