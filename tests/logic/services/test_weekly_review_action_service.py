"""WeeklyReviewActionService のユニットテスト。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from agents.base import AgentError
from agents.task_agents.weekly_review_actions import WeeklyReviewTaskAgent
from errors import NotFoundError
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.services.weekly_review_action_service import WeeklyReviewActionService
from models import (
    TaskStatus,
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
    agent = MagicMock(spec=WeeklyReviewTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    plan = _build_plan(task.id)
    agent.plan_subtasks.return_value = [plan]
    created_id = uuid.uuid4()
    task_repo.create.return_value = SimpleNamespace(id=created_id)

    service = WeeklyReviewActionService(task_repo, tag_repo, agent)
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
    agent = MagicMock(spec=WeeklyReviewTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    tag_repo.get_by_name.side_effect = NotFoundError("missing")
    tag_repo.create.return_value = SimpleNamespace(id=uuid.uuid4())

    service = WeeklyReviewActionService(task_repo, tag_repo, agent)
    decision = WeeklyReviewTaskDecision(task_id=task.id, action="someday")

    result = service.apply_actions([decision])

    assert result.moved_to_someday == 1
    assert result.someday_task_ids == [task.id]
    tag_repo.create.assert_called_once()
    task_repo.add_tag.assert_called_once()


def test_apply_actions_handles_agent_error() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)

    task = _build_task()
    task_repo.get_by_id.return_value = task
    agent.plan_subtasks.side_effect = AgentError("失敗")

    service = WeeklyReviewActionService(task_repo, tag_repo, agent)
    decision = WeeklyReviewTaskDecision(task_id=task.id, action="split")

    result = service.apply_actions([decision])

    assert result.created_subtasks == 0
    assert result.errors


def test_apply_actions_deletes_tasks() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    tag_repo = MagicMock(spec=TagRepository)
    agent = MagicMock(spec=WeeklyReviewTaskAgent)

    task_repo.delete.return_value = True
    task_repo.get_by_id.return_value = _build_task()

    service = WeeklyReviewActionService(task_repo, tag_repo, agent)
    decision = WeeklyReviewTaskDecision(task_id=uuid.uuid4(), action="delete")

    result = service.apply_actions([decision])

    assert result.deleted_tasks == 1
    assert result.deleted_task_ids == [decision.task_id]
    task_repo.delete.assert_called_once()
