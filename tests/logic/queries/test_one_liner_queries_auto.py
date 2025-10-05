"""one_liner_queries の自動集計ビルダーテスト"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from logic.queries.one_liner_queries import _TaskMetricsProvider, build_one_liner_context_auto  # [AI GENERATED]

# 空行維持

if TYPE_CHECKING:  # [AI GENERATED] 型チェック専用
    from logic.queries.task_queries import GetTodayTasksCountQuery


@dataclass
class _FakeTaskAppService(_TaskMetricsProvider):  # type: ignore[misc]  # [AI GENERATED] Protocol 直接実装
    today: int
    completed: int
    overdue: int

    def get_today_tasks_count(self, _query: GetTodayTasksCountQuery) -> int:  # [AI GENERATED] 単純委譲
        return self.today

    def get_completed_tasks_count(self) -> int:  # [AI GENERATED]
        return self.completed

    def get_overdue_tasks_count(self) -> int:  # [AI GENERATED]
        return self.overdue


@pytest.mark.parametrize(
    ("today", "completed", "overdue"),
    [
        (0, 0, 0),
        (3, 1, 0),
        (5, 2, 1),
    ],
)
def test_build_one_liner_context_auto_counts(today: int, completed: int, overdue: int) -> None:
    ctx = build_one_liner_context_auto(
        task_app_service_factory=lambda: _FakeTaskAppService(today, completed, overdue),
        user_name="tester",
    )
    assert ctx.today_task_count == today
    assert ctx.completed_task_count == completed
    assert ctx.overdue_task_count == overdue
    assert ctx.user_name == "tester"
