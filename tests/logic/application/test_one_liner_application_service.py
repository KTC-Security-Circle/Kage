from __future__ import annotations

from types import SimpleNamespace
from typing import ClassVar

import pytest

import logic.application.one_liner_application_service as one_liner_module
from agents.agent_conf import HuggingFaceModel, LLMProvider
from agents.task_agents.one_liner.state import OneLinerState
from logic.application.one_liner_application_service import (
    OneLinerApplicationService,
    OneLinerServiceError,
)
from models import TaskStatus


@pytest.fixture
def stub_agent(monkeypatch: pytest.MonkeyPatch) -> type:
    """OneLinerAgent をスタブ化し、挙動をテストごとに制御できるようにする。"""

    class DummyAgent:
        """テスト専用の簡易エージェント。"""

        last_init: ClassVar[tuple[LLMProvider, HuggingFaceModel | str | None] | None] = None
        invoke_result: ClassVar[object] = SimpleNamespace(response="ok")
        invocations: ClassVar[list[tuple[OneLinerState, str]]] = []

        def __init__(self, provider: LLMProvider, *, model_name: HuggingFaceModel | str | None = None) -> None:
            type(self).last_init = (provider, model_name)

        def invoke(self, state: OneLinerState, thread_id: str) -> object:
            type(self).invocations.append((state, thread_id))
            return type(self).invoke_result

    monkeypatch.setattr(one_liner_module, "OneLinerAgent", DummyAgent)
    DummyAgent.last_init = None
    DummyAgent.invoke_result = SimpleNamespace(response="ok")
    DummyAgent.invocations = []
    return DummyAgent


def _stub_config(
    monkeypatch: pytest.MonkeyPatch,
    *,
    provider: LLMProvider,
    model: HuggingFaceModel | str | None,
    user_name: str = "Tester",
) -> None:
    """設定マネージャーを差し替えて、テスト用設定を返す。"""

    class AgentsStub:
        def __init__(self, provider_value: LLMProvider, model_value: HuggingFaceModel | str | None) -> None:
            self.provider = provider_value
            self._model_value = model_value

        def get_model_name(self, _: str) -> HuggingFaceModel | str | None:
            return self._model_value

    settings = SimpleNamespace(
        agents=AgentsStub(provider, model),
        user=SimpleNamespace(user_name=user_name),
    )
    config_manager = SimpleNamespace(settings=settings)
    monkeypatch.setattr(one_liner_module, "get_config_manager", lambda: config_manager)


def test_openvino_string_model_raises_service_error(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """OPENVINO で文字列モデルを指定した場合に例外が送出されることを検証する。"""

    _stub_config(monkeypatch, provider=LLMProvider.FAKE, model=HuggingFaceModel.QWEN_3_8B_INT4)

    with pytest.raises(OneLinerServiceError) as exc:
        OneLinerApplicationService(provider=LLMProvider.OPENVINO, model_name="invalid-model")

    assert "Enum 型で指定してください" in str(exc.value)
    assert stub_agent.last_init is None


def test_openvino_enum_model_is_accepted(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """OPENVINO 環境で Enum モデル指定時に正しく初期化されることを確認する。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.OPENVINO,
        model=HuggingFaceModel.QWEN_3_8B_INT4,
    )

    service = OneLinerApplicationService()

    assert stub_agent.last_init == (LLMProvider.OPENVINO, HuggingFaceModel.QWEN_3_8B_INT4)
    assert service._get_default_message() == "今日も一日、お疲れさまです。"


def test_generate_one_liner_returns_agent_response(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """Google プロバイダの場合にエージェント応答がそのまま返されることを検証する。"""

    _stub_config(monkeypatch, provider=LLMProvider.GOOGLE, model="models/gemini-pro", user_name="Alice")
    stub_agent.invoke_result = SimpleNamespace(response="こんにちは")

    service = OneLinerApplicationService()

    query = OneLinerState(
        today_task_count=1,
        completed_task_count=0,
        overdue_task_count=0,
        progress_summary="",
        user_name="Bob",
        final_response="",
    )
    result = service.generate_one_liner(query)

    assert result == "こんにちは"
    assert stub_agent.last_init == (LLMProvider.GOOGLE, "models/gemini-pro")
    assert stub_agent.invocations[0][0]["user_name"] == "Bob"


def test_generate_one_liner_without_query_returns_default(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """自動コンテキスト構築時に応答が空ならデフォルトメッセージへフォールバックすることを検証する。"""

    _stub_config(monkeypatch, provider=LLMProvider.FAKE, model=HuggingFaceModel.QWEN_3_8B_INT4, user_name="Tester")
    stub_agent.invoke_result = SimpleNamespace(response="")

    class TaskServiceStub:
        def __init__(self) -> None:
            self._counts = {
                TaskStatus.TODAYS: 2,
                TaskStatus.COMPLETED: 1,
                TaskStatus.OVERDUE: 3,
            }

        def list_by_status(self, status: TaskStatus) -> list[int]:
            return [0] * self._counts.get(status, 0)

    class AppServicesStub:
        def __init__(self, task_service: TaskServiceStub) -> None:
            self._task_service = task_service

        def get_service(self, service_type: type) -> TaskServiceStub:
            assert service_type is one_liner_module.TaskApplicationService
            return self._task_service

    task_service = TaskServiceStub()
    app_services = AppServicesStub(task_service)
    monkeypatch.setattr(
        "logic.application.apps.ApplicationServices.create",
        lambda: app_services,
    )

    service = OneLinerApplicationService()
    result = service.generate_one_liner()

    assert result == "今日も一日、お疲れさまです。"
    generated_state = stub_agent.invocations[0][0]
    expected_counts = task_service._counts
    assert generated_state["today_task_count"] == expected_counts[TaskStatus.TODAYS]
    assert generated_state["completed_task_count"] == expected_counts[TaskStatus.COMPLETED]
    assert generated_state["overdue_task_count"] == expected_counts[TaskStatus.OVERDUE]
    assert generated_state["user_name"] == "Tester"
