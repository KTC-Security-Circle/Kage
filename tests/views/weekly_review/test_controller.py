"""WeeklyReviewController の挙動を検証するテスト。"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from logic.application.memo_application_service import MemoApplicationService
from logic.application.review_application_service import WeeklyReviewApplicationService
from logic.application.task_application_service import TaskApplicationService
from models import (
    MemoAuditInsight,
    ReviewPeriod,
    TaskRead,
    TaskStatus,
    WeeklyReviewActionResult,
    WeeklyReviewHighlightsItem,
    WeeklyReviewHighlightsPayload,
    WeeklyReviewInsights,
    WeeklyReviewMemoAuditPayload,
    WeeklyReviewMetadata,
    WeeklyReviewSplitTaskInfo,
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


def test_load_initial_data_handles_fetch_error() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    review_service.fetch_insights.side_effect = RuntimeError("fetch failed")

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    with pytest.raises(RuntimeError) as exc_info:
        controller.load_initial_data()
    assert "週次レビューデータの取得に失敗しました" in str(exc_info.value)


def test_load_initial_data_handles_missing_task_and_memo() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    task_id = uuid4()
    memo_id = uuid4()
    insights = _build_insights(task_id, memo_id)

    review_service.fetch_insights.return_value = insights
    # Simulate task/memo retrieval failures gracefully returning None
    task_service.get_by_id.side_effect = Exception("task lookup failed")
    memo_service.get_by_id.side_effect = Exception("memo lookup failed")

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    controller.load_initial_data()

    # Task/memo failures should not crash and should be excluded
    assert state.completed_tasks_this_week == []
    assert state.unprocessed_memos[0].title == "メモの要約"
    assert state.unprocessed_memos[0].content == "すぐにタスクに変換しましょう"
    assert state.data_loaded is True


def test_load_initial_data_empty_insights_lists() -> None:
    now = datetime.now()
    metadata = WeeklyReviewMetadata(
        period=ReviewPeriod(start=now - timedelta(days=7), end=now),
        generated_at=now,
        zombie_threshold_days=14,
        project_filters=[],
    )
    empty_insights = WeeklyReviewInsights(
        metadata=metadata,
        highlights=WeeklyReviewHighlightsPayload(status="ready", intro="", items=[]),
        zombie_tasks=WeeklyReviewZombiePayload(status="ready", tasks=[]),
        memo_audits=WeeklyReviewMemoAuditPayload(status="ready", audits=[]),
    )

    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    review_service.fetch_insights.return_value = empty_insights

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    controller.load_initial_data()

    assert state.achievement_highlights == []
    assert state.completed_tasks_this_week == []
    assert state.zombie_tasks == []
    assert state.unprocessed_memos == []
    assert state.recommendations == []
    assert state.data_loaded is True


def test_execute_task_actions_builds_decisions() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    review_service.apply_actions.return_value = WeeklyReviewActionResult(message="ok")

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    task_id = uuid4()
    state.zombie_task_decisions[str(task_id)] = "subdivide"

    result = controller.execute_task_actions()

    assert result.message == "ok"
    sent_decisions = review_service.apply_actions.call_args.args[0]
    assert sent_decisions[0].action == "split"
    assert sent_decisions[0].task_id == task_id


def test_execute_task_actions_without_selection_raises() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    with pytest.raises(ValueError, match="アクションが選択されていません"):
        controller.execute_task_actions()


def test_execute_task_actions_records_split_drafts() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    parent_task_id = uuid4()
    split_id = uuid4()
    review_service.apply_actions.return_value = WeeklyReviewActionResult(
        split_tasks=[WeeklyReviewSplitTaskInfo(parent_task_id=parent_task_id, task_id=split_id)],
        split_task_ids=[split_id],
    )
    task_service.get_by_id.side_effect = [_build_task(split_id), _build_task(parent_task_id)]

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    state.zombie_task_decisions[str(parent_task_id)] = "subdivide"

    result = controller.execute_task_actions()

    assert result.split_task_ids == [split_id]
    drafts = state.get_split_drafts(str(parent_task_id))
    assert len(drafts) == 1
    assert str(drafts[0].id) == str(split_id)
    assert state.get_split_parent_title(str(parent_task_id)) is not None


def test_execute_task_actions_marks_completed_for_someday_and_delete() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    someday_task_id = uuid4()
    delete_task_id = uuid4()
    state.zombie_task_decisions[str(someday_task_id)] = "someday"
    state.zombie_task_decisions[str(delete_task_id)] = "delete"

    review_service.apply_actions.return_value = WeeklyReviewActionResult(
        moved_to_someday=1,
        someday_task_ids=[someday_task_id],
        deleted_tasks=1,
        deleted_task_ids=[delete_task_id],
    )

    controller.execute_task_actions()

    assert state.is_zombie_task_completed(str(someday_task_id))
    assert state.is_zombie_task_completed(str(delete_task_id))


def test_approve_split_task_updates_status_and_state() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    parent_id = uuid4()
    task_id = uuid4()
    draft = _build_task(task_id)
    state.add_split_draft_tasks(str(parent_id), "親タスク", [draft])
    task_service.update.return_value = draft

    controller.approve_split_task(str(task_id))

    update_args = task_service.update.call_args.args[1]
    assert update_args.status == TaskStatus.TODO
    assert state.get_split_drafts(str(parent_id)) == []
    assert state.is_zombie_task_completed(str(parent_id))


def test_discard_split_task_removes_state() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    controller = WeeklyReviewController(
        task_app_service=task_service,
        review_app_service=review_service,
        memo_app_service=memo_service,
        state=state,
    )

    parent_id = uuid4()
    task_id = uuid4()
    state.add_split_draft_tasks(str(parent_id), "親タスク", [_build_task(task_id)])
    task_service.delete.return_value = True

    controller.discard_split_task(str(task_id))

    task_service.delete.assert_called_once()
    assert state.get_split_drafts(str(parent_id)) == []
    assert state.is_zombie_task_completed(str(parent_id))


def test_zombie_insight_without_suggestions_uses_excerpt() -> None:
    state = WeeklyReviewState()
    task_service = MagicMock(spec=TaskApplicationService)
    review_service = MagicMock(spec=WeeklyReviewApplicationService)
    memo_service = MagicMock(spec=MemoApplicationService)

    task_id = uuid4()
    memo_id = uuid4()
    insights = _build_insights(task_id, memo_id)

    # frozenモデルのため再構築して差し替え
    modified_zombie = WeeklyReviewZombiePayload(
        status="ready",
        tasks=[
            ZombieTaskInsight(
                task_id=uuid4(),
                title="停滞タスクB",
                stale_days=30,
                project_title=None,
                memo_excerpt="メモ抜粋",
                suggestions=[],
            )
        ],
    )
    insights = WeeklyReviewInsights(
        metadata=insights.metadata,
        highlights=insights.highlights,
        zombie_tasks=modified_zombie,
        memo_audits=insights.memo_audits,
    )

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

    assert state.zombie_tasks[0].reason.startswith("30日停滞")
    assert "メモ抜粋" in state.zombie_tasks[0].reason
