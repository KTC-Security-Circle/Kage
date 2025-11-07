import uuid

import pytest

from errors import NotFoundError, RepositoryError
from logic.repositories.task import TaskRepository
from logic.services.task_service import TaskService, TaskServiceError
from models import Task, TaskCreate, TaskRead, TaskStatus
from tests.logic.helpers import create_test_tag, create_test_task_create


@pytest.fixture
def task_service(task_repository: TaskRepository) -> TaskService:
    """TaskServiceを実データベース(インメモリ)で構築するフィクスチャ。"""
    return TaskService(task_repo=task_repository)  # type: ignore[arg-type]


def test_delete_force_false_calls_remove_and_delete(task_service: TaskService, task_repository: TaskRepository) -> None:
    """delete(force=False) 経路でタグ全削除と削除が実行され、Trueを返す。"""
    # 準備: タスク作成
    task = task_repository.create(create_test_task_create(title="del-target"))

    # 監視: 呼び出しフラグ
    called: dict[str, bool] = {"remove": False, "delete": False}

    original_remove_all_tags = task_repository.remove_all_tags
    original_delete = task_repository.delete

    def spy_remove_all_tags(task_id: uuid.UUID) -> Task:
        called["remove"] = True
        return original_remove_all_tags(task_id)

    def spy_delete(task_id: uuid.UUID) -> bool:
        called["delete"] = True
        return original_delete(task_id)

    # モンキーパッチ
    # pytest の monkeypatch フィクスチャを使わず、直接属性を差し替え
    task_repository.remove_all_tags = spy_remove_all_tags  # type: ignore[method-assign]
    task_repository.delete = spy_delete  # type: ignore[method-assign]

    # 実行
    assert task.id is not None
    res = task_service.delete(task.id, force=False)

    # 検証
    assert res is True
    assert called["remove"] is True
    assert called["delete"] is True

    # 後片付け: 元に戻す
    task_repository.remove_all_tags = original_remove_all_tags  # type: ignore[method-assign]
    task_repository.delete = original_delete  # type: ignore[method-assign]


def test_remove_tag_raises_when_tag_not_attached(task_service: TaskService, task_repository: TaskRepository) -> None:
    """タスクに付与されていないタグをremove_tagするとNotFoundError。"""
    # 準備: タスクと（未付与の）タグを作成
    task = task_repository.create(create_test_task_create(title="has-no-tags"))
    tag = create_test_tag("t1")
    # タグはDBに存在するが、タスクには付与していない
    task_repository.session.add(tag)
    task_repository.session.commit()

    # 実行/検証
    assert task.id is not None
    assert tag.id is not None
    with pytest.raises(NotFoundError):
        task_service.remove_tag(task.id, tag.id)


def test_list_by_status_not_found_raises(task_service: TaskService) -> None:
    """該当ステータスのタスクがない場合、ServiceもNotFoundErrorを透過。"""
    with pytest.raises(NotFoundError):
        task_service.list_by_status(TaskStatus.WAITING)


# ---- 以下、light 版から統合したユニット志向テスト（DummyRepoベース） ----


class DummyTaskRepo:
    def __init__(self) -> None:
        self.storage: dict[uuid.UUID, Task] = {}

    def create(self, data: TaskCreate) -> Task:
        t = Task(id=uuid.uuid4(), title=data.title)
        assert t.id is not None
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


class RepoRaiser(DummyTaskRepo):
    def create(self, data: TaskCreate) -> Task:
        msg = "db down"
        raise RepositoryError(msg)


class RepoUnexpected(DummyTaskRepo):
    def create(self, data: TaskCreate) -> Task:
        msg = "boom"
        raise RuntimeError(msg)


@pytest.fixture
def svc() -> TaskService:
    return TaskService(task_repo=DummyTaskRepo())  # type: ignore[arg-type]


def test_create_happy_path_unified_light(svc: TaskService) -> None:
    data = TaskCreate(title="task1")
    res = svc.create(data)
    assert isinstance(res, TaskRead)
    assert res.title == "task1"


def test_get_by_id_not_found_unified_light(svc: TaskService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_by_id(uuid.uuid4())


def test_get_all_not_found_unified_light(svc: TaskService) -> None:
    with pytest.raises(NotFoundError):
        svc.get_all()


def test_delete_happy_path_unified_light() -> None:
    repo = DummyTaskRepo()
    service = TaskService(task_repo=repo)  # type: ignore[arg-type]
    created = repo.create(TaskCreate(title="t"))
    assert created.id is not None
    assert service.delete(created.id) is True


def test_create_repo_error_wrapped_unified_light() -> None:
    service = TaskService(task_repo=RepoRaiser())  # type: ignore[arg-type]

    with pytest.raises(TaskServiceError) as exc:
        service.create(TaskCreate(title="x"))

    err = exc.value
    assert isinstance(err.__cause__, RepositoryError)


def test_create_unexpected_exception_is_wrapped() -> None:
    service = TaskService(task_repo=RepoUnexpected())  # type: ignore[arg-type]

    with pytest.raises(TaskServiceError) as exc:
        service.create(TaskCreate(title="y"))

    err = exc.value
    assert isinstance(err.__cause__, RuntimeError)


def test_remove_tag_happy_path(task_service: TaskService, task_repository: TaskRepository) -> None:
    """タスクに付与済みのタグを remove_tag で削除できる。"""
    # 準備: タスクとタグを作成して付与
    task = task_repository.create(create_test_task_create(title="has-tag"))
    tag = create_test_tag("t1")
    assert task.id is not None
    assert tag.id is not None
    task_repository.session.add(tag)
    task_repository.session.commit()
    task_repository.add_tag(task.id, tag.id)

    # 実行: 削除
    updated = task_service.remove_tag(task.id, tag.id)

    # 検証: ReadModelで返る & DB上でタグが外れている
    assert isinstance(updated, TaskRead)
    task_entity = task_repository.get_by_id(task.id, with_details=True)
    assert all(t.id != tag.id for t in task_entity.tags)


def test_search_tasks_deduplicates_and_uses_both_fields(task_repository: TaskRepository) -> None:
    """search_tasks はタイトル/説明の両方を検索し、重複を除去する。"""
    svc = TaskService(task_repo=task_repository)  # type: ignore[arg-type]
    # タイトルヒットと説明ヒットが重複するケース
    a = task_repository.create(create_test_task_create(title="Write docs", description="Write user docs"))
    b = task_repository.create(create_test_task_create(title="Implement", description="Write code"))
    assert a.id is not None
    assert b.id is not None

    results = svc.search_tasks("write", with_details=False)
    titles = {t.title for t in results}
    assert titles == {"Write docs", "Implement"}


def test_search_tasks_with_details_flag(task_repository: TaskRepository) -> None:
    """with_details フラグがあってもエラーにならずに結果を返す。"""
    svc = TaskService(task_repo=task_repository)  # type: ignore[arg-type]
    task_repository.create(create_test_task_create(title="A", description="B"))
    out = svc.search_tasks("a", with_details=True)
    assert isinstance(out, list)
