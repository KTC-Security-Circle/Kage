"""タスクステータスタブコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from views.shared.components import StatusTabs, TabDefinition

from .shared.constants import STATUS_ORDER, TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable


# タスクステータスはstr型なので、ダミーEnumとして扱う
# 共通StatusTabsはEnum型を想定しているが、str | Noneも受け入れ可能
def _create_task_tab_definitions() -> tuple[TabDefinition[str], ...]:
    """タスク用のタブ定義を生成する。"""
    definitions: list[TabDefinition[str]] = [
        TabDefinition(status=None, label="すべて"),
    ]
    for status in STATUS_ORDER:
        label = TASK_STATUS_LABELS.get(status, status)
        definitions.append(TabDefinition(status=status, label=label))
    return tuple(definitions)


_TASK_TAB_DEFINITIONS = _create_task_tab_definitions()


class TaskStatusTabs(StatusTabs[str]):
    """タスクステータスタブを表示するコンポーネント。

    共通StatusTabsコンポーネントを継承し、タスク固有のタブ定義（文字列ベース）を適用。
    「すべて」タブ + STATUS_ORDER に基づく各ステータスタブを表示。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[str | None], None] | None = None,
        active_status: str | None = None,
        tab_counts: dict[str, int] | None = None,
        _total_count: int = 0,
    ) -> None:
        """ステータスタブを初期化。

        Args:
            on_tab_change: タブ変更時のコールバック（ステータスまたはNone（すべて）を渡す）
            active_status: 現在アクティブなステータス（Noneは「すべて」）
            tab_counts: 各ステータスの件数
            _total_count: 全タスク件数（後方互換性のため保持、現在は未使用）
        """
        super().__init__(
            tab_definitions=_TASK_TAB_DEFINITIONS,
            on_tab_change=on_tab_change,
            active_status=active_status,
            tab_counts=tab_counts or {},
        )
