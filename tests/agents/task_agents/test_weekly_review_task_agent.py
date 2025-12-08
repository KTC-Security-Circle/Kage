from __future__ import annotations

import uuid

from agents.agent_conf import LLMProvider
from agents.task_agents.weekly_review_actions.agent import WeeklyReviewTaskAgent
from models import WeeklyReviewSplitTarget


def _sample_target() -> WeeklyReviewSplitTarget:
    return WeeklyReviewSplitTarget(
        task_id=uuid.uuid4(),
        title="停滞タスクA",
        stale_days=10,
        context="仕様検討で止まっている",
    )


def test_plan_subtasks_returns_structured_plan() -> None:
    agent = WeeklyReviewTaskAgent(provider=LLMProvider.FAKE)
    target = _sample_target()

    plans = agent.plan_subtasks([target])

    assert plans, "少なくとも1件のプランが返ること"
    assert plans[0].subtasks, "サブタスクが生成されること"
    assert plans[0].parent_task_id == target.task_id


def test_plan_subtasks_handles_empty_targets() -> None:
    agent = WeeklyReviewTaskAgent(provider=LLMProvider.FAKE)

    assert agent.plan_subtasks([]) == []
