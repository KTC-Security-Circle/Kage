"""プロジェクトステータスタブコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from models import ProjectStatus
from views.shared.components import StatusTabs, TabDefinition

if TYPE_CHECKING:
    from collections.abc import Callable


# タブ定義（None = すべて）
_PROJECT_TAB_DEFINITIONS: tuple[TabDefinition[ProjectStatus], ...] = (
    TabDefinition(status=None, label="すべて"),
    TabDefinition(status=ProjectStatus.ACTIVE, label=ProjectStatus.display_label(ProjectStatus.ACTIVE)),
    TabDefinition(status=ProjectStatus.ON_HOLD, label=ProjectStatus.display_label(ProjectStatus.ON_HOLD)),
    TabDefinition(status=ProjectStatus.COMPLETED, label=ProjectStatus.display_label(ProjectStatus.COMPLETED)),
    TabDefinition(status=ProjectStatus.CANCELLED, label=ProjectStatus.display_label(ProjectStatus.CANCELLED)),
)


class ProjectStatusTabs(StatusTabs[ProjectStatus]):
    """プロジェクトステータスタブを表示するコンポーネント。

    共通StatusTabsコンポーネントを継承し、プロジェクト固有のタブ定義を適用。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[ProjectStatus | None], None] | None = None,
        active_status: ProjectStatus | None = None,
        tab_counts: dict[ProjectStatus, int] | None = None,
    ) -> None:
        """ステータスタブを初期化。

        Args:
            on_tab_change: タブ変更時のコールバック（ステータスを直接受け取る）
            active_status: アクティブなステータス
            tab_counts: 各ステータスのカウント
        """
        super().__init__(
            tab_definitions=_PROJECT_TAB_DEFINITIONS,
            on_tab_change=on_tab_change,
            active_status=active_status,
            tab_counts=tab_counts,
        )
