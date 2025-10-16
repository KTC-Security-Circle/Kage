import uuid

import pytest

from errors import NotFoundError
from logic.repositories.task import TaskRepository
from logic.services.task_service import TaskService
from models import Task, TaskStatus
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
