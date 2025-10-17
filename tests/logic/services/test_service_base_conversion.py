from __future__ import annotations

import uuid

import pytest

from logic.services.base import (
    ModelConversionError,
    ServiceBase,
    ServiceError,
    convert_read_model,
)
from models import Memo, MemoRead


def test_convert_read_model_single_returns_read_model() -> None:
    @convert_read_model(MemoRead)
    def factory() -> Memo:
        return Memo(id=uuid.uuid4(), title="t", content="c")

    result = factory()
    assert isinstance(result, MemoRead)
    assert result.title == "t"


def test_convert_read_model_list_returns_read_models() -> None:
    @convert_read_model(MemoRead, is_list=True)
    def factory() -> list[Memo]:
        return [
            Memo(id=uuid.uuid4(), title="a", content="b"),
            Memo(id=uuid.uuid4(), title="c", content="d"),
        ]

    result = factory()
    assert isinstance(result, list)
    assert all(isinstance(item, MemoRead) for item in result)


def test_convert_read_model_invalid_single_raises() -> None:
    @convert_read_model(MemoRead)
    def broken() -> Memo:
        return "invalid"  # type: ignore[return-value]

    with pytest.raises(ModelConversionError):
        broken()


def test_convert_read_model_invalid_list_raises() -> None:
    @convert_read_model(MemoRead, is_list=True)
    def broken() -> list[Memo]:
        return ["invalid"]  # type: ignore[list-item]

    with pytest.raises(ModelConversionError):
        broken()


class DummyService(ServiceBase):
    @classmethod
    def build_service(cls, *args, **kwargs) -> DummyService:  # noqa: ANN002, ANN003
        return cls()


def test_service_error_str_contains_operation() -> None:
    err = ServiceError("failure", operation="テスト")
    assert "テスト" in str(err)


def test_get_service_name_returns_class_name() -> None:
    assert DummyService.get_service_name() == "DummyService"
