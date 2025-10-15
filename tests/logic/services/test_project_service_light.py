from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.project_service import ProjectService, ProjectServiceError
from models import Project, ProjectCreate, ProjectRead


class DummyProjectRepo:
    def __init__(self) -> None:
        self.storage = {}

    def create(self, data: ProjectCreate) -> Project:
        p = Project(id=uuid.uuid4(), title=data.title)
        self.storage[p.id] = p
        return p

    def get_by_id(self, project_id: uuid.UUID, *, with_details: bool = False) -> Project:
        p = self.storage.get(project_id)
        if p is None:
            msg = "not found"
            raise NotFoundError(msg)
        return p

    def get_all(self) -> list[Project]:
        if not self.storage:
            msg = "no projects"
            raise NotFoundError(msg)
        return list(self.storage.values())

    def delete(self, project_id: uuid.UUID) -> bool:
        return bool(self.storage.pop(project_id, None))

    # ProjectService.delete expects these methods to exist on the repo.
    def remove_all_tasks(self, project_id: uuid.UUID) -> None:
        # In a real repo this would dissociate tasks; for tests it's a no-op.
        return None

    def remove_task(self, project_id: uuid.UUID, task_id: str) -> Project:
        # For remove_task flow, simply return the project (no mutation needed for tests)
        proj = self.storage.get(project_id)
        if proj is None:
            msg = "not found"
            raise NotFoundError(msg)
        return proj


class RepoRaiser(DummyProjectRepo):
    def create(self, data: ProjectCreate) -> Project:
        msg = "db down"
        raise RepositoryError(msg)


@pytest.fixture
def svc() -> ProjectService:
    return ProjectService(project_repo=DummyProjectRepo())  # type: ignore[arg-type]


def test_create_happy_path(svc: ProjectService) -> None:
    data = ProjectCreate(title="p")
    res = svc.create(data)
    assert isinstance(res, ProjectRead)
    assert res.title == "p"


def test_get_by_id_not_found(svc: ProjectService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_by_id(uuid.uuid4())


def test_get_all_not_found(svc: ProjectService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_all()


def test_delete_happy_path() -> None:
    repo = DummyProjectRepo()
    service = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    created = repo.create(ProjectCreate(title="x"))
    assert created.id is not None
    assert service.delete(created.id) is True


def test_create_repo_error_wrapped() -> None:
    service = ProjectService(project_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(ProjectServiceError) as exc:
        service.create(ProjectCreate(title="x"))

    err = exc.value
    assert isinstance(err.__cause__, RepositoryError)
