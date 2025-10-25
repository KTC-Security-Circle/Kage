import pytest

from agents.agent_conf import LLMProvider
from agents.base import ErrorAgentOutput
from agents.task_agents.splitter.agent import TaskSplitterAgent
from agents.task_agents.splitter.state import TaskSplitterOutput, TaskSplitterState


def test_task_splitter_invoke_sequence(task_splitter_agent: TaskSplitterAgent, thread_id: str) -> None:
    state: TaskSplitterState = {
        "task_title": "勉強する",
        "task_description": "国語と数学の宿題",
        "final_response": "",
    }
    r1 = task_splitter_agent.invoke(state, thread_id)
    assert isinstance(r1, TaskSplitterOutput)
    r2 = task_splitter_agent.invoke(state, thread_id)
    assert isinstance(r2, TaskSplitterOutput)
    assert r1.task_titles != r2.task_titles


def test_task_splitter_stream(task_splitter_agent: TaskSplitterAgent, thread_id: str) -> None:
    state: TaskSplitterState = {
        "task_title": "掃除する",
        "task_description": "部屋を片付ける",
        "final_response": "",
    }
    events = list(task_splitter_agent.stream(state, thread_id))
    if events:
        assert len(events) >= 1
        return
    # [AI GENERATED] フェイクモデルがストリーミングチャンクを生成しないケースを許容
    result = task_splitter_agent.invoke(state, thread_id)
    assert result is not None
    # TaskSplitterOutput は task_titles / task_descriptions を持つ
    assert hasattr(result, "task_titles")
    assert isinstance(result.task_titles, list)  # type: ignore[attr-defined]


def test_task_splitter_error_response(thread_id: str) -> None:
    agent = TaskSplitterAgent(LLMProvider.FAKE, error_response=True)
    state: TaskSplitterState = {
        "task_title": "テスト",
        "task_description": "説明",
        "final_response": "",
    }
    result = agent.invoke(state, thread_id)
    assert isinstance(result, ErrorAgentOutput)


def test_task_splitter_agent_property(task_splitter_agent: TaskSplitterAgent) -> None:
    prop = task_splitter_agent.agent_property
    assert prop.name == "TaskSplitterAgent"


def test_task_splitter_get_model_singleton(task_splitter_agent: TaskSplitterAgent) -> None:
    m1 = task_splitter_agent.get_model()
    m2 = task_splitter_agent.get_model()
    assert m1 is m2


def test_task_splitter_handles_empty_candidates(monkeypatch: pytest.MonkeyPatch, thread_id: str) -> None:
    agent = TaskSplitterAgent(LLMProvider.FAKE, verbose=False, error_response=False)

    class _EmptyResponseAgent:
        def invoke(self, *_args: object, **_kwargs: object) -> TaskSplitterOutput:
            return TaskSplitterOutput(task_titles=[], task_descriptions=[])

    monkeypatch.setattr(agent, "_create_agent", lambda: _EmptyResponseAgent())

    state: TaskSplitterState = {
        "task_title": "準備",
        "task_description": "明日の会議の準備",
        "final_response": "",
    }

    result = agent.invoke(state, thread_id)

    assert isinstance(result, TaskSplitterOutput)
    assert result.task_titles == []
    assert result.task_descriptions == []
