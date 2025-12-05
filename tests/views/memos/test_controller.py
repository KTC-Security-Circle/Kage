"""MemosController の挙動に関するテスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

from models import AiSuggestionStatus, MemoRead, MemoStatus, MemoUpdate
from views.memos.controller import MemoApplicationPort, MemosController

if TYPE_CHECKING:
    from views.memos.state import MemosViewState


def _build_memo_read() -> MemoRead:
    """テスト用の単純な MemoRead インスタンスを生成する。"""
    return MemoRead(
        id=uuid4(),
        title="title",
        content="content",
        status=MemoStatus.INBOX,
        ai_suggestion_status=AiSuggestionStatus.NOT_REQUESTED,
    )


class _DummyMemoApp:
    """MemoApplicationPort の update だけを提供する簡易スタブ。"""

    def __init__(self, memo_to_return: MemoRead) -> None:
        self.memo_to_return = memo_to_return
        self.last_called_id: UUID | None = None
        self.last_update_data: MemoUpdate | None = None

    def update(self, memo_id: UUID, update_data: MemoUpdate) -> MemoRead:  # type: ignore[override]
        self.last_called_id = memo_id
        self.last_update_data = update_data
        return self.memo_to_return


class _DummyState:
    """controller が参照する最小限の State を提供する。"""

    def __init__(self, memos: list[MemoRead] | None = None) -> None:
        self.all_memos = memos or []
        self.search_query = ""
        self.last_upserted: MemoRead | None = None
        self.reconciled = False

    def upsert_memo(self, memo: MemoRead) -> None:
        self.last_upserted = memo

    def set_all_memos(self, memos: list[MemoRead]) -> None:
        self.all_memos = memos

    def set_selected_memo(self, memo_id: UUID | None) -> None:  # pragma: no cover - unused but kept for safety
        self.selected_memo_id = memo_id

    def set_search_result(self, query: str, memos: list[MemoRead]) -> None:  # pragma: no cover - unused
        self.search_results = (query, memos)

    def reconcile(self) -> None:
        self.reconciled = True


def test_update_memo_skips_ai_status_when_not_provided() -> None:
    memo = _build_memo_read()
    memo_app = _DummyMemoApp(memo)
    state = _DummyState([memo])
    controller = MemosController(
        memo_app=cast("MemoApplicationPort", memo_app),
        state=cast("MemosViewState", state),
    )

    controller.update_memo(
        memo.id,
        title="updated title",
        content="updated content",
        status=MemoStatus.INBOX,
    )

    assert memo_app.last_update_data is not None
    update_dict = memo_app.last_update_data.model_dump(exclude_unset=True)
    assert "ai_suggestion_status" not in update_dict
    assert state.last_upserted == memo
    assert memo_app.last_called_id == memo.id


def test_update_memo_updates_ai_status_when_specified() -> None:
    memo = _build_memo_read()
    memo_app = _DummyMemoApp(memo)
    state = _DummyState([memo])
    controller = MemosController(
        memo_app=cast("MemoApplicationPort", memo_app),
        state=cast("MemosViewState", state),
    )

    controller.update_memo(
        memo.id,
        title="updated title",
        content="updated content",
        status=MemoStatus.ACTIVE,
        ai_status=AiSuggestionStatus.REVIEWED,
    )

    assert memo_app.last_update_data is not None
    update_dict = memo_app.last_update_data.model_dump(exclude_unset=True)
    assert update_dict["ai_suggestion_status"] == AiSuggestionStatus.REVIEWED
