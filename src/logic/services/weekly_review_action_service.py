"""週次レビューStep2でのアクション適用を担うサービス。"""

from __future__ import annotations

from collections.abc import Iterable  # noqa: TC003
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from loguru import logger

from agents.base import AgentError
from agents.task_agents.weekly_review_actions import WeeklyReviewTaskAgent
from errors import NotFoundError
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.services.base import MyBaseError, ServiceBase, handle_service_errors
from models import (
    TagCreate,
    TaskCreate,
    TaskStatus,
    TaskUpdate,
    WeeklyReviewActionResult,
    WeeklyReviewSplitPlan,
    WeeklyReviewSplitSubtask,
    WeeklyReviewSplitTarget,
    WeeklyReviewSplitTaskInfo,
    WeeklyReviewTaskDecision,
)
from settings.manager import get_config_manager

if TYPE_CHECKING:
    from logic.repositories import RepositoryFactory

SOMEDAY_TAG_NAME = "Someday/Maybe"


class WeeklyReviewActionServiceError(MyBaseError):
    """週次レビュー整理アクションで発生するエラー。"""


class WeeklyReviewActionService(ServiceBase):
    """ゾンビタスクに対する split/someday/delete をまとめて適用するサービス。"""

    def __init__(
        self,
        task_repo: TaskRepository,
        tag_repo: TagRepository,
        task_agent: WeeklyReviewTaskAgent,
    ) -> None:
        self.task_repo = task_repo
        self.tag_repo = tag_repo
        self.task_agent = task_agent
        self._someday_tag_id: UUID | None = None

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> WeeklyReviewActionService:
        task_repo = repo_factory.create(TaskRepository)
        tag_repo = repo_factory.create(TagRepository)
        cfg = get_config_manager().settings.agents
        provider = cfg.provider
        runtime_cfg = getattr(cfg, "runtime", None)
        device = None
        if runtime_cfg and getattr(runtime_cfg, "device", None) is not None:
            device = str(runtime_cfg.device.value)
        model_name_option = cfg.get_model_name("review")
        resolved_model_name = str(model_name_option) if model_name_option is not None else None
        agent = WeeklyReviewTaskAgent(provider=provider, model_name=resolved_model_name, device=device)
        return cls(task_repo, tag_repo, agent)

    @handle_service_errors("週次レビュー整理", "実行", WeeklyReviewActionServiceError)
    def apply_actions(self, decisions: list[WeeklyReviewTaskDecision]) -> WeeklyReviewActionResult:
        if not decisions:
            return WeeklyReviewActionResult(message="実行対象がありません")

        split_ids = [d.task_id for d in decisions if d.action == "split"]
        someday_ids = [d.task_id for d in decisions if d.action == "someday"]
        delete_ids = [d.task_id for d in decisions if d.action == "delete"]

        errors: list[str] = []
        task_map = self._fetch_tasks({*split_ids, *someday_ids, *delete_ids}, errors)

        created_subtasks, split_infos = self._process_split_actions(split_ids, task_map, errors)
        moved, moved_ids = self._process_someday_actions(someday_ids, task_map, errors)
        deleted, deleted_ids = self._process_delete_actions(delete_ids, errors)

        message = self._build_summary(created_subtasks, moved, deleted)
        return WeeklyReviewActionResult(
            created_subtasks=created_subtasks,
            split_tasks=split_infos,
            split_task_ids=[info.task_id for info in split_infos],
            moved_to_someday=moved,
            someday_task_ids=moved_ids,
            deleted_tasks=deleted,
            deleted_task_ids=deleted_ids,
            errors=errors,
            message=message,
        )

    def _process_split_actions(
        self,
        task_ids: list[UUID],
        task_map: dict[UUID, object],
        errors: list[str],
    ) -> tuple[int, list[WeeklyReviewSplitTaskInfo]]:
        if not task_ids:
            return 0, []
        targets = self._build_split_targets(task_ids, task_map, errors)
        if not targets:
            return 0, []
        try:
            plans = self.task_agent.plan_subtasks(targets)
        except AgentError as exc:
            errors.append(f"細分化エージェントの呼び出しに失敗しました: {exc}")
            logger.warning("WeeklyReviewTaskAgent failure: %s", exc)
            return 0, []
        normalized_plans = self._normalize_plan_parent_ids(plans, targets)
        return self._persist_split_plans(normalized_plans, task_map, errors)

    def _process_someday_actions(
        self,
        task_ids: list[UUID],
        task_map: dict[UUID, object],
        errors: list[str],
    ) -> tuple[int, list[UUID]]:
        if not task_ids:
            return 0, []
        tag_id = self._ensure_someday_tag_id()
        moved = 0
        moved_ids: list[UUID] = []
        for task_id in task_ids:
            task = task_map.get(task_id)
            if task is None:
                errors.append(f"タスク({task_id})が見つかりませんでした")
                continue
            update = TaskUpdate(status=TaskStatus.WAITING, due_date=None)
            self.task_repo.update(task_id, update)
            try:
                self.task_repo.add_tag(task_id, tag_id)
            except NotFoundError:
                errors.append(f"タスク({task_id})へのタグ付けに失敗しました")
                continue
            moved += 1
            moved_ids.append(task_id)
        return moved, moved_ids

    def _process_delete_actions(self, task_ids: list[UUID], errors: list[str]) -> tuple[int, list[UUID]]:
        if not task_ids:
            return 0, []
        deleted = 0
        deleted_ids: list[UUID] = []
        for task_id in task_ids:
            success = self.task_repo.delete(task_id)
            if success:
                deleted += 1
                deleted_ids.append(task_id)
            else:
                errors.append(f"タスク({task_id})の削除に失敗しました")
        return deleted, deleted_ids

    def _fetch_tasks(self, task_ids: Iterable[UUID], errors: list[str]) -> dict[UUID, object]:
        task_map: dict[UUID, object] = {}
        for task_id in task_ids:
            if task_id in task_map:
                continue
            try:
                task = self.task_repo.get_by_id(task_id, with_details=True)
                task_map[task_id] = task
            except NotFoundError:
                errors.append(f"タスク({task_id})が見つかりませんでした")
        return task_map

    def _build_split_targets(
        self,
        task_ids: list[UUID],
        task_map: dict[UUID, object],
        errors: list[str],
    ) -> list[WeeklyReviewSplitTarget]:
        targets: list[WeeklyReviewSplitTarget] = []
        for task_id in task_ids:
            task = task_map.get(task_id)
            if task is None:
                errors.append(f"タスク({task_id})が見つかりませんでした")
                continue
            stale_days = self._calc_stale_days(task)
            context = self._extract_context(task)
            targets.append(
                WeeklyReviewSplitTarget(
                    task_id=task_id,
                    title=str(getattr(task, "title", "")),
                    stale_days=stale_days,
                    context=context,
                )
            )
        return targets

    def _persist_split_plans(
        self,
        plans: list[WeeklyReviewSplitPlan],
        task_map: dict[UUID, object],
        errors: list[str],
    ) -> tuple[int, list[WeeklyReviewSplitTaskInfo]]:
        created = 0
        created_infos: list[WeeklyReviewSplitTaskInfo] = []
        for plan in plans:
            parent = task_map.get(plan.parent_task_id)
            if parent is None:
                errors.append(f"細分化対象タスク({plan.parent_task_id})が見つかりません")
                continue
            if plan.status != "ready" or not plan.subtasks:
                errors.append(f"タスク({plan.parent_task_id})の細分化結果が空、または失敗しました")
                continue
            for sub in plan.subtasks:
                description = self._compose_subtask_description(parent, plan, sub)
                create_model = TaskCreate(
                    title=sub.title,
                    description=description,
                    status=TaskStatus.DRAFT,
                    project_id=getattr(parent, "project_id", None),
                    memo_id=getattr(parent, "memo_id", None),
                )
                created_task = self.task_repo.create(create_model)
                created_id = getattr(created_task, "id", None)
                if created_id is not None:
                    created_infos.append(
                        WeeklyReviewSplitTaskInfo(parent_task_id=plan.parent_task_id, task_id=created_id)
                    )
                created += 1
            self.task_repo.update(plan.parent_task_id, TaskUpdate(status=TaskStatus.PROGRESS))
        return created, created_infos

    def _normalize_plan_parent_ids(
        self,
        plans: list[WeeklyReviewSplitPlan],
        targets: list[WeeklyReviewSplitTarget],
    ) -> list[WeeklyReviewSplitPlan]:
        fallback_ids = [target.task_id for target in targets]
        fallback_iter = iter(fallback_ids)
        normalized: list[WeeklyReviewSplitPlan] = []
        for plan_entry in plans:
            parent_id = plan_entry.parent_task_id
            if parent_id.int == 0:
                try:
                    replacement = next(fallback_iter)
                except StopIteration:
                    replacement = parent_id
                normalized_plan = plan_entry.model_copy(update={"parent_task_id": replacement})
            else:
                normalized_plan = plan_entry
            normalized.append(normalized_plan)
        return normalized

    def _compose_subtask_description(
        self,
        parent: object,
        plan: WeeklyReviewSplitPlan,
        subtask: WeeklyReviewSplitSubtask,
    ) -> str:
        parent_title = getattr(parent, "title", "親タスク")
        pieces = [subtask.description or ""]
        if subtask.first_step_hint:
            pieces.append(f"最初の一歩: {subtask.first_step_hint}")
        pieces.append(f"親タスク: {parent_title}")
        if plan.rationale:
            pieces.append(f"分割理由: {plan.rationale}")
        return "\n".join(part for part in pieces if part)

    def _calc_stale_days(self, task: object) -> int:
        created_at = getattr(task, "created_at", None)
        if isinstance(created_at, datetime):
            delta = datetime.now() - created_at
            return max(delta.days, 0)
        return 0

    def _extract_context(self, task: object) -> str | None:
        description = getattr(task, "description", None) or ""
        memo = getattr(task, "memo", None)
        memo_excerpt = None
        if memo is not None:
            memo_excerpt = getattr(memo, "content", None)
        context_parts = [description.strip(), (memo_excerpt or "").strip()]
        context = " / ".join(part for part in context_parts if part)
        return context or None

    def _ensure_someday_tag_id(self) -> UUID:
        if self._someday_tag_id is not None:
            return self._someday_tag_id
        try:
            tag = self.tag_repo.get_by_name(SOMEDAY_TAG_NAME)
        except NotFoundError:
            tag = self.tag_repo.create(TagCreate(name=SOMEDAY_TAG_NAME))
        if tag.id is None:
            msg = "Someday/Maybe タグのIDが取得できません"
            raise WeeklyReviewActionServiceError(msg)
        self._someday_tag_id = tag.id
        return self._someday_tag_id

    def _build_summary(self, created: int, moved: int, deleted: int) -> str:
        parts: list[str] = []
        if created:
            parts.append(f"細分化 {created}件")
        if moved:
            parts.append(f"Someday移動 {moved}件")
        if deleted:
            parts.append(f"削除 {deleted}件")
        return " / ".join(parts) if parts else "変更はありません"
