"""WeeklyReviewInsightsService のユニットテスト。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from agents.task_agents.review_copilot import ReviewCopilotAgent
from errors import NotFoundError
from logic.repositories.memo import MemoRepository
from logic.repositories.project import ProjectRepository
from logic.repositories.task import TaskRepository
from logic.services.weekly_review_service import WeeklyReviewInsightsService
from models import MemoStatus, TaskStatus, WeeklyReviewInsightsQuery
from settings.models import ReviewSettings


def _build_task(title: str, *, created_offset: int, completed_offset: int | None = None) -> SimpleNamespace:
    now = datetime.now()
    completed_at = now - timedelta(days=completed_offset or 0) if completed_offset is not None else None
    return SimpleNamespace(
        id=uuid.uuid4(),
        title=title,
        description=f"{title} 詳細",
        status=TaskStatus.COMPLETED if completed_at else TaskStatus.PROGRESS,
        created_at=now - timedelta(days=created_offset),
        completed_at=completed_at,
        memo=SimpleNamespace(content=f"{title} memo"),
        project=SimpleNamespace(title="Project X"),
    )


def _build_memo(title: str, *, status: MemoStatus = MemoStatus.INBOX) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        title=title,
        content=f"{title} content",
        status=status,
        created_at=datetime.now(),
        tasks=[],
    )


def test_generate_insights_happy_path() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    project_repo = MagicMock(spec=ProjectRepository)

    task_repo.list_completed_between.return_value = [_build_task("完了A", created_offset=3, completed_offset=1)]
    task_repo.list_stale_tasks.return_value = [_build_task("停滞B", created_offset=20)]
    memo_repo.list_unprocessed_memos.side_effect = [
        [_build_memo("メモC")],
        [_build_memo("メモIdea", status=MemoStatus.IDEA)],
    ]
    project_repo.list_by_status.return_value = [SimpleNamespace(id=uuid.uuid4(), title="Project X")]

    review_settings = ReviewSettings()
    service = WeeklyReviewInsightsService(task_repo, memo_repo, project_repo, ReviewCopilotAgent(), review_settings)

    result = service.generate_insights(WeeklyReviewInsightsQuery())

    assert result.highlights.items
    assert result.zombie_tasks.tasks
    assert result.memo_audits.audits
    assert result.metadata.period.start <= result.metadata.period.end


def test_generate_insights_handles_empty_sources() -> None:
    task_repo = MagicMock(spec=TaskRepository)
    memo_repo = MagicMock(spec=MemoRepository)
    project_repo = MagicMock(spec=ProjectRepository)

    task_repo.list_completed_between.side_effect = NotFoundError("no data")
    task_repo.list_stale_tasks.side_effect = NotFoundError("no data")
    memo_repo.list_unprocessed_memos.side_effect = [NotFoundError("no data"), NotFoundError("no data")]
    project_repo.list_by_status.side_effect = NotFoundError("no data")

    review_settings = ReviewSettings()
    service = WeeklyReviewInsightsService(task_repo, memo_repo, project_repo, ReviewCopilotAgent(), review_settings)

    result = service.generate_insights(WeeklyReviewInsightsQuery())

    assert result.highlights.status == "fallback"
    assert result.zombie_tasks.tasks == []
    assert result.memo_audits.audits == []
