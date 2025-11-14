"""Tests for the memos view controller."""

from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from errors import NotFoundError
from models import MemoRead, MemoStatus
from views.memos.controller import MemoApplicationPort, MemosController
from views.memos.state import MemosViewState


def _build_memo(*, memo_id: uuid.UUID | None = None, status: MemoStatus = MemoStatus.INBOX, title: str = "Test") -> MemoRead:
    """Create a MemoRead instance for tests."""

    memo_id = memo_id or uuid.uuid4()
    return MemoRead(id=memo_id, title=title, content="content", status=status)


def test_load_initial_memos_sort_and_reset_state() -> None:
    """Initial load should sort memos and reset search state."""

    memo_inbox = _build_memo(status=MemoStatus.INBOX, title="Inbox")
    memo_active = _build_memo(status=MemoStatus.ACTIVE, title="Active")

    memo_app = Mock(spec=MemoApplicationPort)
    memo_app.get_all_memos.return_value = [memo_active, memo_inbox]

    state = MemosViewState()
    controller = MemosController(memo_app=memo_app, state=state)

    controller.load_initial_memos()

    assert state.all_memos == [memo_inbox, memo_active]
    assert state.search_query == ""
    assert state.search_results is None


def test_create_memo_updates_state_and_refreshes_search() -> None:
    """Creating a memo should persist it and refresh the search cache."""

    memo_app = Mock(spec=MemoApplicationPort)
    state = MemosViewState()
    state.set_current_tab(MemoStatus.ACTIVE)
    controller = MemosController(memo_app=memo_app, state=state)

    state.set_search_result("idea", [])

    created = _build_memo(status=MemoStatus.ACTIVE, title="New Idea")
    memo_app.create.return_value = created
    memo_app.search.return_value = [created]

    controller.create_memo("New Idea", "body", status=MemoStatus.ACTIVE)

    memo_app.create.assert_called_once_with(title="New Idea", content="body", status=MemoStatus.ACTIVE)
    memo_app.search.assert_called_once_with(
        "idea",
        with_details=False,
        status=state.current_tab,
    )
    assert state.selected_memo_id == created.id
    assert created in state.all_memos
    assert state.search_results == [created]


def test_update_memo_applies_changes_without_search_when_not_needed() -> None:
    """Updating a memo should replace state but avoid needless searches."""

    memo_id = uuid.uuid4()
    existing = _build_memo(memo_id=memo_id, status=MemoStatus.INBOX, title="Old")

    memo_app = Mock(spec=MemoApplicationPort)
    updated = _build_memo(memo_id=memo_id, status=MemoStatus.ACTIVE, title="Updated")
    memo_app.update.return_value = updated

    state = MemosViewState()
    state.set_all_memos([existing])
    controller = MemosController(memo_app=memo_app, state=state)

    controller.update_memo(memo_id, title="Updated", status=MemoStatus.ACTIVE)

    memo_app.update.assert_called_once()
    _, update_payload = memo_app.update.call_args[0]
    assert update_payload.title == "Updated"
    assert update_payload.status == MemoStatus.ACTIVE
    assert state.all_memos[0].title == "Updated"
    assert not memo_app.search.called


def test_delete_memo_updates_state_and_search_results() -> None:
    """Deleting a memo should prune state, selection, and search results."""

    memo_id = uuid.uuid4()
    other_id = uuid.uuid4()
    to_delete = _build_memo(memo_id=memo_id, status=MemoStatus.INBOX, title="Delete")
    other = _build_memo(memo_id=other_id, status=MemoStatus.ACTIVE, title="Keep")

    memo_app = Mock(spec=MemoApplicationPort)
    memo_app.delete.return_value = True
    memo_app.search.return_value = [other]

    state = MemosViewState()
    state.set_all_memos([to_delete, other])
    state.set_selected_memo(memo_id)
    state.set_search_result("query", [to_delete, other])

    controller = MemosController(memo_app=memo_app, state=state)
    controller.delete_memo(memo_id)

    memo_app.delete.assert_called_once_with(memo_id)
    assert all(m.id != memo_id for m in state.all_memos)
    assert state.selected_memo_id is None
    assert state.search_results == [other]
    memo_app.search.assert_called_once_with(
        "query",
        with_details=False,
        status=state.current_tab,
    )


def test_delete_memo_raises_when_not_found() -> None:
    """Delete should raise NotFoundError when repository returns False."""

    memo_app = Mock(spec=MemoApplicationPort)
    memo_app.delete.return_value = False

    state = MemosViewState()
    controller = MemosController(memo_app=memo_app, state=state)

    with pytest.raises(NotFoundError):
        controller.delete_memo(uuid.uuid4())
