from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar

import pytest

import logic.application.one_liner_application_service as one_liner_module
from agents.agent_conf import HuggingFaceModel, LLMProvider, OpenVINODevice
from logic.application.one_liner_application_service import (
    OneLinerApplicationService,
    OneLinerServiceError,
)
from models import TaskStatus

if TYPE_CHECKING:  # 型チェック専用のインポート
    from agents.task_agents.one_liner.state import OneLinerState


@pytest.fixture
def stub_agent(monkeypatch: pytest.MonkeyPatch) -> type:
    """OneLinerAgent をスタブ化し、挙動をテストごとに制御できるようにする。"""

    class DummyAgent:
        """テスト専用の簡易エージェント。"""

        last_init: ClassVar[tuple[LLMProvider, HuggingFaceModel | str | None, str | None] | None] = None
        invoke_result: ClassVar[object] = SimpleNamespace(response="ok")
        invocations: ClassVar[list[tuple[OneLinerState, str]]] = []

        def __init__(
            self,
            provider: LLMProvider,
            *,
            model_name: HuggingFaceModel | str | None = None,
            device: str | None = None,
        ) -> None:
            type(self).last_init = (provider, model_name, device)

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
    device: OpenVINODevice = OpenVINODevice.CPU,
) -> None:
    """SettingsApplicationService を差し替えて、テスト用設定を返す。"""

    class AgentsStub:
        def __init__(
            self,
            provider_value: LLMProvider,
            model_value: HuggingFaceModel | str | None,
            runtime_device: OpenVINODevice,
        ) -> None:
            self.provider = provider_value
            self._model_value = model_value
            self.runtime = SimpleNamespace(device=runtime_device)

        def get_model_name(self, _: str) -> HuggingFaceModel | str | None:
            return self._model_value

    class UserStub:
        def __init__(self, name: str) -> None:
            self.user_name = name

    class SettingsAppStub:
        def __init__(self) -> None:
            self._agents = AgentsStub(provider, model, device)
            self._user = UserStub(user_name)

        def get_agents_settings(self) -> AgentsStub:
            return self._agents

        def get_user_settings(self) -> UserStub:
            return self._user

    monkeypatch.setattr(one_liner_module.SettingsApplicationService, "get_instance", lambda: SettingsAppStub())


def _sample_state(user_name: str = "Tester") -> OneLinerState:
    return {
        "today_task_count": 0,
        "completed_task_count": 0,
        "overdue_task_count": 0,
        "progress_summary": "",
        "user_name": user_name,
    }


