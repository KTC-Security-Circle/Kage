"""メモ→タスク変換エージェントで利用する状態モデル。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NotRequired

import models
from agents.base import AgentError, BaseAgentResponse, BaseAgentState
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

if TYPE_CHECKING:
    from models import MemoRead
else:  # pragma: no cover - runtime annotation support
    MemoRead = models.MemoRead


class MemoToTaskState(BaseAgentState):
    """メモ解析に必要な入力情報。"""

    memo: MemoRead
    """解析対象のメモ情報。"""

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

    error: NotRequired[AgentError]
    """エラーが発生した場合の例外インスタンス。"""

    custom_instructions: NotRequired[str]
    """設定から渡されるカスタム指示文。"""

    detail_hint: NotRequired[str]
    """応答の詳細度を指示するテキスト。"""

    # 最終応答は最終ノードで構築され、BaseAgent/_create_return_response で取り出されるため、
    # State での final_response は不要（互換フィールドを削除）。


@dataclass
class MemoToTaskResult(BaseAgentResponse[MemoToTaskState]):
    """メモ解析エージェントの結果モデル（最終応答）。"""

    tasks: list[TaskDraft]
    suggested_memo_status: MemoStatusSuggestion
    requires_project: bool = False
    project_plan: ProjectPlanSuggestion | None = None
