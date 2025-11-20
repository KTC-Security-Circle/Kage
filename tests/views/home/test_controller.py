"""HomeController の振る舞い(空データ時のログレベル確認など)のユニットテスト。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Never

if TYPE_CHECKING:
    import pytest

from views.home.controller import HomeController
from views.home.query import InMemoryHomeQuery
from views.home.state import HomeViewState
from views.home.view import HomeView
from views.shared.base_view import BaseViewProps


def test_load_initial_data_with_empty_does_not_raise() -> None:
    """InMemoryHomeQuery (空データ) でロードしても例外が発生しないこと。

    既定値ではHomeState が空のままであり、例外は発生しないことを確認する。
    """

    state = HomeViewState()
    query = InMemoryHomeQuery()
    ctrl = HomeController(state=state, query=query)

    # 実行しても例外が発生しない
    ctrl.load_initial_data()

    assert state.daily_review == {}
    assert state.inbox_memos == []
    assert state.stats == {}


def test_load_initial_data_logs_info_when_empty(caplog: pytest.LogCaptureFixture) -> None:
    """空のデータでロードすると INFO レベルで通知されることを確認する。"""

    # pytest fixture caplog を利用

    state = HomeViewState()
    query = InMemoryHomeQuery()
    ctrl = HomeController(state=state, query=query)

    caplog.set_level(logging.INFO)
    ctrl.load_initial_data()

    assert any("Home initial data empty" in r.message for r in caplog.records)


def test_homeview_uses_inmemory_query_when_services_missing() -> None:
    """サービス不在時に HomeView は例外を出さず InMemoryHomeQuery へフォールバックすることを確認する。"""

    class FakeApps:
        def get_service(self, _: object) -> Never:
            msg = "missing"
            raise RuntimeError(msg)

    props = BaseViewProps(page=object(), apps=FakeApps())  # type: ignore[arg-type]

    view = HomeView(props)

    assert isinstance(view.controller.query, InMemoryHomeQuery)
