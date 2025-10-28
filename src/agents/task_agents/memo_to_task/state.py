"""メモ→タスク変換エージェントで利用する状態モデル。"""

from __future__ import annotations

from typing import NotRequired

from agents.base import BaseAgentState, ErrorAgentOutput
from agents.task_agents.memo_to_task.schema import (  # noqa: TC001
    MemoClassification,
    MemoStatusSuggestion,
    MemoToTaskAgentOutput,
    ProjectPlanSuggestion,
    QuickActionAssessment,
    ResponsibilityAssessment,
    ScheduleAssessment,
    TaskDraft,
    TaskDraftSeed,
)


class MemoToTaskState(BaseAgentState):
    """メモ解析に必要な入力情報。"""

    memo_text: str
    """ユーザーが入力したメモ本文。"""

    existing_tags: list[str]
    """既存タグ名の一覧。タグ推定はこの集合内でのみ行う。"""

    current_datetime_iso: str
    """現在日時 (ISO8601)。期日推定のリファレンスポイント。"""

    draft_output: NotRequired[MemoToTaskAgentOutput]
    """LLM から取得した生の出力。"""

    classification: NotRequired[MemoClassification]
    """Clarify段階での分類結果。"""

    task_seed: NotRequired[TaskDraftSeed]
    """タスク化が必要な場合の最小限のドラフト。"""

    requires_action: NotRequired[bool]
    """Clarify の結果、行動が必要かどうか。"""

    is_quick_action: NotRequired[bool]
    """2 分以内で完了するタスクかどうか。"""

    should_delegate: NotRequired[bool]
    """自分以外に委譲すべきかどうか。"""

    requires_specific_date: NotRequired[bool]
    """特定の日付・時間に紐付くかどうか。"""

    requires_project: NotRequired[bool]
    """複数ステップを含むプロジェクトかどうか。"""

    quick_assessment: NotRequired[QuickActionAssessment]
    """クイックアクション判定の詳細。"""

    responsibility_assessment: NotRequired[ResponsibilityAssessment]
    """委譲判定の詳細。"""

    schedule_assessment: NotRequired[ScheduleAssessment]
    """スケジュール判定の詳細。"""

    project_plan: NotRequired[ProjectPlanSuggestion]
    """プロジェクトと判断された場合の初期プラン。"""

    routed_tasks: NotRequired[list[TaskDraft]]
    """整理済みのタスク候補。"""

    suggested_status: NotRequired[MemoStatusSuggestion]
    """メモに対して提案されるステータス。"""

    error_output: NotRequired[ErrorAgentOutput]
    """エラー応答が発生した場合の内容。"""
