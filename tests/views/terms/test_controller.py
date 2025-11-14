"""Tests for TermsController."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from models import TermRead, TermStatus
from views.terms.controller import TermApplicationPort, TermFormData, TermsController
from views.terms.state import TermsViewState


def _make_term(
    key: str,
    title: str,
    *,
    status: TermStatus = TermStatus.APPROVED,
    updated_at: datetime | None = None,
) -> TermRead:
    """Helper to build TermRead objects for tests."""
    return TermRead(
        id=uuid4(),
        key=key,
        title=title,
        description="description",
        status=status,
        source_url=None,
        created_at=datetime.now(),
        updated_at=updated_at or datetime.now(),
    )


class FakeTermService(TermApplicationPort):
    """In-memory TermApplicationPort implementation for controller tests."""

    def __init__(self) -> None:
        now = datetime.now()
        self._terms: list[TermRead] = [
            _make_term("alpha", "Alpha", updated_at=now - timedelta(days=1)),
            _make_term("beta", "Beta", status=TermStatus.DRAFT, updated_at=now),
        ]

    def list_terms(self, status: TermStatus | None = None) -> list[TermRead]:
        if status:
            return [term for term in self._terms if term.status == status]
        return list(self._terms)

    def search_terms(self, query: str) -> list[TermRead]:
        keyword = query.lower()
        return [term for term in self._terms if keyword in term.title.lower()]

    def create_term(self, form_data: TermFormData) -> TermRead:
        status_value = form_data.get("status", TermStatus.DRAFT)
        status = status_value if isinstance(status_value, TermStatus) else TermStatus(status_value)
        term = _make_term(
            form_data.get("key", "new"),
            form_data.get("title", "New Term"),
            status=status,
        )
        self._terms.append(term)
        return term

    def update_term(self, term_id: UUID, form_data: TermFormData) -> TermRead:
        for term in self._terms:
            if term.id == term_id:
                term.title = form_data.get("title", term.title) or term.title
                status_value = form_data.get("status")
                if status_value:
                    term.status = status_value if isinstance(status_value, TermStatus) else TermStatus(status_value)
                term.updated_at = datetime.now()
                return term
        msg = f"Term not found: {term_id}"
        raise ValueError(msg)

    def delete_term(self, term_id: UUID) -> bool:
        for index, term in enumerate(self._terms):
            if term.id == term_id:
                self._terms.pop(index)
                return True
        return False


def _run(coro):
    """Utility to execute controller coroutines."""
    return asyncio.run(coro)


def test_load_initial_terms_populates_state() -> None:
    """Controller should populate state from service."""
    state = TermsViewState()
    controller = TermsController(state=state, service=FakeTermService())

    _run(controller.load_initial_terms())

    assert len(state.all_terms) == 2
    assert state.search_results is None
    assert state.all_terms[0].updated_at >= state.all_terms[1].updated_at


def test_update_search_filters_terms() -> None:
    """Controller should update search results based on query."""
    state = TermsViewState()
    controller = TermsController(state=state, service=FakeTermService())
    _run(controller.load_initial_terms())

    _run(controller.update_search("alp"))

    assert state.search_results is not None
    assert len(state.search_results) == 1
    assert state.search_results[0].key == "alpha"


def test_create_term_updates_state() -> None:
    """Creating a term should add it to state."""
    state = TermsViewState()
    controller = TermsController(state=state, service=FakeTermService())
    _run(controller.load_initial_terms())

    form_data: TermFormData = {
        "key": "gamma",
        "title": "Gamma",
        "description": "desc",
        "status": TermStatus.APPROVED,
        "source_url": None,
        "synonyms": [],
    }
    created = _run(controller.create_term(form_data))

    assert any(term.id == created.id for term in state.all_terms)
    assert created.title == "Gamma"


def test_delete_term_updates_state_and_results() -> None:
    """Deleting a term should remove it from both all_terms and search_results."""
    state = TermsViewState()
    controller = TermsController(state=state, service=FakeTermService())
    _run(controller.load_initial_terms())
    target_id = state.all_terms[0].id

    _run(controller.update_search(state.all_terms[0].title))
    assert state.search_results is not None

    _run(controller.delete_term(target_id))

    assert all(term.id != target_id for term in state.all_terms)
    assert state.search_results is not None
    assert all(term.id != target_id for term in state.search_results)
