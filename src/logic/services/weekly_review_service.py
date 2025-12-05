"""週次レビューインサイトを生成するサービス。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, TypedDict, TypeVar

from loguru import logger

from agents.task_agents.review_copilot import ReviewCopilotAgent
from errors import NotFoundError
from logic.repositories import MemoRepository, ProjectRepository, RepositoryFactory, TaskRepository
from logic.services.base import MyBaseError, ServiceBase, handle_service_errors
from models import (
    CompletedTaskDigest,
    MemoAuditDigest,
    MemoRead,
    ProjectRead,
    ProjectStatus,
    ReviewPeriod,
    TaskRead,
    TaskStatus,
    WeeklyReviewInsights,
    WeeklyReviewInsightsQuery,
    WeeklyReviewMetadata,
    ZombieTaskDigest,
)
from settings.manager import get_config_manager
from settings.models import AgentDetailLevel
from settings.review import get_review_settings

DEFAULT_STATUS_FILTER: tuple[TaskStatus, ...] = (
    TaskStatus.TODO,
    TaskStatus.PROGRESS,
    TaskStatus.WAITING,
)

_T = TypeVar("_T")

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from uuid import UUID

    from settings.models import ReviewSettings


class _PromptKwargs(TypedDict, total=False):
    prompt_custom_instructions: str
    prompt_detail_level: AgentDetailLevel


@dataclass(slots=True)
class _ReviewSourceData:
    completed: list[CompletedTaskDigest]
    stale: list[ZombieTaskDigest]
    unprocessed_memos: list[MemoAuditDigest]


class WeeklyReviewInsightsError(MyBaseError):
    """週次レビュー生成で発生するエラー。"""


class WeeklyReviewInsightsService(ServiceBase):
    """週次レビューの集計とLLM整形を担うサービス。"""

    def __init__(
        self,
        task_repo: TaskRepository,
        memo_repo: MemoRepository,
        project_repo: ProjectRepository,
        review_agent: ReviewCopilotAgent,
        review_settings: ReviewSettings | None = None,
    ) -> None:
        self.task_repo = task_repo
        self.memo_repo = memo_repo
        self.project_repo = project_repo
        self.review_agent = review_agent
        self.review_settings = review_settings or get_review_settings()

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> WeeklyReviewInsightsService:
        task_repo = repo_factory.create(TaskRepository)
        memo_repo = repo_factory.create(MemoRepository)
        project_repo = repo_factory.create(ProjectRepository)
        cfg = get_config_manager().settings.agents
        provider = cfg.provider
        runtime_cfg = getattr(cfg, "runtime", None)
        device = None
        if runtime_cfg and getattr(runtime_cfg, "device", None) is not None:
            device = str(runtime_cfg.device.value)
        model_name = cfg.get_model_name("review")
        prompt_cfg = getattr(cfg, "review_prompt", None)
        prompt_kwargs: _PromptKwargs = {}
        if prompt_cfg is not None:
            prompt_kwargs["prompt_custom_instructions"] = str(getattr(prompt_cfg, "custom_instructions", "") or "")
            level = getattr(prompt_cfg, "detail_level", None)
            if isinstance(level, AgentDetailLevel):
                prompt_kwargs["prompt_detail_level"] = level
        agent = ReviewCopilotAgent(
            provider=provider,
            model_name=model_name,
            device=device,
            **prompt_kwargs,
        )
        return cls(task_repo, memo_repo, project_repo, agent)

    @handle_service_errors("週次レビュー", "集計", WeeklyReviewInsightsError)
    def generate_insights(self, query: WeeklyReviewInsightsQuery | None = None) -> WeeklyReviewInsights:
        """レビューインサイトを生成する。"""
        safe_query = query or WeeklyReviewInsightsQuery()
        period_start, period_end = self._resolve_period(safe_query)
        threshold_days = safe_query.zombie_threshold_days or self.review_settings.default_zombie_threshold_days
        stale_boundary = period_end - timedelta(days=threshold_days)
        project_filters = safe_query.project_ids

        source_data = self._collect_source_data(
            period_start=period_start,
            period_end=period_end,
            stale_boundary=stale_boundary,
            project_filters=project_filters,
        )

        highlights = self.review_agent.build_highlights(source_data.completed)
        zombie_payload = self.review_agent.build_zombie_suggestions(
            source_data.stale,
            zombie_threshold_days=threshold_days,
        )
        memo_payload = self.review_agent.build_memo_audits(source_data.unprocessed_memos)

        metadata = WeeklyReviewMetadata(
            period=ReviewPeriod(start=period_start, end=period_end),
            generated_at=datetime.now(),
            zombie_threshold_days=threshold_days,
            project_filters=project_filters,
        )

        return WeeklyReviewInsights(
            metadata=metadata,
            highlights=highlights,
            zombie_tasks=zombie_payload,
            memo_audits=memo_payload,
        )

    def _collect_source_data(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        stale_boundary: datetime,
        project_filters: list[UUID],
    ) -> _ReviewSourceData:
        completed_entities = self._safe_fetch(
            lambda: self.task_repo.list_completed_between(
                period_start,
                period_end,
                project_ids=project_filters or None,
                limit=self.review_settings.max_completed_tasks,
            )
        )
        stale_entities = self._safe_fetch(
            lambda: self.task_repo.list_stale_tasks(
                stale_boundary,
                project_ids=project_filters or None,
                status_filter=DEFAULT_STATUS_FILTER,
                limit=self.review_settings.max_stale_tasks,
            )
        )
        memo_entities = self._safe_fetch(
            lambda: self.memo_repo.list_unprocessed_memos(
                created_after=period_start,
                limit=self.review_settings.max_unprocessed_memos,
            )
        )

        completed = [self._build_completed_digest(task) for task in completed_entities]
        stale = [self._build_stale_digest(task, reference=period_end) for task in stale_entities]

        active_projects = [
            ProjectRead.model_validate(project)
            for project in self._safe_fetch(lambda: self.project_repo.list_by_status(ProjectStatus.ACTIVE))
        ]
        filtered_projects = (
            [project for project in active_projects if project.id in project_filters]
            if project_filters
            else active_projects
        )

        memo_digests = []
        for memo in memo_entities:
            memo_read = MemoRead.model_validate(memo)
            memo_digests.append(
                MemoAuditDigest(
                    memo=memo_read,
                    linked_project=self._guess_project(memo_read, filtered_projects),
                )
            )

        return _ReviewSourceData(completed=completed, stale=stale, unprocessed_memos=memo_digests)

    def _resolve_period(self, query: WeeklyReviewInsightsQuery) -> tuple[datetime, datetime]:
        period_end = query.end or datetime.now()
        default_range = timedelta(days=self.review_settings.default_range_days)
        start = query.start or (period_end - default_range)
        if start > period_end:
            logger.debug("期間指定が不正のため start/end を入れ替えました。")
            return period_end, start
        return start, period_end

    def _build_completed_digest(self, task_entity: object) -> CompletedTaskDigest:
        task_read = TaskRead.model_validate(task_entity)
        memo_excerpt = self._memo_excerpt(getattr(task_entity, "memo", None))
        project_title = self._project_title(task_entity)
        return CompletedTaskDigest(task=task_read, memo_excerpt=memo_excerpt, project_title=project_title)

    def _build_stale_digest(self, task_entity: object, *, reference: datetime) -> ZombieTaskDigest:
        task_read = TaskRead.model_validate(task_entity)
        created_at: datetime = getattr(task_entity, "created_at", reference) or reference
        stale_days = max((reference - created_at).days, 0)
        memo_excerpt = self._memo_excerpt(getattr(task_entity, "memo", None))
        project_title = self._project_title(task_entity)
        return ZombieTaskDigest(
            task=task_read,
            stale_days=stale_days,
            memo_excerpt=memo_excerpt,
            project_title=project_title,
        )

    @staticmethod
    def _project_title(task_entity: object) -> str | None:
        project = getattr(task_entity, "project", None)
        return getattr(project, "title", None)

    @staticmethod
    def _memo_excerpt(memo_obj: object | None, *, limit: int = 80) -> str | None:
        if memo_obj is None:
            return None
        content = getattr(memo_obj, "content", None)
        if not content:
            return None
        sanitized = " ".join(str(content).split())
        return sanitized if len(sanitized) <= limit else f"{sanitized[:limit]}…"

    def _guess_project(self, memo: MemoRead, projects: list[ProjectRead]) -> ProjectRead | None:
        if not projects:
            return None
        haystack = f"{memo.title} {memo.content}".lower()
        for project in projects:
            if project.title.lower() in haystack:
                return project
        return None

    def _safe_fetch(self, fetcher: Callable[[], list[_T]]) -> list[_T]:
        try:
            return fetcher()
        except NotFoundError:
            logger.debug("レビュー用の取得結果が空のため空リストを返します。")
            return []
