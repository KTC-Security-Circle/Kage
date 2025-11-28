"""週次レビューウィザード向けのDTOとスキーマ定義。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field, FieldValidationInfo, field_validator

if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from models import MemoRead, ProjectRead, TaskRead


@dataclass(slots=True)
class CompletedTaskDigest:
    """成果サマリー生成時に利用する完了タスク情報。"""

    task: TaskRead
    memo_excerpt: str | None = None
    project_title: str | None = None


@dataclass(slots=True)
class ZombieTaskDigest:
    """ゾンビタスク検知に利用するタスク情報。"""

    task: TaskRead
    stale_days: int
    memo_excerpt: str | None = None
    project_title: str | None = None


@dataclass(slots=True)
class MemoAuditDigest:
    """棚卸し対象の未処理メモ情報。"""

    memo: MemoRead
    linked_project: ProjectRead | None = None


class WeeklyReviewInsightsQuery(BaseModel):
    """週次レビュー生成用の問い合わせモデル。"""

    model_config = ConfigDict(frozen=True)

    user_id: UUID | None = Field(default=None, description="レビューを実行したユーザーID。")
    start: datetime | None = Field(default=None, description="収集期間の開始。未指定時は設定値から算出。")
    end: datetime | None = Field(default=None, description="収集期間の終了。未指定時は現在時刻。")
    zombie_threshold_days: int | None = Field(
        default=None,
        ge=1,
        le=120,
        description="ゾンビタスク判定で使用する経過日数。",
    )
    project_ids: list[UUID] = Field(
        default_factory=list,
        description="特定プロジェクトに絞り込む場合のID一覧。",
    )

    @field_validator("project_ids")
    @classmethod
    def _deduplicate_projects(cls, values: list[UUID]) -> list[UUID]:
        ordered: dict[UUID, None] = dict.fromkeys(values)
        return list(ordered.keys())


class ReviewPeriod(BaseModel):
    """レスポンスの期間情報。"""

    model_config = ConfigDict(frozen=True)

    start: datetime = Field(description="集計期間の開始日時。")
    end: datetime = Field(description="集計期間の終了日時。")

    @field_validator("end")
    @classmethod
    def _validate_range(cls, end: datetime, info: FieldValidationInfo) -> datetime:
        start = info.data.get("start") if info.data is not None else None
        if isinstance(start, datetime) and end < start:
            msg = "end は start 以降である必要があります"
            raise ValueError(msg)
        return end


class WeeklyReviewMetadata(BaseModel):
    """レスポンス共通のメタデータ。"""

    model_config = ConfigDict(frozen=True)

    period: ReviewPeriod = Field(description="今回のレビュー期間。")
    generated_at: datetime = Field(description="レスポンス生成日時。")
    zombie_threshold_days: int = Field(description="ゾンビ判定に使用した日数。")
    project_filters: list[UUID] = Field(default_factory=list, description="適用したプロジェクトフィルター。")


class WeeklyReviewHighlightsItem(BaseModel):
    """成果サマリーの bullet 項目。"""

    model_config = ConfigDict(frozen=True)

    title: str = Field(description="成果のタイトル。")
    description: str = Field(description="成果の詳細。")
    source_task_ids: list[UUID] = Field(default_factory=list, description="この成果に紐付くタスクID。")


class WeeklyReviewHighlightsPayload(BaseModel):
    """成果サマリーセクション。"""

    model_config = ConfigDict(frozen=True)

    status: Literal["ready", "fallback"] = Field(default="ready")
    intro: str = Field(description="ユーザーへの肯定的なメッセージ。")
    items: list[WeeklyReviewHighlightsItem] = Field(default_factory=list)
    fallback_message: str | None = Field(default=None, description="LLM 失敗時の代替テキスト。")


class ZombieTaskSuggestion(BaseModel):
    """ゾンビタスクへの具体的な提案。"""

    model_config = ConfigDict(frozen=True)

    action: Literal["split", "defer", "someday", "delete"]
    rationale: str
    suggested_subtasks: list[str] = Field(default_factory=list)


class ZombieTaskInsight(BaseModel):
    """ゾンビタスク1件分の情報。"""

    model_config = ConfigDict(frozen=True)

    task_id: UUID
    title: str
    stale_days: int
    project_title: str | None = None
    memo_excerpt: str | None = None
    suggestions: list[ZombieTaskSuggestion] = Field(default_factory=list)


class WeeklyReviewZombiePayload(BaseModel):
    """ゾンビタスクセクション。"""

    model_config = ConfigDict(frozen=True)

    status: Literal["ready", "fallback"] = Field(default="ready")
    tasks: list[ZombieTaskInsight] = Field(default_factory=list)
    fallback_message: str | None = None


class MemoAuditInsight(BaseModel):
    """未処理メモ棚卸しの項目。"""

    model_config = ConfigDict(frozen=True)

    memo_id: UUID
    summary: str
    recommended_route: Literal["task", "reference", "someday", "discard"]
    linked_project_id: UUID | None = None
    linked_project_title: str | None = None
    guidance: str = Field(description="ユーザーへの短い問いかけ。")


class WeeklyReviewMemoAuditPayload(BaseModel):
    """棚卸しセクション。"""

    model_config = ConfigDict(frozen=True)

    status: Literal["ready", "fallback"] = Field(default="ready")
    audits: list[MemoAuditInsight] = Field(default_factory=list)
    fallback_message: str | None = None


class WeeklyReviewInsights(BaseModel):
    """週次レビュー API のレスポンスモデル。"""

    model_config = ConfigDict(from_attributes=True)

    metadata: WeeklyReviewMetadata
    highlights: WeeklyReviewHighlightsPayload
    zombie_tasks: WeeklyReviewZombiePayload
    memo_audits: WeeklyReviewMemoAuditPayload
