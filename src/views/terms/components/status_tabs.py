"""Term status tabs component for filtering terms by status."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import TermStatus
from views.shared.components import StatusTabs, TabDefinition

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class StatusTabsProps:
    """StatusTabs用のプロパティ（後方互換性のため保持）。"""

    approved_count: int = 0
    draft_count: int = 0
    deprecated_count: int = 0
    on_status_change: Callable[[TermStatus | None], None] | None = None


# タブ定義
_TERM_TAB_DEFINITIONS: tuple[TabDefinition[TermStatus], ...] = (
    TabDefinition(status=TermStatus.APPROVED, label="承認済み"),
    TabDefinition(status=TermStatus.DRAFT, label="草案"),
    TabDefinition(status=TermStatus.DEPRECATED, label="非推奨"),
)


class TermStatusTabs(StatusTabs[TermStatus]):
    """Status tabs for filtering terms by their approval status.

    共通StatusTabsコンポーネントを継承し、用語固有のタブ定義を適用。
    """

    def __init__(self, props: StatusTabsProps) -> None:
        """Initialize term status tabs.

        Args:
            props: タブの設定プロパティ
        """
        self.props = props

        # StatusTabsカウント形式に変換
        tab_counts = {
            TermStatus.APPROVED: props.approved_count,
            TermStatus.DRAFT: props.draft_count,
            TermStatus.DEPRECATED: props.deprecated_count,
        }

        super().__init__(
            tab_definitions=_TERM_TAB_DEFINITIONS,
            on_tab_change=props.on_status_change,
            active_status=TermStatus.APPROVED,
            tab_counts=tab_counts,
        )

    def set_active_status(self, status: TermStatus) -> None:
        """外部からステータスを指定してタブ選択を変更する。"""
        self.set_active(status)

    def set_props(self, props: StatusTabsProps) -> None:
        """新しいプロパティを設定する。

        Args:
            props: 新しいプロパティ
        """
        self.props = props

        # カウントを更新
        tab_counts = {
            TermStatus.APPROVED: props.approved_count,
            TermStatus.DRAFT: props.draft_count,
            TermStatus.DEPRECATED: props.deprecated_count,
        }
        self.update_counts(tab_counts)
