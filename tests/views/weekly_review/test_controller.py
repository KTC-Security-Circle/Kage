"""WeeklyReviewController の挙動を検証するテスト。"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from logic.application.memo_application_service import MemoApplicationService
from logic.application.review_application_service import WeeklyReviewApplicationService
from logic.application.task_application_service import TaskApplicationService
from models import (
    MemoAuditInsight,
    ReviewPeriod,
    TaskRead,
    TaskStatus,
    WeeklyReviewHighlightsItem,
    WeeklyReviewHighlightsPayload,
    WeeklyReviewInsights,
    WeeklyReviewMemoAuditPayload,
    WeeklyReviewMetadata,
    WeeklyReviewZombiePayload,
    ZombieTaskInsight,
    ZombieTaskSuggestion,
)
from views.weekly_review.controller import WeeklyReviewController
from views.weekly_review.state import WeeklyReviewState


def _build_insights(task_id: UUID, memo_id: UUID) -> WeeklyReviewInsights:
    now = datetime.now()
    metadata = WeeklyReviewMetadata(
        period=ReviewPeriod(start=now - timedelta(days=7), end=now),
        generated_at=now,
        zombie_threshold_days=14,
        project_filters=[],
    )
    highlights = WeeklyReviewHighlightsPayload(
        status="ready",
        intro="今週もお疲れさまでした。",
        items=[
            WeeklyReviewHighlightsItem(
                title="成果1",
                description="大きな進捗を達成",
                source_task_ids=[task_id],
            )
        ],
    )
    zombie_payload = WeeklyReviewZombiePayload(
        status="ready",
        tasks=[
            ZombieTaskInsight(
                task_id=uuid4(),
                title="停滞タスク",
                stale_days=21,
                project_title=None,
                memo_excerpt="要分割",
                suggestions=[
                    ZombieTaskSuggestion(action="split", rationale="細かく分割しましょう", suggested_subtasks=[])
                ],
            )
        ],
    )
    memo_payload = WeeklyReviewMemoAuditPayload(
        status="ready",
        audits=[
            MemoAuditInsight(
                memo_id=memo_id,
                summary="メモの要約",
                recommended_route="task",
                linked_project_id=None,
                linked_project_title=None,
                guidance="すぐにタスクに変換しましょう",
            )
        ],
    )
    return WeeklyReviewInsights(
        metadata=metadata,
        highlights=highlights,
        zombie_tasks=zombie_payload,
        memo_audits=memo_payload,
    )


def _build_task(task_id: UUID) -> TaskRead:
    return TaskRead(
        id=task_id,
        title="完了タスク",
        description="詳細",
        status=TaskStatus.COMPLETED,
    )


def test_load_initial_data_populates_state() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    task_id = uuid4()
    memo_id = uuid4()
    insights = _build_insights(task_id, memo_id)

    review_service.fetch_insights.return_value = insights
    task_service.get_by_id.return_value = _build_task(task_id)
    memo_service.get_by_id.return_value = SimpleNamespace(title="メモA", content="メモ本文")

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    controller.load_initial_data()

    assert state.stats is not None
    assert state.achievement_highlights == ["成果1: 大きな進捗を達成"]
    assert len(state.completed_tasks_this_week) == 1
    assert state.zombie_tasks[0].title == "停滞タスク"
    assert state.unprocessed_memos[0].title == "メモA"
    assert state.recommendations, "推奨事項が生成されていません"
    assert state.data_loaded is True
