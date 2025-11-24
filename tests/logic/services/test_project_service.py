from __future__ import annotations

import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.services.project_service import ProjectService, ProjectServiceError
from models import Project, ProjectCreate, ProjectRead, ProjectStatus, ProjectUpdate, Task, TaskStatus


class DummyProjectRepo:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Project] = {}

    def create(self, data: ProjectCreate) -> Project:
        p = Project(id=uuid.uuid4(), title=data.title, status=ProjectStatus.ACTIVE)
        pid = p.id
        assert pid is not None
        self.storage[pid] = p
        p.tasks = []
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

    def update(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
        project = self.get_by_id(project_id)
        project.title = data.title or project.title
        if data.status is not None:
            project.status = data.status
        return project

    def remove_all_tasks(self, project_id: uuid.UUID) -> None:
        project = self.get_by_id(project_id)
        project.tasks = []

    def add_task(self, project_id: uuid.UUID, task_id: uuid.UUID) -> Project:
        project = self.get_by_id(project_id)
        if not hasattr(project, "tasks") or project.tasks is None:
            project.tasks = []
        if any(getattr(task, "id", None) == task_id for task in project.tasks):
            return project
        project.tasks.append(Task(id=task_id, title="linked", status=TaskStatus.TODO))
        return project

    def remove_task(self, project_id: uuid.UUID, task_id: uuid.UUID) -> Project:
        project = self.get_by_id(project_id)
        project.tasks = [task for task in project.tasks if getattr(task, "id", None) != task_id]
        return project

    def list_by_status(self, status: ProjectStatus) -> list[Project]:
        items = [p for p in self.storage.values() if p.status == status]
        if not items:
            msg = "not found"
            raise NotFoundError(msg)
        return items

    # 新規追加: タイトル検索
    def search_by_title(self, title_query: str) -> list[Project]:  # type: ignore[override]
        items = [p for p in self.storage.values() if title_query.lower() in p.title.lower()]
        if not items:
            msg = "not found"
            raise NotFoundError(msg)
        return items


class RepoRaiser(DummyProjectRepo):
    def create(self, data: ProjectCreate) -> Project:  # type: ignore[override]
        msg = "db down"
        raise RepositoryError(msg)


class SpyProjectRepo(DummyProjectRepo):
    def __init__(self) -> None:
        super().__init__()
        self.remove_all_calls: list[uuid.UUID] = []
        self.delete_calls: list[uuid.UUID] = []

    def remove_all_tasks(self, project_id: uuid.UUID) -> None:  # type: ignore[override]
        self.remove_all_calls.append(project_id)
        super().remove_all_tasks(project_id)

    def delete(self, project_id: uuid.UUID) -> bool:  # type: ignore[override]
        self.delete_calls.append(project_id)
        return super().delete(project_id)


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


def test_delete_force_false_removes_tasks() -> None:
    repo = SpyProjectRepo()
    service = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    project = repo.create(ProjectCreate(title="p"))
    assert project.id is not None

    assert service.delete(project.id, force=False) is True
    assert repo.remove_all_calls == [project.id]


def test_delete_force_true_skips_remove_all() -> None:
    repo = SpyProjectRepo()
    project = repo.create(ProjectCreate(title="p"))
    assert project.id is not None

    service = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    repo.storage[project.id] = project
    assert service.delete(project.id, force=True) is True
    assert repo.remove_all_calls == []


def test_create_repo_error_wrapped() -> None:
    service = ProjectService(project_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(ProjectServiceError) as exc:
        service.create(ProjectCreate(title="x"))

    err = exc.value
    assert isinstance(err.__cause__, RepositoryError)


def test_list_by_status_not_found_transparent(svc: ProjectService) -> None:
    with pytest.raises(NotFoundError):
        # Use a valid status with no items to trigger NotFoundError
        svc.list_by_status(ProjectStatus.COMPLETED)


def test_remove_task_not_found_when_not_attached(svc: ProjectService) -> None:
    proj = svc.create(ProjectCreate(title="p"))
    assert isinstance(proj, ProjectRead)
    assert proj.id is not None

    with pytest.raises(NotFoundError):
        svc.remove_task(proj.id, uuid.uuid4())


def test_update_returns_read_model(svc: ProjectService) -> None:
    created = svc.create(ProjectCreate(title="old"))
    assert isinstance(created, ProjectRead)
    assert created.id is not None

    updated = svc.update(created.id, ProjectUpdate(title="new"))
    assert isinstance(updated, ProjectRead)
    assert updated.title == "new"


def test_remove_task_success() -> None:
    repo = DummyProjectRepo()
    service = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    project = repo.create(ProjectCreate(title="p"))
    assert project.id is not None
    task_uuid = uuid.uuid4()
    task = Task(id=task_uuid, title="t", project_id=project.id)
    project.tasks = [task]

    result = service.remove_task(project.id, task_uuid)
    assert isinstance(result, ProjectRead)


def test_add_task_delegates_to_repository() -> None:
    repo = DummyProjectRepo()
    svc = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    project = repo.create(ProjectCreate(title="p"))
    assert project.id is not None
    task_uuid = uuid.uuid4()

    result = svc.add_task(project.id, task_uuid)
    assert isinstance(result, ProjectRead)


def test_search_projects() -> None:
    repo = DummyProjectRepo()
    svc = ProjectService(project_repo=repo)  # type: ignore[arg-type]
    a = repo.create(ProjectCreate(title="Alpha"))
    b = repo.create(ProjectCreate(title="Beta"))
    assert a.id is not None
    assert b.id is not None

    res = svc.search_projects("alp")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].title == "Alpha"
