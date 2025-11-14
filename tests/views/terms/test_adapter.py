"""Tests for TerminologyApplicationPortAdapter."""

from __future__ import annotations

from uuid import uuid4

from models import TermRead, TermStatus
from views.terms.controller import TermFormData, TerminologyApplicationPortAdapter

try:
    from unittest.mock import MagicMock
except ImportError:  # pragma: no cover - fallback for minimal environments
    from mock import MagicMock  # type: ignore[no-redef]


def _make_term(key: str, title: str) -> TermRead:
    return TermRead(
        id=uuid4(),
        key=key,
        title=title,
        description=None,
        status=TermStatus.APPROVED,
        source_url=None,
    )


def test_adapter_list_terms_delegates_to_service() -> None:
    """list_terms should call appropriate service method."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)

    service.get_all.return_value = [_make_term("a", "A")]
    assert adapter.list_terms() == service.get_all.return_value
    service.get_all.assert_called_once_with()

    service.reset_mock()
    filtered = [_make_term("b", "B")]
    service.search.return_value = filtered
    assert adapter.list_terms(status=TermStatus.APPROVED) == filtered
    service.search.assert_called_once_with(query=None, status=TermStatus.APPROVED)


def test_adapter_list_terms_handles_not_found() -> None:
    """list_terms should gracefully handle NotFoundError and return empty list."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)
    from errors import NotFoundError

    service.get_all.side_effect = NotFoundError("no terms")

    assert adapter.list_terms() == []
    service.get_all.assert_called_once_with()


def test_adapter_search_terms_uses_service_search() -> None:
    """search_terms should delegate to service.search."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)
    expected = [_make_term("k", "Kappa")]
    service.search.return_value = expected

    assert adapter.search_terms("ka") == expected
    service.search.assert_called_once_with(query="ka")


def test_adapter_create_term_normalizes_payload() -> None:
    """create_term should strip text and coerce statuses."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)
    created = _make_term("key", "Title")
    service.create.return_value = created

    form_data: TermFormData = {
        "key": " key ",
        "title": " Title ",
        "description": " desc ",
        "status": "approved",
        "source_url": " https://example.com ",
        "synonyms": [],
    }
    result = adapter.create_term(form_data)

    assert result is created
    service.create.assert_called_once_with(
        key="key",
        title="Title",
        description="desc",
        status=TermStatus.APPROVED,
        source_url="https://example.com",
    )


def test_adapter_update_term_builds_update_model() -> None:
    """update_term should pass TermUpdate with normalized values."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)
    updated = _make_term("key", "Title")
    service.update.return_value = updated
    term_id = uuid4()

    form_data: TermFormData = {
        "key": " new_key ",
        "title": " new title ",
        "description": None,
        "status": TermStatus.DEPRECATED,
        "source_url": " ",
        "synonyms": [],
    }
    result = adapter.update_term(term_id, form_data)

    assert result is updated
    service.update.assert_called_once()
    _, update_model = service.update.call_args[0]
    assert update_model.key == "new_key"
    assert update_model.title == "new title"
    assert update_model.description is None
    assert update_model.status == TermStatus.DEPRECATED
    assert update_model.source_url is None


def test_adapter_delete_term_returns_service_result() -> None:
    """delete_term should return service.delete value."""
    service = MagicMock()
    adapter = TerminologyApplicationPortAdapter(service)
    service.delete.return_value = True
    term_id = uuid4()

    assert adapter.delete_term(term_id) is True
    service.delete.assert_called_once_with(term_id)
