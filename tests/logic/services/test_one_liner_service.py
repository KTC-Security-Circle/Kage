"""OneLinerApplicationService 移行後テスト

シンプルな pytest 関数スタイルで記述し、インデント問題を回避。
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agents.agent_conf import LLMProvider
from logic.application.one_liner_application_service import (
    OneLinerApplicationService,
    OneLinerContext,
    OneLinerServiceError,
)
from logic.services.base import MyBaseError


def test_one_liner_basic_generation() -> None:
    svc = OneLinerApplicationService()
    text = svc.generate_one_liner()
    assert isinstance(text, str)
    assert text


def test_one_liner_generation_with_context() -> None:
    svc = OneLinerApplicationService()
    ctx = OneLinerContext(today_task_count=5, overdue_task_count=1, completed_task_count=2)
    text = svc.generate_one_liner(ctx)
    assert isinstance(text, str)
    assert text


def test_one_liner_exception_fallback() -> None:
    svc = OneLinerApplicationService()
    with patch.object(svc, "_generate_with_agent", side_effect=Exception("boom")):
        text = svc.generate_one_liner()
        assert text == "今日も一日、お疲れさまです。"


def test_one_liner_provider_override() -> None:
    from settings.manager import get_config_manager

    mgr = get_config_manager()
    with mgr.edit() as editable:
        editable.agents.provider = LLMProvider.FAKE
    svc = OneLinerApplicationService()
    text = svc.generate_one_liner()
    assert isinstance(text, str)
    assert text


def test_one_liner_log_error_and_raise() -> None:
    svc = OneLinerApplicationService()
    with pytest.raises(OneLinerServiceError):
        svc._log_error_and_raise("err")


def test_one_liner_context_defaults() -> None:
    ctx = OneLinerContext()
    assert ctx.today_task_count == 0
    assert ctx.overdue_task_count == 0
    assert ctx.completed_task_count == 0


def test_one_liner_context_mutability() -> None:
    ctx = OneLinerContext(today_task_count=2)
    new_value = 3
    ctx.today_task_count = new_value
    assert ctx.today_task_count == new_value


def test_one_liner_service_error_message() -> None:
    err = OneLinerServiceError("x")
    assert "一言コメント生成エラー" in str(err)


def test_one_liner_service_error_inheritance() -> None:
    err = OneLinerServiceError("test")
    assert isinstance(err, MyBaseError)
    assert isinstance(err, Exception)
