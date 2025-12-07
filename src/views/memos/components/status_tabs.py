"""メモステータスタブコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from models import MemoStatus
from views.shared.components import StatusTabs, TabDefinition

if TYPE_CHECKING:
    from collections.abc import Callable


# タブ定義（アイコン付き）
_MEMO_TAB_DEFINITIONS: tuple[TabDefinition[MemoStatus], ...] = (
    TabDefinition(status=MemoStatus.INBOX, label="Inbox", icon=ft.Icons.INBOX),
    TabDefinition(status=MemoStatus.ACTIVE, label="アクティブ", icon=ft.Icons.AUTO_AWESOME),
    TabDefinition(status=MemoStatus.IDEA, label="アイデア", icon=ft.Icons.LIGHTBULB),
    TabDefinition(status=MemoStatus.ARCHIVE, label="アーカイブ", icon=ft.Icons.ARCHIVE),
)


class MemoStatusTabs(StatusTabs[MemoStatus]):
    """Inbox/Active/Idea/Archive を切り替えるタブバーを表現する。

    共通StatusTabsコンポーネントを継承し、メモ固有のタブ定義（アイコン付き）を適用。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[MemoStatus | None], None] | None = None,
        active_status: MemoStatus = MemoStatus.INBOX,
        tab_counts: dict[MemoStatus, int] | None = None,
    ) -> None:
        """タブを初期化する。

        Args:
            on_tab_change: タブ切り替え時のコールバック（Noneも許可）
            active_status: 初期選択するタブのステータス
            tab_counts: タブごとの件数
        """
        super().__init__(
            tab_definitions=_MEMO_TAB_DEFINITIONS,
            on_tab_change=on_tab_change,
            active_status=active_status,
            tab_counts=tab_counts,
        )
