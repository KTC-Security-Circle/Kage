"""週次レビュービューのプレゼンター

UI構築・データ整形・差分更新ロジックを担当。
"""

# pyright: reportAttributeAccessIssue=false

from collections.abc import Sequence
from dataclasses import dataclass

import flet as ft

from models import TaskRead
from views.weekly_review.components.task_list_card import TaskItemData

from .state import WeeklyReviewState
from .utils import format_count, format_percentage

# Presenter constants
THRESHOLD_HIGH_COMPLETED = 10
THRESHOLD_MEDIUM_COMPLETED = 5
LONG_DESCRIPTION_THRESHOLD = 100


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

    def generate_achievement_summary_message(self) -> str:
        """成果サマリーメッセージを生成

        Returns:
            成果サマリーメッセージ
        """
        completed_count = len(self.state.completed_tasks_this_week)

        if completed_count == 0:
            return "今週は記録されたタスクの完了がありませんでしたが、目に見えない成果もたくさんあるはずです。"

        if completed_count >= THRESHOLD_HIGH_COMPLETED:
            return f"素晴らしい！今週は {completed_count} 件のタスクを完了しました。大きな進捗です！"
        if completed_count >= THRESHOLD_MEDIUM_COMPLETED:
            return f"お疲れ様です！今週は {completed_count} 件のタスクを完了しました。着実に前進しています！"
        return f"今週は {completed_count} 件のタスクを完了しました。一歩ずつ進んでいます。"

    def generate_zombie_task_analysis(self, task: TaskRead, days_since_creation: int) -> str:
        """ゾンビタスクの分析メッセージを生成(AI風)

        Args:
            task: タスク
            days_since_creation: 作成からの日数

        Returns:
            分析メッセージ
        """
        messages = [f"{days_since_creation} 日間進捗がありません。"]

        if len(task.description or "") > LONG_DESCRIPTION_THRESHOLD:
            messages.append("タスクの粒度が大きすぎる可能性があります。")

        if not task.due_date:
            messages.append("期限が設定されていません。")

        return " ".join(messages)

    def generate_memo_analysis(self, memo_content: str, memo_title: str) -> str:
        """未処理メモの分析メッセージを生成（AI風）

        Args:
            memo_content: メモ内容
            memo_title: メモタイトル

        Returns:
            分析メッセージ
        """
        # 簡易的なキーワード分析
        action_keywords = ["TODO", "やる", "作成", "実装", "確認", "修正", "対応"]
        content_to_check = memo_content + memo_title

        has_action = any(keyword in content_to_check for keyword in action_keywords)

        if has_action:
            return "アクションが必要な内容が含まれています。タスクにし忘れていませんか？"

        return "アイデアや参考情報として保存することをお勧めします。"

    def get_step_labels(self) -> list[str]:
        """ウィザードステップのラベルを取得

        Returns:
            ステップラベルのリスト
        """
        return ["成果の振り返り", "システムの整理", "来週の計画"]
