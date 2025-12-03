"""WeeklyReviewInsightsService を公開する Application Service。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError
from logic.application.base import BaseApplicationService
from logic.services.weekly_review_service import WeeklyReviewInsightsService
from logic.unit_of_work import SqlModelUnitOfWork
from models import WeeklyReviewInsights, WeeklyReviewInsightsQuery

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime
    from uuid import UUID


class WeeklyReviewApplicationError(ApplicationError):
    """週次レビュー Application Service で発生するエラー。"""


class WeeklyReviewApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """UI から週次レビュー集計を呼び出すためのサービス。"""

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(
        cls,
        unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> WeeklyReviewApplicationService:
        return super().get_instance(unit_of_work_factory, *args, **kwargs)  # type: ignore[return-value]

    def generate_insights(self, query: WeeklyReviewInsightsQuery) -> WeeklyReviewInsights:
        """週次レビューインサイトを生成する。"""
        try:
            with self._unit_of_work_factory() as uow:
                review_service = uow.service_factory.get_service(WeeklyReviewInsightsService)
                result = review_service.generate_insights(query)
                logger.info("WeeklyReviewApplicationService: インサイトを生成しました")
                return result
        except Exception as exc:  # pragma: no cover - エラー経路
            raise WeeklyReviewApplicationError(str(exc)) from exc

    def fetch_insights(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        zombie_threshold_days: int | None = None,
        project_ids: list[UUID] | None = None,
        user_id: UUID | None = None,
    ) -> WeeklyReviewInsights:
        """プリミティブなパラメータからインサイトを取得する。"""
        query = WeeklyReviewInsightsQuery(
            start=start,
            end=end,
            zombie_threshold_days=zombie_threshold_days,
            project_ids=project_ids or [],
            user_id=user_id,
        )
        return self.generate_insights(query)
