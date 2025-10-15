from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.tag_service import TagService, TagServiceError
from models import Tag, TagCreate, TagRead


class DummyTagRepo:
    def __init__(self) -> None:
        self.storage = {}

    def create(self, data: TagCreate) -> Tag:
        t = Tag(id=uuid.uuid4(), name=data.name)
        self.storage[t.id] = t
        return t

    def get_by_id(self, tag_id: uuid.UUID) -> Tag:
        t = self.storage.get(tag_id)
        if t is None:
            msg = "not found"
            raise NotFoundError(msg)
        return t

    def get_all(self) -> list[Tag]:
        if not self.storage:
            msg = "no tags"
            raise NotFoundError(msg)
        return list(self.storage.values())

    def delete(self, tag_id: uuid.UUID) -> bool:
        return bool(self.storage.pop(tag_id, None))

    def remove_all_memos(self, tag_id: uuid.UUID) -> None:
        return None

    def remove_all_tasks(self, tag_id: uuid.UUID) -> None:
        return None


class RepoRaiser(DummyTagRepo):
    def create(self, data: TagCreate) -> Tag:
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
