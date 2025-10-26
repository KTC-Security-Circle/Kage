"""Term status tabs component for filtering terms by status."""

import flet as ft

from models.terminology import TerminologyStatus


class TermStatusTabs(ft.Control):
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
        self.selected_status = TerminologyStatus.APPROVED

    def build(self) -> ft.Control:
        """Build the status tabs control."""
        return ft.Tabs(
            tabs=[
                ft.Tab(
                    text=f"承認済み ({self.approved_count})",
                    content=ft.Container(),
                ),
                ft.Tab(
                    text=f"草案 ({self.draft_count})",
                    content=ft.Container(),
                ),
                ft.Tab(
                    text=f"非推奨 ({self.deprecated_count})",
                    content=ft.Container(),
                ),
            ],
            on_change=self._on_tab_change,
            selected_index=0,
        )

    def _on_tab_change(self, e: ft.ControlEvent) -> None:
        """Handle tab change event."""
        tab_index = e.control.selected_index

        status_map = {
            0: TerminologyStatus.APPROVED,
            1: TerminologyStatus.DRAFT,
            2: TerminologyStatus.DEPRECATED,
        }

        self.selected_status = status_map.get(tab_index, TerminologyStatus.APPROVED)

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
        tabs = self.controls[0]
        tabs.tabs[0].text = f"承認済み ({approved_count})"
        tabs.tabs[1].text = f"草案 ({draft_count})"
        tabs.tabs[2].text = f"非推奨 ({deprecated_count})"

        self.update()

    def get_selected_status(self) -> TerminologyStatus:
        """Get the currently selected status.

        Returns:
            Currently selected terminology status
        """
        return self.selected_status
