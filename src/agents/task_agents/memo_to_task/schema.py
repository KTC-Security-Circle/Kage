"""メモからタスク候補を生成するエージェントのスキーマ定義。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TaskPriority = Literal["low", "normal", "high"]
TaskRoute = Literal["progress", "waiting", "calendar", "next_action"]
MemoStatusSuggestion = Literal["idea", "active", "clarify"]
MemoProcessingDecision = Literal["idea", "task", "project"]


class TaskDraft(BaseModel):
    """タスク作成前のドラフト情報。"""

    title: str = Field(description="タスクのタイトル。")
    description: str | None = Field(default=None, description="タスクの説明。")
    due_date: str | None = Field(
        default=None,
        description="タスクの期日。ISO8601形式の日付または日時。",
    )
    priority: TaskPriority | None = Field(default=None, description="タスクの優先度。")
    tags: list[str] | None = Field(default=None, description="関連付けるタグ一覧。")
    estimate_minutes: int | None = Field(default=None, description="見積時間（分単位）。")
    route: TaskRoute | None = Field(default=None, description="Clarify/Organizeでの配置先。")
    project_title: str | None = Field(default=None, description="複数ステップを含む場合のプロジェクト名称。")

    @field_validator("due_date")
    @classmethod
    def _validate_due_date(cls, value: str | None) -> str | None:
        """ISO8601の日付または日時として解釈できる値かを検証する。"""
        if value is None:
            return None

        text = value.strip()
        if not text:
            return None

        try:
            _ensure_iso8601(text)
        except ValueError as exc:
            msg = "due_date には ISO8601 形式の文字列を指定してください。"
            raise ValueError(msg) from exc
        return text


class MemoToTaskAgentOutput(BaseModel):
    """メモ解析結果。"""

    tasks: list[TaskDraft] = Field(description="解析で得られたタスク候補一覧。")
    suggested_memo_status: MemoStatusSuggestion = Field(
        description="Clarify結果に基づくメモステータス提案。",
    )
    requires_project: bool = Field(
        default=False,
        description="プロジェクト作成が必要な場合に True。",
    )
    project_plan: ProjectPlanSuggestion | None = Field(
        default=None,
        description="project 判定時の初期プラン。",
    )


class MemoClassification(BaseModel):
    """メモの処理方針を判定した結果。"""

    decision: MemoProcessingDecision = Field(description="メモを idea/task/project のどれで扱うか。")
    reason: str = Field(description="判断理由。")
    project_title: str | None = Field(default=None, description="project の場合に推奨されるプロジェクト名。")


class TaskDraftSeed(BaseModel):
    """タスク化が必要な場合の最小限のタスク情報。"""

    title: str = Field(description="生成されたタスクタイトル")
    description: str | None = Field(default=None, description="タスク内容の簡潔な説明")
    tags: list[str] | None = Field(default=None, description="推奨タグ一覧")


class QuickActionAssessment(BaseModel):
    """2分以内に完了できるかの評価。"""

    is_quick_action: bool = Field(description="2分以内で完了できる場合は True")
    reason: str = Field(description="判断理由")


class ResponsibilityAssessment(BaseModel):
    """自分で実行すべきか、委譲すべきかの評価。"""

    should_delegate: bool = Field(description="委譲が望ましい場合は True")
    reason: str = Field(description="判断理由")


class ScheduleAssessment(BaseModel):
    """日付・時間に紐付くかの評価。"""

    requires_specific_date: bool = Field(description="特定日時が必要なら True")
    due_date: str | None = Field(default=None, description="推奨される期日 (必要な場合)")
    reason: str = Field(description="判断理由")


class ProjectPlanSuggestion(BaseModel):
    """プロジェクト分類時の初期プラン。"""

    project_title: str = Field(description="推奨されるプロジェクト名称")
    next_actions: list[TaskDraft] = Field(description="直近で着手すべきタスク候補一覧")


def _ensure_iso8601(value: str) -> None:
    """与えられた文字列が ISO8601 として解釈できるか検証する。"""
    normalized = _normalize_iso8601(value)
    datetime.fromisoformat(normalized)


def _normalize_iso8601(value: str) -> str:
    """`datetime.fromisoformat` が読み取れる形式に補正した文字列を返す。"""
    text = value.strip()
    if text.endswith(("Z", "z")):
        return f"{text[:-1]}+00:00"
    return text


def is_iso8601_string(value: str) -> bool:
    """ISO8601として解釈できる場合に True を返す。"""
    try:
        _ensure_iso8601(value)
    except ValueError:
        return False
    return True
