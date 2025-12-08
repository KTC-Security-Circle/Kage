"""WeeklyReviewActionService のユニットテスト。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from agents.base import AgentError
from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
from agents.task_agents.memo_to_task.schema import TaskDraft
from agents.task_agents.weekly_review_actions import WeeklyReviewTaskAgent
from errors import NotFoundError
from logic.repositories.memo import MemoRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.services.weekly_review_action_service import WeeklyReviewActionService
from models import (
    AiSuggestionStatus,
    MemoStatus,
    TaskStatus,
    WeeklyReviewMemoDecision,
    WeeklyReviewSplitPlan,
    WeeklyReviewSplitSubtask,
    WeeklyReviewTaskDecision,
)


def _build_task(created_days_ago: int = 10) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        title="停滞タスク",
        description="詳細",
        created_at=datetime.now() - timedelta(days=created_days_ago),
        project_id=None,
        memo_id=None,
        memo=SimpleNamespace(content="memo content"),
    )


def _build_memo() -> SimpleNamespace:
    now = datetime.now()
    return SimpleNamespace(
        id=uuid.uuid4(),
        title="未処理メモ",
        content="メモ本文",
        status=MemoStatus.INBOX,
        ai_suggestion_status=AiSuggestionStatus.NOT_REQUESTED,
        ai_analysis_log=None,
        created_at=now,
        updated_at=now,
        processed_at=None,
        tags=[],
        tasks=[],
    )


def _build_plan(task_id: uuid.UUID) -> WeeklyReviewSplitPlan:
    return WeeklyReviewSplitPlan(
        parent_task_id=task_id,
        rationale="理由",
        subtasks=[
            WeeklyReviewSplitSubtask(
                title="サブタスク",
                description="説明",
                first_step_hint="一歩目",
                estimate_minutes=30,
            )
        ],
    )


def test_apply_actions_creates_subtasks_and_updates_parent() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    plan = _build_plan(task.id)
    agent.plan_subtasks.return_value = [plan]
    created_id = uuid.uuid4()
    task_repo.create.return_value = SimpleNamespace(id=created_id)

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, agent, memo_agent)
    decision = WeeklyReviewTaskDecision(task_id=task.id, action="split")

    result = service.apply_actions([decision])

    assert result.created_subtasks == 1
    assert result.split_task_ids == [created_id]
    assert len(result.split_tasks) == 1
    assert result.split_tasks[0].task_id == created_id
    task_repo.create.assert_called_once()
    created_model = task_repo.create.call_args.args[0]
    assert created_model.status == TaskStatus.DRAFT
    update_args, _ = task_repo.update.call_args
    assert update_args[0] == task.id
    assert update_args[1].status == TaskStatus.PROGRESS


def test_apply_actions_moves_tasks_to_someday_and_creates_tag() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    tag_repo.get_by_name.side_effect = NotFoundError("missing")
    tag_repo.create.return_value = SimpleNamespace(id=uuid.uuid4())

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, agent, memo_agent)
    decision = WeeklyReviewTaskDecision(task_id=task.id, action="someday")

    result = service.apply_actions([decision])

    assert result.moved_to_someday == 1
    assert result.someday_task_ids == [task.id]
    tag_repo.create.assert_called_once()
    task_repo.add_tag.assert_called_once()


def test_apply_actions_handles_agent_error() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    agent.plan_subtasks.side_effect = AgentError("失敗")

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, agent, memo_agent)
    decision = WeeklyReviewTaskDecision(task_id=task.id, action="split")

    result = service.apply_actions([decision])

    assert result.created_subtasks == 0
    assert result.errors


def test_apply_actions_deletes_tasks() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    task_repo.delete.return_value = True
    task_repo.get_by_id.return_value = _build_task()

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, agent, memo_agent)
    decision = WeeklyReviewTaskDecision(task_id=uuid.uuid4(), action="delete")

    result = service.apply_actions([decision])

    assert result.deleted_tasks == 1
    assert result.deleted_task_ids == [decision.task_id]
    task_repo.delete.assert_called_once()


def test_apply_actions_creates_memo_tasks() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    task_agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    memo = _build_memo()
    memo_repo.get_by_id.return_value = memo
    created_task_id = uuid.uuid4()
    task_repo.create.return_value = SimpleNamespace(id=created_task_id)
    memo_agent.invoke.return_value = SimpleNamespace(
        tasks=[
            TaskDraft(
                title="DraftTask",
                description="Desc",
                due_date="2025-01-01",
                tags=None,
                route="next_action",
            )
        ]
    )

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, task_agent, memo_agent)
    memo_decision = WeeklyReviewMemoDecision(memo_id=memo.id, action="create_task")

    result = service.apply_actions([], [memo_decision])

    assert result.memo_tasks_created == 1
    assert result.memo_task_ids == [created_task_id]
    memo_repo.update.assert_called()
    update_model = memo_repo.update.call_args.args[1]
    assert update_model.status == MemoStatus.ACTIVE


def test_apply_actions_archives_and_skips_memos() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    task_agent = MagicMock(spec=WeeklyReviewTaskAgent)
    memo_agent = MagicMock(spec=MemoToTaskAgent)

    memo_one = _build_memo()
    memo_two = _build_memo()
    memo_repo.get_by_id.side_effect = [memo_one, memo_two]

    service = WeeklyReviewActionService(task_repo, tag_repo, memo_repo, task_agent, memo_agent)
    archive_decision = WeeklyReviewMemoDecision(memo_id=memo_one.id, action="archive")
    skip_decision = WeeklyReviewMemoDecision(memo_id=memo_two.id, action="skip")

    result = service.apply_actions([], [archive_decision, skip_decision])

    assert result.memos_archived == 1
    assert result.archived_memo_ids == [memo_one.id]
    assert result.memos_skipped == 1
    assert result.skipped_memo_ids == [memo_two.id]
    statuses = [call.args[1].status for call in memo_repo.update.call_args_list]
    assert MemoStatus.IDEA in statuses
    assert MemoStatus.ARCHIVE in statuses
