"""WeeklyReviewApplicationService のテスト。"""

from __future__ import annotations

from typing import Self
from unittest.mock import MagicMock

from logic.application.review_application_service import WeeklyReviewApplicationService
from logic.services.weekly_review_service import WeeklyReviewInsightsService
from models import WeeklyReviewInsightsQuery


class _DummyUnitOfWork:
    def __init__(self, review_service: WeeklyReviewInsightsService) -> None:
        self.service_factory = MagicMock()
        self.service_factory.get_service.return_value = review_service

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None


def test_generate_insights_delegates_to_service() -> None:
    review_service = MagicMock(spec=WeeklyReviewInsightsService)
    fake_response = MagicMock()
    review_service.generate_insights.return_value = fake_response

    def factory() -> _DummyUnitOfWork:
        return _DummyUnitOfWork(review_service)

    app_service = WeeklyReviewApplicationService(unit_of_work_factory=factory)  # type: ignore[arg-type]

    query = WeeklyReviewInsightsQuery()
    result = app_service.generate_insights(query)

    assert result is fake_response
    review_service.generate_insights.assert_called_once_with(query)


def test_fetch_insights_builds_query() -> None:
    review_service = MagicMock(spec=WeeklyReviewInsightsService)
    review_service.generate_insights.return_value = MagicMock()

    def factory() -> _DummyUnitOfWork:
        return _DummyUnitOfWork(review_service)

    app_service = WeeklyReviewApplicationService(unit_of_work_factory=factory)  # type: ignore[arg-type]

    app_service.fetch_insights(project_ids=None)

    called_query = review_service.generate_insights.call_args.args[0]
    assert isinstance(called_query, WeeklyReviewInsightsQuery)
