from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.task_service import TaskService, TaskServiceError
from models import Task, TaskCreate, TaskRead


class DummyTaskRepo:
    def __init__(self) -> None:
        self.storage = {}

    def create(self, data: TaskCreate) -> Task:
        t = Task(id=uuid.uuid4(), title=data.title)
        self.storage[t.id] = t
        return t

    def get_by_id(self, task_id: uuid.UUID, *, with_details: bool = False) -> Task:
        t = self.storage.get(task_id)
        if t is None:
            msg = "not found"
            raise NotFoundError(msg)
        return t

    def get_all(self) -> list[Task]:
        if not self.storage:
            msg = "no tasks"
            raise NotFoundError(msg)
        return list(self.storage.values())

    def delete(self, task_id: uuid.UUID) -> bool:
        return bool(self.storage.pop(task_id, None))

    def remove_all_tags(self, task_id: uuid.UUID) -> None:
        return None

    def remove_all_tasks(self, task_id: uuid.UUID) -> None:
        return None


class RepoRaiser(DummyTaskRepo):
    def create(self, data: TaskCreate) -> Task:
        msg = "db down"
        raise RepositoryError(msg)


@pytest.fixture
def svc() -> TaskService:
    return TaskService(task_repo=DummyTaskRepo())  # type: ignore[arg-type]


def test_create_happy_path(svc: TaskService) -> None:
    data = TaskCreate(title="task1")
    res = svc.create(data)
    assert isinstance(res, TaskRead)
    assert res.title == "task1"


def test_get_by_id_not_found(svc: TaskService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_by_id(uuid.uuid4())


def test_get_all_not_found(svc: TaskService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_all()


def test_delete_happy_path() -> None:
    repo = DummyTaskRepo()
    service = TaskService(task_repo=repo)  # type: ignore[arg-type]
    created = repo.create(TaskCreate(title="t"))
    assert created.id is not None
    assert service.delete(created.id) is True


def test_create_repo_error_wrapped() -> None:
    service = TaskService(task_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(TaskServiceError) as exc:
        service.create(TaskCreate(title="x"))

    err = exc.value
    assert isinstance(err.__cause__, RepositoryError)
