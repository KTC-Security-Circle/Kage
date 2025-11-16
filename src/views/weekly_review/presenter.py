"""週次レビュービューのプレゼンター

UI構築・データ整形・差分更新ロジックを担当。
"""

from collections.abc import Sequence
from dataclasses import dataclass

import flet as ft

from models import TaskRead
from views.weekly_review.components.task_list_card import TaskItemData

from .state import WeeklyReviewState
from .utils import format_count, format_percentage


@dataclass(frozen=True, slots=True)
class StatsCardData:
    """統計カード用データ"""

    title: str
    value: str
    subtitle: str
    icon_name: str


@dataclass(frozen=True, slots=True)
class ChecklistItemData:
    """チェックリスト項目データ"""

    id: str
    label: str
    completed: bool


class WeeklyReviewPresenter:
    """週次レビューのUI構築・更新ロジック"""

    def __init__(self, state: WeeklyReviewState) -> None:
        """プレゼンターを初期化

        Args:
            state: レビュー状態
        """
        self.state = state

    def create_stats_cards_data(self) -> list[StatsCardData]:
        """統計カード用データを生成

        Returns:
            統計カードデータのリスト
        """
        if not self.state.stats:
            return []

        stats = self.state.stats
        return [
            StatsCardData(
                title="今週完了",
                value=str(stats.completed_last_week),
                subtitle="タスク",
                icon_name=ft.Icons.TRENDING_UP,
            ),
            StatsCardData(
                title="インボックス",
                value=str(stats.inbox_count),
                subtitle="未整理",
                icon_name=ft.Icons.INBOX,
            ),
            StatsCardData(
                title="待機中",
                value=str(stats.waiting_count),
                subtitle="確認が必要",
                icon_name=ft.Icons.SCHEDULE,
            ),
            StatsCardData(
                title="進行中PJ",
                value=str(stats.active_projects),
                subtitle="プロジェクト",
                icon_name=ft.Icons.CALENDAR_MONTH,
            ),
        ]

    def create_checklist_data(self) -> list[ChecklistItemData]:
        """チェックリスト用データを生成

        Returns:
            チェックリスト項目データのリスト
        """
        return [
            ChecklistItemData(
                id=item.id,
                label=item.label,
                completed=item.completed,
            )
            for item in self.state.checklist
        ]

    def format_progress_text(self) -> str:
        """進捗テキストをフォーマット

        Returns:
            進捗テキスト（例: "3 / 7 完了"）
        """
        completed = self.state.completed_checklist_count()
        total = self.state.total_checklist_count()
        return f"{completed} / {total} 完了"

    def format_progress_percentage(self) -> str:
        """進捗率をフォーマット

        Returns:
            進捗率文字列（例: "43%"）
        """
        return format_percentage(self.state.checklist_progress())

    def get_inbox_alert_message(self) -> str | None:
        """インボックス警告メッセージを取得

        Returns:
            警告メッセージ（警告不要の場合はNone）
        """
        if not self.state.is_inbox_needs_attention():
            return None

        count = self.state.stats.inbox_count if self.state.stats else 0
        return f"インボックスに{format_count(count)}の未整理タスクがあります"

    def format_week_range(self) -> str:
        """週の範囲をフォーマット

        Returns:
            週の範囲文字列
        """
        return self.state.format_week_range()

    def create_task_list_data(self, tasks: Sequence[TaskRead]) -> list[TaskItemData]:
        """タスクリスト用データを生成

        Args:
            tasks: タスクリスト

        Returns:
            タスク項目データのリスト
        """
        return [
            TaskItemData(
                id=str(task.id),
                title=task.title,
                priority=task.priority if task.priority is not None else None,
            )
            for task in tasks
        ]
