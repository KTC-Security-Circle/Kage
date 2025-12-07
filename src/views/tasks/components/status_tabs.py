"""タスクステータスタブコンポーネント。

共通StatusTabsコンポーネントを継承し、タスク固有のタブ定義を適用。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.shared.components import StatusTabs, TabDefinition

from .shared.constants import TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable


# タブ定義（アイコン付き）
_TASK_TAB_DEFINITIONS: tuple[TabDefinition[str], ...] = (
    TabDefinition(status=None, label="すべて", icon=ft.Icons.LIST),
    TabDefinition(status="todo", label=TASK_STATUS_LABELS["todo"], icon=ft.Icons.INBOX),
    TabDefinition(status="todays", label=TASK_STATUS_LABELS["todays"], icon=ft.Icons.TODAY),
    TabDefinition(status="progress", label=TASK_STATUS_LABELS["progress"], icon=ft.Icons.PLAY_ARROW),
    TabDefinition(status="waiting", label=TASK_STATUS_LABELS["waiting"], icon=ft.Icons.SCHEDULE),
    TabDefinition(status="completed", label=TASK_STATUS_LABELS["completed"], icon=ft.Icons.CHECK_CIRCLE),
    TabDefinition(status="canceled", label=TASK_STATUS_LABELS["canceled"], icon=ft.Icons.CANCEL),
    TabDefinition(status="overdue", label=TASK_STATUS_LABELS["overdue"], icon=ft.Icons.WARNING),
)


class TaskStatusTabs(StatusTabs[str]):
    """タスクステータスタブを表示するコンポーネント。

    共通StatusTabsコンポーネントを継承し、タスク固有のタブ定義（アイコン付き）を適用。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[str | None], None] | None = None,
        active_status: str | None = None,
        tab_counts: dict[str, int] | None = None,
    ) -> None:
        """タブを初期化する。

        Args:
            on_tab_change: タブ切り替え時のコールバック（Noneも許可）
            active_status: 初期選択するタブのステータス（Noneは「すべて」）
            tab_counts: タブごとの件数
        """
        super().__init__(
            tab_definitions=_TASK_TAB_DEFINITIONS,
            on_tab_change=on_tab_change,
            active_status=active_status,
            tab_counts=tab_counts,
        )