def test_openvino_string_model_raises_service_error(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """OPENVINO で文字列モデルを指定した場合に例外が送出されることを検証する。"""

    # 設定側で OPENVINO を指定し、文字列モデルを与えたときに例外となることを検証
    _stub_config(monkeypatch, provider=LLMProvider.OPENVINO, model=HuggingFaceModel.QWEN_3_8B_INT4)

    with pytest.raises(OneLinerServiceError) as exc:
        OneLinerApplicationService(model_name="invalid-model")

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

    assert stub_agent.last_init == (LLMProvider.OPENVINO, HuggingFaceModel.QWEN_3_8B_INT4, OpenVINODevice.CPU.value)
    assert service._get_default_message() == "今日も一日、お疲れさまです。"


def test_generate_one_liner_returns_agent_response(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """Google プロバイダの場合にエージェント応答がそのまま返されることを検証する。"""

    _stub_config(monkeypatch, provider=LLMProvider.GOOGLE, model="models/gemini-pro", user_name="Alice")
    stub_agent.invoke_result = SimpleNamespace(response="こんにちは")

    service = OneLinerApplicationService()

    # OneLinerState は TypedDict なので dict リテラルで生成する
    query: OneLinerState = {
        "today_task_count": 1,
        "completed_task_count": 0,
        "overdue_task_count": 0,
        "progress_summary": "",
        "user_name": "Bob",
    }
    result = service.generate_one_liner(query)

    assert result == "こんにちは"
    assert stub_agent.last_init == (LLMProvider.GOOGLE, "models/gemini-pro", OpenVINODevice.CPU.value)
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


def test_agent_receives_gpu_device_setting(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """設定で GPU を選択した場合にエージェントへ渡されることを検証する。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.FAKE,
        model=None,
        device=OpenVINODevice.GPU,
    )

    OneLinerApplicationService()

    assert stub_agent.last_init == (LLMProvider.FAKE, None, OpenVINODevice.GPU.value)


def test_generate_one_liner_returns_cached_value_within_ttl(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """TTL 内の連続呼び出しではキャッシュを返し、エージェント再実行を避ける。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.FAKE,
        model=None,
    )

    call_count = {"value": 0}

    def fake_build_context(self: OneLinerApplicationService) -> OneLinerState:
        call_count["value"] += 1
        return _sample_state()

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_build_context_auto", fake_build_context)

    current_time = datetime(2024, 1, 1, tzinfo=UTC)

    def fake_now(self: OneLinerApplicationService) -> datetime:
        return current_time

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_now", fake_now)

    stub_agent.invoke_result = SimpleNamespace(response="first")
    service = OneLinerApplicationService()

    first = service.generate_one_liner()
    assert first == "first"
    assert call_count["value"] == 1
    assert len(stub_agent.invocations) == 1

    current_time = current_time + timedelta(minutes=30)
    stub_agent.invoke_result = SimpleNamespace(response="second")

    second = service.generate_one_liner()
    assert second == "first"
    assert call_count["value"] == 1
    assert len(stub_agent.invocations) == 1


def test_generate_one_liner_refreshes_after_ttl(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """TTL 経過後は新たにエージェントを実行する。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.FAKE,
        model=None,
    )

    call_count = {"value": 0}

    def fake_build_context(self: OneLinerApplicationService) -> OneLinerState:
        call_count["value"] += 1
        return _sample_state(user_name=f"User{call_count['value']}")

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_build_context_auto", fake_build_context)

    base_time = datetime(2024, 1, 1, tzinfo=UTC)
    current_time = base_time

    def fake_now(self: OneLinerApplicationService) -> datetime:
        return current_time

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_now", fake_now)

    stub_agent.invoke_result = SimpleNamespace(response="first")
    service = OneLinerApplicationService()
    first = service.generate_one_liner()

    assert first == "first"
    assert call_count["value"] == 1
    assert len(stub_agent.invocations) == 1

    current_time = base_time + timedelta(minutes=61)
    stub_agent.invoke_result = SimpleNamespace(response="second")

    second = service.generate_one_liner()

    expected_refresh_invocations = 2
    assert second == "second"
    assert call_count["value"] == expected_refresh_invocations
    assert len(stub_agent.invocations) == expected_refresh_invocations


def test_explicit_query_bypasses_cache(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """明示的なクエリはキャッシュの有無に関係なくエージェントを呼び出す。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.FAKE,
        model=None,
    )

    def fake_build_context(self: OneLinerApplicationService) -> OneLinerState:
        return _sample_state()

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_build_context_auto", fake_build_context)

    service = OneLinerApplicationService()
    stub_agent.invoke_result = SimpleNamespace(response="cached")
    cached = service.generate_one_liner()
    assert cached == "cached"
    assert len(stub_agent.invocations) == 1

    def fail_build(self: OneLinerApplicationService) -> OneLinerState:  # pragma: no cover
        message = "explicit query should bypass context build"
        raise AssertionError(message)

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_build_context_auto", fail_build)

    stub_agent.invoke_result = SimpleNamespace(response="fresh")
    query: OneLinerState = _sample_state(user_name="Bob")
    result = service.generate_one_liner(query)

    expected_calls_after_explicit = 2
    assert result == "fresh"
    assert len(stub_agent.invocations) == expected_calls_after_explicit


def test_default_message_is_not_cached(monkeypatch: pytest.MonkeyPatch, stub_agent: type) -> None:
    """デフォルトメッセージへフォールバックした場合はキャッシュされず直後も再試行される。"""

    _stub_config(
        monkeypatch,
        provider=LLMProvider.FAKE,
        model=None,
    )

    call_count = {"value": 0}

    def fake_build_context(self: OneLinerApplicationService) -> OneLinerState:
        call_count["value"] += 1
        return _sample_state()

    monkeypatch.setattr(one_liner_module.OneLinerApplicationService, "_build_context_auto", fake_build_context)

    service = OneLinerApplicationService()
    stub_agent.invoke_result = SimpleNamespace(response="")

    first = service.generate_one_liner()
    assert first == service._get_default_message()
    assert call_count["value"] == 1
    assert len(stub_agent.invocations) == 1

    stub_agent.invoke_result = SimpleNamespace(response="recovered")

    second = service.generate_one_liner()

    expected_call_count_after_recovery = 2
    assert second == "recovered"
    assert call_count["value"] == expected_call_count_after_recovery
    assert len(stub_agent.invocations) == expected_call_count_after_recovery
