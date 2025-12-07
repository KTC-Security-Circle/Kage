"""ApplicationHomeQueryのユニットテスト。"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Never
from uuid import uuid4

if TYPE_CHECKING:
    import pytest

from models import (
    AiSuggestionStatus,
    MemoRead,
    MemoStatus,
    ProjectRead,
    ProjectStatus,
    TaskRead,
    TaskStatus,
)
from views.home.query import ApplicationHomeQuery, OneLinerServicePort


class FakeMemoService:
    """MemoApplicationService互換のフェイク。"""

    def __init__(self, memos: list[MemoRead]) -> None:
        self._memos = memos

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        return self._memos


class FakeTaskService:
    """TaskApplicationService互換のフェイク。"""

    def __init__(self, tasks: list[TaskRead]) -> None:
        self._tasks = tasks

    def get_all_tasks(self) -> list[TaskRead]:
        return self._tasks


class FakeProjectService:
    """ProjectApplicationService互換のフェイク。"""

    def __init__(self, projects: list[ProjectRead]) -> None:
        self._projects = projects

    def get_all_projects(self) -> list[ProjectRead]:
        return self._projects


class FakeOneLinerService(OneLinerServicePort):
    """OneLinerApplicationService互換のフェイク。"""

    def __init__(self, message: str = "AIメッセージ", *, should_raise: bool = False) -> None:
        self._message = message
        self._should_raise = should_raise
        self.call_count = 0

    def generate_one_liner(self, query: object | None = None) -> str:
        self.call_count += 1
        if self._should_raise:
            error_message = "one liner generation failed"
            raise RuntimeError(error_message)
        return self._message


def _memo(
    *,
    title: str,
    content: str = "",
    status: MemoStatus = MemoStatus.INBOX,
    ai_status: AiSuggestionStatus = AiSuggestionStatus.NOT_REQUESTED,
    created_at: datetime,
) -> MemoRead:
    """テスト用のMemoReadインスタンスを生成する。"""
    return MemoRead(
        id=uuid4(),
        title=title,
        content=content,
        status=status,
        ai_suggestion_status=ai_status,
        created_at=created_at,
        updated_at=created_at,
    )


def _task(*, title: str, status: TaskStatus) -> TaskRead:
    """テスト用のTaskReadインスタンスを生成する。"""
    return TaskRead(
        id=uuid4(),
        title=title,
        status=status,
    )


def _project(*, title: str, status: ProjectStatus) -> ProjectRead:
    """テスト用のProjectReadインスタンスを生成する。"""
    return ProjectRead(
        id=uuid4(),
        title=title,
        status=status,
    )


def _create_query(
    *,
    memos: list[MemoRead],
    tasks: list[TaskRead],
    projects: list[ProjectRead],
    one_liner_service: OneLinerServicePort | None = None,
) -> ApplicationHomeQuery:
    """フェイクサービスを束ねたQueryを生成する。"""
    service = one_liner_service or FakeOneLinerService()
    return ApplicationHomeQuery(
        memo_service=FakeMemoService(memos),
        task_service=FakeTaskService(tasks),
        project_service=FakeProjectService(projects),
        one_liner_service=service,
    )


def test_get_inbox_memos_filters_and_sorts() -> None:
    """Inboxメモのみが新しい順に返ること。"""
    now = datetime.now()
    memos = [
        _memo(title="古いメモ", created_at=now - timedelta(days=1)),
        _memo(title="最新メモ", created_at=now),
        _memo(title="アクティブ", status=MemoStatus.ACTIVE, created_at=now),
    ]
    query = _create_query(memos=memos, tasks=[], projects=[])

    inbox_memos = query.get_inbox_memos()

    assert [memo["title"] for memo in inbox_memos] == ["最新メモ", "古いメモ"]
    assert inbox_memos[0]["ai_suggestion_status"] == AiSuggestionStatus.NOT_REQUESTED.value


def test_get_stats_counts_tasks_and_projects() -> None:
    """タスクとプロジェクトの集計結果を返すこと。"""
    tasks = [
        _task(title="T1", status=TaskStatus.TODAYS),
        _task(title="T2", status=TaskStatus.TODAYS),
        _task(title="T3", status=TaskStatus.TODO),
    ]
    projects = [
        _project(title="P1", status=ProjectStatus.ACTIVE),
        _project(title="P2", status=ProjectStatus.ON_HOLD),
    ]
    query = _create_query(memos=[], tasks=tasks, projects=projects)

    stats = query.get_stats()

    expected_todays_count = 2
    expected_todo_count = 1
    expected_active_projects = 1

    assert stats["todays_tasks"] == expected_todays_count
    assert stats["todo_tasks"] == expected_todo_count
    assert stats["active_projects"] == expected_active_projects


def test_daily_review_prefers_overdue_tasks() -> None:
    """期限超過タスクのシナリオは即時描画用メッセージを返し、OneLinerは呼ばれない。"""
    tasks = [
        _task(title="Overdue", status=TaskStatus.OVERDUE),
        _task(title="Todo", status=TaskStatus.TODO),
    ]
    memos = [_memo(title="Inbox", created_at=datetime.now())]
    one_liner = FakeOneLinerService(message="AIの一言")
    query = _create_query(memos=memos, tasks=tasks, projects=[], one_liner_service=one_liner)

    review = query.get_daily_review()

    assert review["icon"] == "error"
    assert "期限超過タスク" in review["message"]
    assert review["action_route"] == "/tasks"
    assert one_liner.call_count == 0


def test_get_one_liner_message_returns_ai_text() -> None:
    """OneLiner生成APIは専用メソッド経由で呼び出される。"""
    one_liner = FakeOneLinerService(message="AIの一言")
    query = _create_query(memos=[], tasks=[], projects=[], one_liner_service=one_liner)

    message = query.get_one_liner_message()

    assert message == "AIの一言"
    assert one_liner.call_count == 1


def test_daily_review_fallback_when_one_liner_fails() -> None:
    """OneLiner生成に失敗した場合は従来のメッセージを保持する。"""
    tasks = [_task(title="Overdue", status=TaskStatus.OVERDUE)]
    memos = []
    query = _create_query(
        memos=memos,
        tasks=tasks,
        projects=[],
        one_liner_service=FakeOneLinerService(should_raise=True),
    )

    review = query.get_daily_review()

    assert "期限超過タスク" in review["message"]


def test_get_tasks_handles_not_found_error_and_returns_empty(caplog: pytest.LogCaptureFixture) -> None:
    """TaskServiceが NotFoundError を送出する場合、get_daily_review は空データを扱えること。"""

    from errors import NotFoundError

    class BrokenTaskService:
        def get_all_tasks(self) -> Never:
            msg = "no tasks in db"
            raise NotFoundError(msg)

    memos = []
    projects: list[ProjectRead] = []

    query = ApplicationHomeQuery(
        memo_service=FakeMemoService(memos),
        task_service=BrokenTaskService(),
        project_service=FakeProjectService(projects),
        one_liner_service=FakeOneLinerService(),
    )

    caplog.set_level(logging.INFO)
    review = query.get_daily_review()

    # タスクが見つからない -> 空扱い -> レビューはデフォルトの low priority シナリオ
    assert isinstance(review, dict)
    assert "message" in review
    assert any("No tasks found" in r.message for r in caplog.records)
