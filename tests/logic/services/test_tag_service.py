from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.tag_service import TagService, TagServiceError
from models import Tag, TagCreate, TagRead


class DummyTagRepo:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Tag] = {}

    def create(self, data: TagCreate) -> Tag:
        t = Tag(id=uuid.uuid4(), name=data.name)
        tag_id = t.id
        assert tag_id is not None
        self.storage[tag_id] = t
        return t

    def get_by_id(self, tag_id: uuid.UUID) -> Tag:
        t = self.storage.get(tag_id)
        if t is None:
            msg = "not found"
            raise NotFoundError(msg)
        return t

    def get_by_name(self, name: str) -> Tag:
        for t in self.storage.values():
            if t.name == name:
                return t
        msg = "not found"
        raise NotFoundError(msg)

    def get_all(self) -> list[Tag]:
        if not self.storage:
            msg = "no tags"
            raise NotFoundError(msg)
        return list(self.storage.values())

    def delete(self, tag_id: uuid.UUID) -> bool:
        return bool(self.storage.pop(tag_id, None))

    def remove_all_memos(self, tag_id: uuid.UUID) -> None:  # pragma: no cover - no side effects needed
        return None

    def remove_all_tasks(self, tag_id: uuid.UUID) -> None:  # pragma: no cover - no side effects needed
        return None

    def search_by_name(self, query: str) -> list[Tag]:
        return [t for t in self.storage.values() if query.lower() in t.name.lower()]


class RepoRaiser(DummyTagRepo):
    def create(self, data: TagCreate) -> Tag:  # type: ignore[override]
        msg = "db down"
        raise RepositoryError(msg)


@pytest.fixture
def svc() -> TagService:
    return TagService(tag_repo=DummyTagRepo())  # type: ignore[arg-type]


def test_create_happy_path(svc: TagService) -> None:
    data = TagCreate(name="tag1")
    res = svc.create(data)
    assert isinstance(res, TagRead)
    assert res.name == "tag1"


def test_get_by_id_not_found(svc: TagService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_by_id(uuid.uuid4())


def test_get_all_not_found(svc: TagService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_all()


def test_delete_happy_path() -> None:
    repo = DummyTagRepo()
    service = TagService(tag_repo=repo)  # type: ignore[arg-type]
    created = repo.create(TagCreate(name="t"))
    assert created.id is not None
    assert service.delete(created.id) is True


def test_create_repo_error_wrapped() -> None:
    service = TagService(tag_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(TagServiceError) as exc:
        service.create(TagCreate(name="x"))

    err = exc.value
    assert isinstance(err.__cause__, RepositoryError)


def test_get_by_name_not_found(svc: TagService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_by_name("missing")


def test_search_by_name_returns_list(svc: TagService) -> None:
    svc.create(TagCreate(name="alpha"))
    svc.create(TagCreate(name="beta"))
    svc.create(TagCreate(name="Alpine"))

    res = svc.search_by_name("al")
    assert isinstance(res, list)
    names = {t.name for t in res}
    assert names == {"alpha", "Alpine"}


def test_get_or_create_tag_when_exists(svc: TagService) -> None:
    created = svc.create(TagCreate(name="keep"))
    got = svc.get_or_create_tag("keep")
    assert isinstance(got, TagRead)
    assert got.id == created.id


def test_get_or_create_tag_when_missing_creates(svc: TagService) -> None:
    got = svc.get_or_create_tag("new-tag")
    assert isinstance(got, TagRead)
    assert got.name == "new-tag"
