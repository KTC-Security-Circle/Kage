"""TagsController のユニットテスト。"""

from __future__ import annotations

import uuid
from unittest.mock import Mock, create_autospec

import pytest

from models import MemoRead, MemoStatus, TagRead, TaskRead, TaskStatus
from views.tags.controller import (
    MemoApplicationPort,
    TagApplicationPort,
    TagsController,
    TaskApplicationPort,
)
from views.tags.state import TagsViewState


@pytest.fixture
def state() -> TagsViewState:
    """空の TagsViewState を返す。"""

    return TagsViewState()


@pytest.fixture
def tag_service() -> TagApplicationPort:
    """TagApplicationPort のモック。"""

    return create_autospec(TagApplicationPort, instance=True)


@pytest.fixture
def memo_service() -> MemoApplicationPort:
    """MemoApplicationPort のモック。"""

    return create_autospec(MemoApplicationPort, instance=True)


@pytest.fixture
def task_service() -> TaskApplicationPort:
    """TaskApplicationPort のモック。"""

    return create_autospec(TaskApplicationPort, instance=True)


@pytest.fixture
def controller(
    state: TagsViewState,
    tag_service: TagApplicationPort,
    memo_service: MemoApplicationPort,
    task_service: TaskApplicationPort,
) -> TagsController:
    """テスト対象の TagsController。"""

    return TagsController(state, tag_service, memo_service, task_service)


def _sample_tag(name: str) -> TagRead:
    return TagRead(id=uuid.uuid4(), name=name, description=f"desc-{name}", color="#123456")


def _sample_memo() -> MemoRead:
    return MemoRead(id=uuid.uuid4(), title="memo", content="memo-content", status=MemoStatus.INBOX)


def _sample_task() -> TaskRead:
    return TaskRead(id=uuid.uuid4(), title="task", description="task-desc", status=TaskStatus.TODO)


def test_load_initial_tags_fetches_from_service(
    controller: TagsController,
    state: TagsViewState,
    tag_service: TagApplicationPort,
) -> None:
    """初期ロードでサービスからデータを取得する。"""

    sample = _sample_tag("緊急")
    tag_service.get_all_tags.return_value = [sample]

    controller.load_initial_tags()

    assert state.initial_loaded is True
    assert len(state.items) == 1
    assert state.items[0]["name"] == "緊急"
    tag_service.get_all_tags.assert_called_once()


def test_create_tag_updates_state_and_avoids_fetch(controller: TagsController, state: TagsViewState, tag_service: TagApplicationPort, memo_service: MemoApplicationPort, task_service: TaskApplicationPort) -> None:
    """作成直後は関連データキャッシュを使用する。"""

    created = _sample_tag("開発")
    tag_service.create.return_value = created

    controller.create_tag(created.name, created.color, created.description)

    assert len(state.items) == 1
    assert state.selected_id == str(created.id)

    controller.get_tag_counts(str(created.id))
    memo_service.list_by_tag.assert_not_called()
    task_service.list_by_tag.assert_not_called()


def test_related_items_are_cached_per_tag(
    controller: TagsController,
    state: TagsViewState,
    memo_service: MemoApplicationPort,
    task_service: TaskApplicationPort,
) -> None:
    """関連メモ・タスクは初回のみ取得される。"""

    tag = _sample_tag("デザイン")
    tag_id = str(tag.id)
    state.items = [
        {
            "id": tag_id,
            "name": tag.name,
            "color": tag.color or "",
            "description": tag.description or "",
            "created_at": "-",
            "updated_at": "-",
        }
    ]
    memo_service.list_by_tag.return_value = [_sample_memo()]
    task_service.list_by_tag.return_value = [_sample_task()]

    first = controller.get_related_memos(tag_id)
    second = controller.get_related_memos(tag_id)

    assert len(first) == 1
    assert second == first
    memo_service.list_by_tag.assert_called_once()


def test_update_tag_resets_usage_cache(
    controller: TagsController,
    state: TagsViewState,
    tag_service: TagApplicationPort,
    memo_service: MemoApplicationPort,
) -> None:
    """更新後はキャッシュが無効化される。"""

    tag = _sample_tag("タグA")
    tag_id = str(tag.id)
    state.items = [
        {
            "id": tag_id,
            "name": tag.name,
            "color": tag.color or "",
            "description": tag.description or "",
            "created_at": "-",
            "updated_at": "-",
        }
    ]
    memo_service.list_by_tag.return_value = [_sample_memo()]

    controller.get_tag_counts(tag_id)
    assert memo_service.list_by_tag.call_count == 1

    memo_service.list_by_tag.reset_mock()
    updated = TagRead(id=tag.id, name="タグB", description="", color="#654321")
    tag_service.update.return_value = updated

    controller.update_tag(tag_id, name="タグB")

    controller.get_tag_counts(tag_id)
    memo_service.list_by_tag.assert_called_once()
