from __future__ import annotations

import uuid

import pytest

import logic.application.memo_to_task_application_service as memo_to_task_module
from agents.agent_conf import LLMProvider, OpenVINODevice
from agents.task_agents.memo_to_task.schema import TaskDraft
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from logic.application.memo_to_task_application_service import (
    RECOMMENDED_TASK_COUNT_BY_LEVEL,
    MemoToTaskApplicationService,
)
from models import MemoRead, MemoStatus
from settings.models import AgentDetailLevel


@pytest.fixture
def memo() -> MemoRead:
    return MemoRead(id=uuid.uuid4(), title="memo", content="body", status=MemoStatus.INBOX)


def test_clarify_memo_injects_prompt_overrides(monkeypatch: pytest.MonkeyPatch, memo: MemoRead) -> None:
    """MemoToTask エージェント呼び出し時にプロンプトオーバーライドが state に注入されることを検証する。"""
    instructions = "出力は丁寧に"

    class PromptStub:
        def __init__(self) -> None:
            self.custom_instructions = instructions
            self.detail_level = AgentDetailLevel.DETAILED

    class AgentsStub:
        def __init__(self) -> None:
            self.provider = LLMProvider.GOOGLE
            self.runtime = type("RuntimeStub", (), {"device": OpenVINODevice.CPU})()
            self.memo_to_task_prompt = PromptStub()

    class SettingsStub:
        def __init__(self) -> None:
            self._agents = AgentsStub()

        def get_agents_settings(self) -> AgentsStub:
            return self._agents

    monkeypatch.setattr(memo_to_task_module.SettingsApplicationService, "get_instance", lambda: SettingsStub())

    captured_state: dict[str, object] = {}

    def _fake_collect(self: MemoToTaskApplicationService) -> list[str]:
        return ["work"]

    def _fake_invoke(
        self: MemoToTaskApplicationService,
        state: dict[str, object],
    ) -> MemoToTaskResult:
        captured_state.update(state)
        return MemoToTaskResult(
            tasks=[TaskDraft(title="t", description=None)],
            suggested_memo_status="active",
            processed_data=MemoToTaskState,
        )

    monkeypatch.setattr(memo_to_task_module.MemoToTaskApplicationService, "_collect_existing_tag_names", _fake_collect)
    monkeypatch.setattr(memo_to_task_module.MemoToTaskApplicationService, "_invoke_agent", _fake_invoke)

    service = MemoToTaskApplicationService()

    overrides = service.get_prompt_overrides_snapshot()
    assert overrides["custom_instructions"] == instructions
    assert "5 件" in overrides["task_count_hint"]
    assert overrides["recommended_task_count"] == RECOMMENDED_TASK_COUNT_BY_LEVEL[AgentDetailLevel.DETAILED]
    assert service.get_configured_provider() == LLMProvider.GOOGLE
    assert service.get_configured_device() == OpenVINODevice.CPU.value

    service.clarify_memo(memo)

    assert captured_state["custom_instructions"] == instructions
    assert "丁寧" in str(captured_state["detail_hint"])
    expected_count = RECOMMENDED_TASK_COUNT_BY_LEVEL[AgentDetailLevel.DETAILED]
    assert f"{expected_count} 件" in str(captured_state["task_count_hint"])
    assert captured_state["recommended_task_count"] == expected_count
