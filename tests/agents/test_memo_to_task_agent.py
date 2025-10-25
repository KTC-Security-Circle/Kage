import pytest

from agents.agent_conf import LLMProvider
from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
from agents.task_agents.memo_to_task.state import MemoToTaskState


class _StubAgent:
    def __init__(self, response: MemoToTaskAgentOutput) -> None:
        self._response = response

    def invoke(self, *_args: object, **_kwargs: object) -> MemoToTaskAgentOutput:
        return self._response


def _build_state() -> MemoToTaskState:
    return {
        "memo_text": "会議のメモ",
        "existing_tags": ["仕事", "プライベート"],
        "current_datetime_iso": "2025-10-25T10:00:00+09:00",
        "final_response": "",
    }


def test_memo_to_task_handles_non_actionable(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    response = MemoToTaskAgentOutput(tasks=[], suggested_memo_status="idea")
    monkeypatch.setattr(agent, "_create_agent", lambda: _StubAgent(response))

    state = _build_state()
    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskAgentOutput)
    assert result.tasks == []
    assert result.suggested_memo_status == "idea"


def test_memo_to_task_routes_quick_action(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    response = MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="5分ミーティング",
                description="要点だけ確認",
                estimate_minutes=1,
            )
        ],
        suggested_memo_status="active",
    )
    monkeypatch.setattr(agent, "_create_agent", lambda: _StubAgent(response))

    state = _build_state()
    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskAgentOutput)
    assert result.tasks[0].route == "progress"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_routes_delegate(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    response = MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="資料レビュー依頼",
                description="上長に確認を依頼",
                route="waiting",
            )
        ],
        suggested_memo_status="active",
    )
    monkeypatch.setattr(agent, "_create_agent", lambda: _StubAgent(response))

    state = _build_state()
    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskAgentOutput)
    assert result.tasks[0].route == "waiting"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_schedules_calendar(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    response = MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="打ち合わせ",
                description="来週の進捗確認",
                due_date="2025-11-01",
            )
        ],
        suggested_memo_status="active",
    )
    monkeypatch.setattr(agent, "_create_agent", lambda: _StubAgent(response))

    state = _build_state()
    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskAgentOutput)
    assert result.tasks[0].route == "calendar"
    assert result.tasks[0].due_date == "2025-11-01"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_handles_project(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    response = MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="資料構成を決める",
                description="全体構成を検討",
            ),
            TaskDraft(
                title="ドラフトを書く",
                description="初稿を作成",
            ),
        ],
        suggested_memo_status="active",
    )
    monkeypatch.setattr(agent, "_create_agent", lambda: _StubAgent(response))

    state = _build_state()
    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskAgentOutput)
    assert result.tasks[0].route == "next_action"
    assert result.tasks[0].project_title is not None
    assert all(task.project_title == result.tasks[0].project_title for task in result.tasks)
    assert result.suggested_memo_status == "active"
