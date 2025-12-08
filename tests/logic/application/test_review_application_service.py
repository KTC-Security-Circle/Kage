"""WeeklyReviewApplicationService のテスト。"""

from __future__ import annotations

import uuid
from typing import Self
from unittest.mock import MagicMock

from logic.application.review_application_service import WeeklyReviewApplicationService
from logic.services.weekly_review_action_service import WeeklyReviewActionService
from logic.services.weekly_review_service import WeeklyReviewInsightsService
from models import WeeklyReviewActionResult, WeeklyReviewInsightsQuery, WeeklyReviewTaskDecision


class _DummyUnitOfWork:
    def __init__(
        self,
        review_service: WeeklyReviewInsightsService,
        action_service: WeeklyReviewActionService | None = None,
    ) -> None:
        self._review_service = review_service
        self._action_service = action_service
        self.service_factory = MagicMock()

        def _get_service(service_type: type[object]) -> object:
            if service_type is WeeklyReviewInsightsService:
                return self._review_service
            if service_type is WeeklyReviewActionService:
                if self._action_service is None:
                    msg = "Action service not provided"
                    raise AssertionError(msg)
                return self._action_service
            msg = f"Unknown service: {service_type}"
            raise AssertionError(msg)

        self.service_factory.get_service.side_effect = _get_service

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    def commit(self) -> None:
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


def test_apply_actions_delegates_to_action_service() -> None:
    review_service = MagicMock(spec=WeeklyReviewInsightsService)
    action_service = MagicMock(spec=WeeklyReviewActionService)
    fake_result = WeeklyReviewActionResult(message="done")
    action_service.apply_actions.return_value = fake_result

    def factory() -> _DummyUnitOfWork:
        return _DummyUnitOfWork(review_service, action_service)

    app_service = WeeklyReviewApplicationService(unit_of_work_factory=factory)  # type: ignore[arg-type]

    decision = WeeklyReviewTaskDecision(task_id=uuid.uuid4(), action="split")
    result = app_service.apply_actions([decision])

    assert result is fake_result
    action_service.apply_actions.assert_called_once_with([decision])
