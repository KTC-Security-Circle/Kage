from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.base import MyBaseError
from logic.services.memo_service import MemoService, MemoServiceError
from models import Memo, MemoCreate, MemoRead, MemoStatus


class DummyMemoRepo:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Memo] = {}

    def create(self, create_data: MemoCreate) -> Memo:
        m = Memo(id=uuid.uuid4(), title=create_data.title, content=create_data.content)
        assert m.id is not None
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

    def list_by_status(self, status: MemoStatus, *, with_details: bool = False) -> list[Memo]:
        """指定ステータスのメモ一覧を返すダミー実装。

        Dummy では単純フィルタのみ。該当がなければ NotFoundError を送出する。
        """
        matched = [m for m in self.storage.values() if m.status == status]
        if not matched:
            msg = "no memos with status"
            raise NotFoundError(msg)
        return matched

    def add_tag(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo:
        return self.get_by_id(memo_id)

    def add_task(self, memo_id: uuid.UUID, task_id: uuid.UUID) -> Memo:
        return self.get_by_id(memo_id)

    def search_by_title(self, query: str, *, with_details: bool = False) -> list[Memo]:
        return [memo for memo in self.storage.values() if query in memo.title]

    def search_by_content(self, query: str, *, with_details: bool = False) -> list[Memo]:
        return [memo for memo in self.storage.values() if query in memo.content]


class RepoRaiser(DummyMemoRepo):
    def create(self, create_data: MemoCreate) -> Memo:
        msg = "db down"
        raise RepositoryError(msg)


class RepoUnexpected(DummyMemoRepo):
    def create(self, create_data: MemoCreate) -> Memo:
        msg = "boom"
        raise RuntimeError(msg)


class RepoDeleteFailure(DummyMemoRepo):
    def delete(self, memo_id: uuid.UUID) -> bool:  # type: ignore[override]
        super().get_by_id(memo_id)
        return False


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


def test_delete_failure_returns_false() -> None:
    repo = RepoDeleteFailure()
    svc = MemoService(memo_repo=repo)  # type: ignore[arg-type]
    created = repo.create(MemoCreate(title="a", content="b"))
    assert created.id is not None

    assert svc.delete(created.id) is False


def test_create_repo_error_wrapped() -> None:
    svc = MemoService(memo_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(MemoServiceError) as exc:
        svc.create(MemoCreate(title="x", content="y"))

    err = exc.value
    assert isinstance(err, MyBaseError)
    assert err.operation == "作成"
    assert isinstance(err.__cause__, RepositoryError)


def test_create_unexpected_exception_is_wrapped() -> None:
    svc = MemoService(memo_repo=RepoUnexpected())  # type: ignore[arg-type]

    with pytest.raises(MemoServiceError) as exc:
        svc.create(MemoCreate(title="x", content="y"))

    err = exc.value
    assert isinstance(err.__cause__, RuntimeError)


def test_get_all_with_details_happy(memo_service: MemoService) -> None:
    # 準備
    created = memo_service.create(MemoCreate(title="a", content="b"))
    assert isinstance(created, MemoRead)
    # 実行: with_details=True 経路でも取得できる
    res = memo_service.get_all(with_details=True)
    assert isinstance(res, list)
    assert any(m.id == created.id for m in res)


def test_list_by_status_with_details(memo_service: MemoService) -> None:
    memo = memo_service.create(MemoCreate(title="x", content="y"))
    assert isinstance(memo, MemoRead)

    repo = memo_service.memo_repo
    if isinstance(repo, DummyMemoRepo):
        stored = repo.storage[memo.id]
        stored.status = MemoStatus.INBOX

    res = memo_service.list_by_status(MemoStatus.INBOX, with_details=True)
    assert any(item.id == memo.id for item in res)


def test_list_by_status_not_found(memo_service: MemoService) -> None:
    from models import MemoStatus

    with pytest.raises(NotFoundError):
        memo_service.list_by_status(MemoStatus.ARCHIVE)


def test_search_memos_deduplicates_and_returns(memo_service: MemoService) -> None:
    first = memo_service.create(MemoCreate(title="alpha", content="shared content"))
    second = memo_service.create(MemoCreate(title="beta", content="alpha shared content"))

    assert isinstance(first, MemoRead)
    assert isinstance(second, MemoRead)

    res = memo_service.search_memos("alpha", with_details=True)
    ids = {item.id for item in res}
    assert ids == {first.id, second.id}


def test_add_tag_returns_read_model(memo_service: MemoService) -> None:
    memo = memo_service.create(MemoCreate(title="x", content="y"))
    assert isinstance(memo, MemoRead)

    result = memo_service.add_tag(memo.id, uuid.uuid4())
    assert isinstance(result, MemoRead)


def test_add_task_returns_read_model(memo_service: MemoService) -> None:
    memo = memo_service.create(MemoCreate(title="x", content="y"))
    assert isinstance(memo, MemoRead)

    result = memo_service.add_task(memo.id, uuid.uuid4())
    assert isinstance(result, MemoRead)
