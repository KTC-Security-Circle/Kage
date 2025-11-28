"""週次レビュー機能に関する設定ユーティリティ。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from settings.manager import get_config_manager
from settings.models import (
    REVIEW_DEFAULT_RANGE_DAYS,
    REVIEW_DEFAULT_ZOMBIE_THRESHOLD_DAYS,
    ReviewSettings,
)

DEFAULT_REVIEW_RANGE_DAYS = REVIEW_DEFAULT_RANGE_DAYS
DEFAULT_ZOMBIE_THRESHOLD_DAYS = REVIEW_DEFAULT_ZOMBIE_THRESHOLD_DAYS


@dataclass(frozen=True)
class ReviewPeriodDefaults:
    """レビュー期間に関する既定値を表すデータクラス。"""

    range_days: int = DEFAULT_REVIEW_RANGE_DAYS
    zombie_threshold_days: int = DEFAULT_ZOMBIE_THRESHOLD_DAYS

    @property
    def range_delta(self) -> timedelta:
        """日数設定を timedelta に変換する。"""
        return timedelta(days=self.range_days)


def get_review_settings() -> ReviewSettings:
    """AppSettings から最新のレビュー設定を取得する。"""
    return get_config_manager().settings.review
