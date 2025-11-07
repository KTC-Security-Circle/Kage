from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pytest

from logic.application.memo_application_service import (
    MemoApplicationError,
    MemoApplicationService,
)

if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from agents.base import AgentError  # noqa: F401
    from agents.task_agents.memo_to_task.state import MemoToTaskState  # noqa: F401
    from models import MemoRead


class _DummyAgent:
    """テスト用ダミーエージェント。返却値を切り替えて例外系を検証する。"""

    next_return: ClassVar[object | None] = None

    def invoke(self, state: object, thread_id: str) -> object | None:  # state は型非依存
        return type(self).next_return


@pytest.fixture(autouse=True)
def reset_dummy_agent() -> None:
    _DummyAgent.next_return = None


def _service_with_dummy_agent(monkeypatch: pytest.MonkeyPatch) -> MemoApplicationService:
    svc = MemoApplicationService()
    monkeypatch.setattr(svc, "_get_memo_to_task_agent", lambda: _DummyAgent())
    # 既存タグ収集は DB 依存のためスタブ
    monkeypatch.setattr(svc, "_collect_existing_tag_names", lambda: ["a", "b"])  # 既存タグ収集をスタブ
    return svc


def _memo(content: str = "test") -> MemoRead:
    # MemoRead は DB 取得モデルだが、テストでは最小フィールドを埋める
    import uuid

    from models import AiSuggestionStatus, MemoRead, MemoStatus

    return MemoRead(
        id=uuid.uuid4(),
        title="t",
        content=content,
        status=MemoStatus.INBOX,
        ai_suggestion_status=AiSuggestionStatus.NOT_REQUESTED,
        ai_analysis_log=None,
        created_at=None,
        updated_at=None,
        processed_at=None,
    )


def test_clarify_memo_raises_on_agent_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from agents.base import AgentError

    svc = _service_with_dummy_agent(monkeypatch)
    _DummyAgent.next_return = AgentError("unit-error")

    with pytest.raises(MemoApplicationError):
        svc.clarify_memo(_memo("valid"))


def test_clarify_memo_raises_on_none(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = _service_with_dummy_agent(monkeypatch)
    _DummyAgent.next_return = None

    with pytest.raises(MemoApplicationError):
        svc.clarify_memo(_memo("valid"))


def test_clarify_memo_raises_on_invalid_type(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = _service_with_dummy_agent(monkeypatch)
    _DummyAgent.next_return = object()  # 想定外型

    with pytest.raises(MemoApplicationError):
        svc.clarify_memo(_memo("valid"))
