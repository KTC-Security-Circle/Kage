from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import cast

from agents.agent_conf import LLMProvider
from agents.task_agents.review_copilot.agent import ReviewCopilotAgent
from agents.task_agents.review_copilot.highlights_agent import HighlightBullet
from agents.task_agents.review_copilot.memo_audit_agent import MemoAuditOutputItem
from agents.task_agents.review_copilot.zombie_agent import ZombieAction, ZombieTaskOutput
from models import CompletedTaskDigest, MemoAuditDigest, ZombieTaskDigest
from settings.models import AgentDetailLevel


class _StubHighlightsAgent:
    def __init__(self) -> None:
        self.last_state: dict[str, object] | None = None

    def invoke(self, state: dict[str, object], thread_id: str) -> SimpleNamespace:
        self.last_state = state
        bullet = HighlightBullet(title="done", description="desc")
        return SimpleNamespace(intro="great", bullets=[bullet])


class _StubZombieAgent:
    def __init__(self) -> None:
        self.last_state: dict[str, object] | None = None

    def invoke(self, state: dict[str, object], thread_id: str) -> SimpleNamespace:
        self.last_state = state
        action = ZombieAction(action="split", rationale="理由", suggested_subtasks=[])
        output = ZombieTaskOutput(title="task", summary="summary", suggestions=[action])
        return SimpleNamespace(tasks=[output])


class _StubMemoAgent:
    def __init__(self) -> None:
        self.last_state: dict[str, object] | None = None

    def invoke(self, state: dict[str, object], thread_id: str) -> SimpleNamespace:
        self.last_state = state
        item = MemoAuditOutputItem(summary="memo", recommended_route="task", guidance="go")
        return SimpleNamespace(audits=[item])


def _sample_completed_digest() -> CompletedTaskDigest:
    """テスト用の完了タスクダイジェストを生成する。"""
    task = cast("TaskRead", SimpleNamespace(id=uuid.uuid4(), title="Task A", description="desc"))
    return CompletedTaskDigest(task=task, memo_excerpt="excerpt", project_title=None)


def _sample_zombie_digest() -> ZombieTaskDigest:
    """テスト用のゾンビタスクダイジェストを生成する。"""
    task = cast("TaskRead", SimpleNamespace(id=uuid.uuid4(), title="Task B", description="desc"))
    return ZombieTaskDigest(task=task, stale_days=10, memo_excerpt=None, project_title=None)


def _sample_memo_digest() -> MemoAuditDigest:
    """テスト用のメモ監査ダイジェストを生成する。"""
    memo = cast("MemoRead", SimpleNamespace(id=uuid.uuid4(), title="Memo", content="body"))
    return MemoAuditDigest(memo=memo, linked_project=None)


def test_review_copilot_attaches_prompt_overrides() -> None:
    """ReviewCopilotAgent が各サブエージェントへプロンプトオーバーライドを適用することを検証する。"""
    agent = ReviewCopilotAgent(
        provider=LLMProvider.FAKE,
        prompt_custom_instructions="丁寧に詳しく",
        prompt_detail_level=AgentDetailLevel.BRIEF,
    )
    highlights_stub = _StubHighlightsAgent()
    zombie_stub = _StubZombieAgent()
    memo_stub = _StubMemoAgent()
    agent._highlights_agent = cast("object", highlights_stub)
    agent._zombie_agent = cast("object", zombie_stub)
    agent._memo_agent = cast("object", memo_stub)

    agent.build_highlights([_sample_completed_digest()])
    agent.build_zombie_suggestions([_sample_zombie_digest()], zombie_threshold_days=7)
    agent.build_memo_audits([_sample_memo_digest()])

    assert highlights_stub.last_state is not None
    assert highlights_stub.last_state["custom_instructions"] == "丁寧に詳しく"
    assert "簡潔" in str(highlights_stub.last_state["detail_hint"])

    assert zombie_stub.last_state is not None
    assert zombie_stub.last_state["custom_instructions"] == "丁寧に詳しく"
    assert "簡潔" in str(zombie_stub.last_state["detail_hint"])

    assert memo_stub.last_state is not None
    assert memo_stub.last_state["custom_instructions"] == "丁寧に詳しく"
    assert "簡潔" in str(memo_stub.last_state["detail_hint"])
