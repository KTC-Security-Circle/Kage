"""週次レビュービューの状態管理

週次レビューの表示状態を管理し、派生データを計算する。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Literal

from models import TaskRead
from views.weekly_review.components import MemoAction, RecommendationData, ZombieTaskAction


class ReviewStep(Enum):
    """レビューウィザードのステップ"""

    OVERVIEW = "overview"
    INBOX = "inbox"
    PROJECTS = "projects"
    REVIEW = "review"
    COMPLETE = "complete"


@dataclass
class ChecklistItem:
    """チェックリスト項目"""

    id: str
    label: str
    completed: bool = False


@dataclass
class WeeklyStats:
    """週次統計データ"""

    completed_tasks: int
    focus_hours: float
    inbox_count: int
    waiting_count: int
    someday_count: int
    active_projects: int
    completed_last_week: int


@dataclass
class ZombieTaskReviewItem:
    """UI 表示用のゾンビタスク情報"""

    id: str
    title: str
    reason: str
    stale_days: int


@dataclass
class MemoReviewItem:
    """UI 表示用の未処理メモ情報"""

    id: str
    title: str
    content: str
    suggestion: str | None = None
    recommended_route: Literal["task", "reference", "someday", "discard"] | None = None


def _get_week_start() -> datetime:
    """今週の開始日（月曜日）を取得

    Returns:
        今週の月曜日の日時
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 0=月曜日, 6=日曜日
    days_since_monday = today.weekday()
    return today - timedelta(days=days_since_monday)


def _get_week_end() -> datetime:
    """今週の終了日（日曜日）を取得

    Returns:
        今週の日曜日の日時
    """
    return _get_week_start() + timedelta(days=6, hours=23, minutes=59, seconds=59)


@dataclass(slots=True)
class WeeklyReviewState:
    """週次レビューの状態を保持するデータクラス

    全ての表示状態の単一ソース。
    """

    # レビューウィザード状態
    current_step: int = 1  # 1: 成果, 2: 整理, 3: 計画
    total_steps: int = 3
    wizard_active: bool = False
    has_started: bool = False
    data_loaded: bool = False

    # チェックリスト状態
    checklist: list[ChecklistItem] = field(
        default_factory=lambda: [
            ChecklistItem(id="collect", label="すべてのインボックスを空にする"),
            ChecklistItem(id="process", label="各タスクを整理し、適切なリストに移動する"),
            ChecklistItem(id="review-calendar", label="先週と来週のカレンダーを確認"),
            ChecklistItem(id="review-waiting", label="待機中リストを確認"),
            ChecklistItem(id="review-projects", label="進行中のプロジェクトを確認"),
            ChecklistItem(id="review-someday", label="いつか/多分リストを見直す"),
            ChecklistItem(id="next-actions", label="次のアクションを決定"),
        ]
    )

    # 統計データ
    stats: WeeklyStats | None = None
    highlights_intro: str | None = None

    # ユーザーの意思決定記録 (Step2)
    zombie_task_decisions: dict[str, ZombieTaskAction] = field(default_factory=dict)
    memo_decisions: dict[str, MemoAction] = field(default_factory=dict)

    # Step1: 成果データ
    completed_tasks_this_week: list[TaskRead] = field(default_factory=list)
    achievement_highlights: list[str] = field(default_factory=list)

    # Step2: 整理データ
    zombie_tasks: list[ZombieTaskReviewItem] = field(default_factory=list)
    unprocessed_memos: list[MemoReviewItem] = field(default_factory=list)

    # Step3: 計画データ
    recommendations: list[RecommendationData] = field(default_factory=list)

    # 期間設定
    current_week_start: datetime = field(default_factory=lambda: _get_week_start())
    current_week_end: datetime = field(default_factory=_get_week_end)

    def toggle_checklist_item(self, item_id: str) -> None:
        """チェックリスト項目の完了状態を切り替える

        Args:
            item_id: 切り替える項目のID
        """
        for item in self.checklist:
            if item.id == item_id:
                item.completed = not item.completed
                break

    def completed_checklist_count(self) -> int:
        """完了したチェックリスト項目数を取得

        Returns:
            完了した項目数
        """
        return sum(1 for item in self.checklist if item.completed)

    def total_checklist_count(self) -> int:
        """チェックリスト項目の総数を取得

        Returns:
            項目の総数
        """
        return len(self.checklist)

    def checklist_progress(self) -> float:
        """チェックリストの進捗率を取得

        Returns:
            進捗率（0.0 ~ 1.0）
        """
        total = self.total_checklist_count()
        if total == 0:
            return 0.0
        return self.completed_checklist_count() / total

    def is_inbox_needs_attention(self) -> bool:
        """インボックスに要整理項目があるかチェック

        Returns:
            要整理項目がある場合True
        """
        return self.stats is not None and self.stats.inbox_count > 0

    def format_week_range(self) -> str:
        """週の範囲を文字列でフォーマット

        Returns:
            週の範囲（例: 2024/01/01 - 2024/01/07）
        """
        start_str = self.current_week_start.strftime("%Y/%m/%d")
        end_str = self.current_week_end.strftime("%Y/%m/%d")
        return f"{start_str} - {end_str}"

    def next_step(self) -> None:
        """次のステップへ進む"""
        if self.current_step < self.total_steps:
            self.current_step += 1

    def prev_step(self) -> None:
        """前のステップへ戻る"""
        if self.current_step > 1:
            self.current_step -= 1

    def set_zombie_task_decision(self, task_id: str, action: ZombieTaskAction) -> None:
        """ゾンビタスクの意思決定を記録

        Args:
            task_id: タスクID
            action: 選択されたアクション
        """
        self.zombie_task_decisions[task_id] = action

    def set_memo_decision(self, memo_id: str, action: MemoAction) -> None:
        """メモの意思決定を記録

        Args:
            memo_id: メモID
            action: 選択されたアクション
        """
        self.memo_decisions[memo_id] = action

    def get_zombie_task_decision(self, task_id: str) -> ZombieTaskAction:
        """ゾンビタスクの意思決定を取得

        Args:
            task_id: タスクID

        Returns:
            選択されたアクション (なければNone)
        """
        return self.zombie_task_decisions.get(task_id)

    def get_memo_decision(self, memo_id: str) -> MemoAction:
        """メモの意思決定を取得

        Args:
            memo_id: メモID

        Returns:
            選択されたアクション (なければNone)
        """
        return self.memo_decisions.get(memo_id)
