from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.base import MyBaseError
from logic.services.memo_service import MemoService, MemoServiceError
from models import Memo, MemoCreate, MemoRead


class DummyMemoRepo:
    def __init__(self) -> None:
        self.storage = {}

    def create(self, create_data: MemoCreate) -> Memo:
        m = Memo(id=uuid.uuid4(), title=create_data.title, content=create_data.content)
        self.storage[m.id] = m
        return m

    def get_by_id(self, memo_id: uuid.UUID, *, with_details: bool = False) -> Memo:
        m = self.storage.get(memo_id)
        if m is None:
            msg = "memo not found"
            raise NotFoundError(msg)
        return m

    def get_all(self, *, with_details: bool = False) -> list[Memo]:
        if not self.storage:
            msg = "no memos"
            raise NotFoundError(msg)
        return list(self.storage.values())

    def delete(self, memo_id: uuid.UUID) -> bool:
        return bool(self.storage.pop(memo_id, None))


class RepoRaiser(DummyMemoRepo):
    def create(self, create_data: MemoCreate) -> Memo:
        msg = "db down"
        raise RepositoryError(msg)


@pytest.fixture
def memo_service() -> MemoService:
    return MemoService(memo_repo=DummyMemoRepo())  # type: ignore[arg-type]


def test_create_happy_path(memo_service: MemoService) -> None:
    data = MemoCreate(title="t", content="c")
    res = memo_service.create(data)
    # MemoService returns a MemoRead model instance
    assert isinstance(res, MemoRead)
    assert res.title == "t"


def test_get_by_id_not_found(memo_service: MemoService) -> None:
    with pytest.raises(NotFoundError):
        memo_service.get_by_id(uuid.uuid4())


def test_get_all_not_found(memo_service: MemoService) -> None:
    with pytest.raises(NotFoundError):
        memo_service.get_all()


def test_delete_happy_path() -> None:
    repo = DummyMemoRepo()
    svc = MemoService(memo_repo=repo)  # type: ignore[arg-type]
    created = repo.create(MemoCreate(title="a", content="b"))
    assert created.id is not None
    assert svc.delete(created.id) is True


def test_create_repo_error_wrapped() -> None:
    svc = MemoService(memo_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(MemoServiceError) as exc:
        svc.create(MemoCreate(title="x", content="y"))

    err = exc.value
    assert isinstance(err, MyBaseError)
    assert err.operation == "作成"
    assert isinstance(err.__cause__, RepositoryError)
