from __future__ import annotations

from typing import Self

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.base import (
    MyBaseError,
    ServiceBase,
    ServiceError,
    handle_service_errors,
)


class DummyService(ServiceBase):
    """例外ラップ検証用のダミーサービス。

    RepositoryError は ServiceError に変換され、
    NotFoundError はそのまま伝播することを確認する。
    """

    @classmethod
    def build_service(cls) -> Self:  # type: ignore[override]
        return cls()

    @handle_service_errors(service_name="DummyService", operation="operate")
    def ok(self) -> str:
        return "ok"

    @handle_service_errors(service_name="DummyService", operation="operate")
    def raise_not_found(self) -> None:
        msg = "not found"
        raise NotFoundError(msg)

    @handle_service_errors(service_name="DummyService", operation="operate")
    def raise_repo_error(self) -> None:
        msg = "db is down"
        raise RepositoryError(msg)

    @handle_service_errors(service_name="DummyService", operation="operate")
    def raise_unknown(self) -> None:
        msg = "boom"
        raise RuntimeError(msg)


def test_repository_error_is_wrapped_as_service_error() -> None:
    svc = DummyService.build_service()

    with pytest.raises(ServiceError) as exc:
        svc.raise_repo_error()

    # メッセージ・operation が設定され、原因がチェインされていること
    err = exc.value
    assert isinstance(err, ServiceError)
    assert getattr(err, "operation", None) == "operate"
    # __cause__ に RepositoryError が入っている
    assert isinstance(err.__cause__, RepositoryError)


def test_not_found_error_is_passed_through() -> None:
    svc = DummyService.build_service()

    with pytest.raises(NotFoundError):
        svc.raise_not_found()


def test_unexpected_exception_is_wrapped() -> None:
    svc = DummyService.build_service()

    with pytest.raises(ServiceError) as exc:
        svc.raise_unknown()

    err = exc.value
    assert getattr(err, "operation", None) == "operate"
    assert isinstance(err.__cause__, RuntimeError)


class CustomServiceError(MyBaseError):
    """エラー型を差し替え可能であることの検証用。"""

    def __str__(self) -> str:  # pragma: no cover - 表示は検証対象外
        return f"{self.operation}: {self.message}"


def test_error_cls_override() -> None:
    class OverrideService(DummyService):
        @handle_service_errors("OverrideService", "operate", error_cls=CustomServiceError)
        def do(self) -> None:
            msg = "fail"
            raise RepositoryError(msg)

    svc = OverrideService.build_service()

    with pytest.raises(CustomServiceError) as exc:
        svc.do()

    err = exc.value
    assert isinstance(err, CustomServiceError)
    assert getattr(err, "operation", None) == "operate"
