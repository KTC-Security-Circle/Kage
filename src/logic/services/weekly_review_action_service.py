"""週次レビューStep2でのアクション適用を担うサービス。"""

from __future__ import annotations

from collections.abc import Iterable  # noqa: TC003
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from loguru import logger

from agents.base import AgentError
from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
from agents.task_agents.memo_to_task.schema import TaskDraft
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from agents.task_agents.weekly_review_actions import WeeklyReviewTaskAgent
from errors import NotFoundError
from logic.repositories.memo import MemoRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.services.base import MyBaseError, ServiceBase, handle_service_errors
from models import (
    MemoRead,
    MemoStatus,
    MemoUpdate,
    TagCreate,
    TaskCreate,
    TaskStatus,
    TaskUpdate,
    WeeklyReviewActionResult,
    WeeklyReviewMemoDecision,
    WeeklyReviewMemoTaskInfo,
    WeeklyReviewSplitPlan,
    WeeklyReviewSplitSubtask,
    WeeklyReviewSplitTarget,
    WeeklyReviewSplitTaskInfo,
    WeeklyReviewTaskDecision,
)
from settings.manager import get_config_manager
from settings.models import AgentDetailLevel

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
        memo_repo: MemoRepository,
        task_agent: WeeklyReviewTaskAgent,
        memo_agent: MemoToTaskAgent,
    ) -> None:
        self.task_repo = task_repo
        self.tag_repo = tag_repo
        self.memo_repo = memo_repo
        self.task_agent = task_agent
        self.memo_agent = memo_agent
        self._someday_tag_id: UUID | None = None
        self._memo_prompt_overrides = self._build_memo_prompt_overrides()

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> WeeklyReviewActionService:
        task_repo = repo_factory.create(TaskRepository)
        tag_repo = repo_factory.create(TagRepository)
        memo_repo = repo_factory.create(MemoRepository)
        cfg = get_config_manager().settings.agents
        provider = cfg.provider
        runtime_cfg = getattr(cfg, "runtime", None)
        device = None
        if runtime_cfg and getattr(runtime_cfg, "device", None) is not None:
            device = str(runtime_cfg.device.value)
        review_model_name = cfg.get_model_name("review")
        resolved_review_model = str(review_model_name) if review_model_name is not None else None
        task_agent = WeeklyReviewTaskAgent(provider=provider, model_name=resolved_review_model, device=device)

        memo_model_name = cfg.get_model_name("memo_to_task")
        resolved_memo_model = str(memo_model_name) if memo_model_name is not None else None
        memo_agent = MemoToTaskAgent(provider=provider, model_name=resolved_memo_model, device=device)

        return cls(task_repo, tag_repo, memo_repo, task_agent, memo_agent)

    @handle_service_errors("週次レビュー整理", "実行", WeeklyReviewActionServiceError)
    def apply_actions(
        self,
        task_decisions: list[WeeklyReviewTaskDecision],
        memo_decisions: list[WeeklyReviewMemoDecision] | None = None,
    ) -> WeeklyReviewActionResult:
        memo_decisions = memo_decisions or []
        if not task_decisions and not memo_decisions:
            return WeeklyReviewActionResult(message="実行対象がありません")

        split_ids = [d.task_id for d in task_decisions if d.action == "split"]
        someday_ids = [d.task_id for d in task_decisions if d.action == "someday"]
        delete_ids = [d.task_id for d in task_decisions if d.action == "delete"]

        memo_create_ids = [d.memo_id for d in memo_decisions if d.action == "create_task"]
        memo_archive_ids = [d.memo_id for d in memo_decisions if d.action == "archive"]
        memo_skip_ids = [d.memo_id for d in memo_decisions if d.action == "skip"]

        errors: list[str] = []
        task_map = self._fetch_tasks({*split_ids, *someday_ids, *delete_ids}, errors)
        memo_map = self._fetch_memos({*memo_create_ids, *memo_archive_ids, *memo_skip_ids}, errors)

        created_subtasks, split_infos = self._process_split_actions(split_ids, task_map, errors)
        moved, moved_ids = self._process_someday_actions(someday_ids, task_map, errors)
        deleted, deleted_ids = self._process_delete_actions(delete_ids, errors)

        memo_created, memo_infos = self._process_memo_create_actions(memo_create_ids, memo_map, errors)
        memos_archived, archived_memo_ids = self._process_memo_status_actions(
            memo_archive_ids,
            memo_map,
            MemoStatus.IDEA,
            errors,
        )
        memos_skipped, skipped_memo_ids = self._process_memo_status_actions(
            memo_skip_ids,
            memo_map,
            MemoStatus.ARCHIVE,
            errors,
        )

        message = self._build_summary(created_subtasks, moved, deleted, memo_created, memos_archived, memos_skipped)
        return WeeklyReviewActionResult(
            created_subtasks=created_subtasks,
            split_tasks=split_infos,
            split_task_ids=[info.task_id for info in split_infos],
            moved_to_someday=moved,
            someday_task_ids=moved_ids,
            deleted_tasks=deleted,
            deleted_task_ids=deleted_ids,
            memo_tasks_created=memo_created,
            memo_task_infos=memo_infos,
            memo_task_ids=[info.task_id for info in memo_infos],
            memos_archived=memos_archived,
            archived_memo_ids=archived_memo_ids,
            memos_skipped=memos_skipped,
            skipped_memo_ids=skipped_memo_ids,
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

    def _process_memo_create_actions(
        self,
        memo_ids: list[UUID],
        memo_map: dict[UUID, object],
        errors: list[str],
    ) -> tuple[int, list[WeeklyReviewMemoTaskInfo]]:
        if not memo_ids:
            return 0, []
        existing_tags = self._collect_existing_tag_names()
        created = 0
        infos: list[WeeklyReviewMemoTaskInfo] = []
        for memo_id in memo_ids:
            memo = memo_map.get(memo_id)
            if memo is None:
                errors.append(f"メモ({memo_id})が見つかりませんでした")
                continue
            memo_read = MemoRead.model_validate(memo)
            state: MemoToTaskState = {
                "memo": memo_read,
                "existing_tags": existing_tags,
                "current_datetime_iso": datetime.now(UTC).isoformat(),
            }
            overrides = self._memo_prompt_overrides
            detail_hint = overrides.get("detail_hint")
            custom_text = overrides.get("custom_instructions")
            if detail_hint:
                state["detail_hint"] = detail_hint
            if custom_text:
                state["custom_instructions"] = custom_text
            response = self.memo_agent.invoke(state, thread_id=str(uuid4()))
            drafts = self._extract_memo_tasks(response, memo_id, errors)
            if not drafts:
                continue
            for draft in drafts:
                task_model = TaskCreate(
                    title=draft.title,
                    description=draft.description or memo_read.content or "",
                    status=TaskStatus.DRAFT,
                    memo_id=memo_read.id,
                    due_date=self._coerce_due_date(draft.due_date),
                )
                created_task = self.task_repo.create(task_model)
                created += 1
                task_id = getattr(created_task, "id", None)
                if task_id is not None:
                    infos.append(WeeklyReviewMemoTaskInfo(memo_id=memo_read.id, task_id=task_id))
            try:
                self.memo_repo.update(memo_read.id, MemoUpdate(status=MemoStatus.ACTIVE))
            except NotFoundError:
                errors.append(f"メモ({memo_id})のステータス更新に失敗しました")
        return created, infos

    def _process_memo_status_actions(
        self,
        memo_ids: list[UUID],
        memo_map: dict[UUID, object],
        status: MemoStatus,
        errors: list[str],
    ) -> tuple[int, list[UUID]]:
        if not memo_ids:
            return 0, []
        updated: list[UUID] = []
        for memo_id in memo_ids:
            if memo_id not in memo_map:
                errors.append(f"メモ({memo_id})が見つかりませんでした")
                continue
            try:
                self.memo_repo.update(memo_id, MemoUpdate(status=status))
                updated.append(memo_id)
            except NotFoundError:
                errors.append(f"メモ({memo_id})の更新に失敗しました")
        return len(updated), updated

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

    def _fetch_memos(self, memo_ids: Iterable[UUID], errors: list[str]) -> dict[UUID, object]:
        memo_map: dict[UUID, object] = {}
        for memo_id in memo_ids:
            if memo_id in memo_map:
                continue
            try:
                memo = self.memo_repo.get_by_id(memo_id, with_details=True)
                memo_map[memo_id] = memo
            except NotFoundError:
                errors.append(f"メモ({memo_id})が見つかりませんでした")
        return memo_map

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
        # 正常な親ID候補（実在するターゲットID）を準備
        fallback_ids = [target.task_id for target in targets]
        fallback_iter = iter(fallback_ids)
        normalized: list[WeeklyReviewSplitPlan] = []
        valid_target_set = set(fallback_ids)
        for plan_entry in plans:
            parent_id = plan_entry.parent_task_id
            # 1) ゼロUUID (0000...) の場合はフォールバックに差し替え
            # 2) ターゲットに存在しない親ID（プレースホルダー等）の場合も差し替え
            if parent_id.int == 0 or parent_id not in valid_target_set:
                try:
                    replacement = next(fallback_iter)
                except StopIteration:
                    replacement = parent_id
                normalized_plan = plan_entry.model_copy(update={"parent_task_id": replacement})
            else:
                normalized_plan = plan_entry
            normalized.append(normalized_plan)
        return normalized

    def _collect_existing_tag_names(self) -> list[str]:
        try:
            tags = self.tag_repo.get_all()
        except NotFoundError:
            return []
        names: list[str] = []
        for tag in tags:
            name = getattr(tag, "name", "").strip()
            if not name or name in names:
                continue
            names.append(name)
        return names

    def _extract_memo_tasks(
        self,
        response: MemoToTaskResult | AgentError | object,
        memo_id: UUID,
        errors: list[str],
    ) -> list[TaskDraft]:
        if isinstance(response, AgentError):
            errors.append(f"MemoToTaskAgent がエラーを返しました (memo_id={memo_id}): {response}")
            return []
        if isinstance(response, MemoToTaskResult):
            return list(response.tasks)
        tasks = getattr(response, "tasks", None)
        if isinstance(tasks, list):
            valid: list[TaskDraft] = []
            for item in tasks:
                if isinstance(item, TaskDraft):
                    valid.append(item)
                elif isinstance(item, dict):
                    try:
                        valid.append(TaskDraft.model_validate(item))
                    except (TypeError, ValueError) as exc:
                        logger.debug("メモタスクドラフトの検証に失敗しました", memo_id=str(memo_id), error=str(exc))
                        continue
            return valid
        errors.append(f"MemoToTaskAgent が有効なタスクを返しませんでした (memo_id={memo_id})")
        return []

    def _build_memo_prompt_overrides(self) -> dict[str, str]:
        cfg = get_config_manager().settings.agents
        prompt_cfg = getattr(cfg, "memo_to_task_prompt", None)
        if prompt_cfg is None:
            return {
                "custom_instructions": "",
                "detail_hint": self._detail_hint_from_level(AgentDetailLevel.BALANCED),
            }
        custom_text = str(getattr(prompt_cfg, "custom_instructions", "") or "").strip()
        level_value = getattr(prompt_cfg, "detail_level", AgentDetailLevel.BALANCED)
        if isinstance(level_value, AgentDetailLevel):
            level = level_value
        else:
            try:
                level = AgentDetailLevel(str(level_value))
            except ValueError:
                level = AgentDetailLevel.BALANCED
        return {
            "custom_instructions": custom_text,
            "detail_hint": self._detail_hint_from_level(level),
        }

    @staticmethod
    def _detail_hint_from_level(level: AgentDetailLevel) -> str:
        if level == AgentDetailLevel.BRIEF:
            return "回答は要点のみを簡潔にまとめてください。"
        if level == AgentDetailLevel.DETAILED:
            return "背景や理由も含めて丁寧に説明してください。"
        return "バランスよく適度な詳細度で回答してください。"

    @staticmethod
    def _coerce_due_date(value: str | None) -> date | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        normalized = raw[:-1] + "+00:00" if raw.endswith(("Z", "z")) else raw
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        return parsed.date()

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

    def _build_summary(
        self,
        created: int,
        moved: int,
        deleted: int,
        memo_created: int,
        memo_archived: int,
        memo_skipped: int,
    ) -> str:
        parts: list[str] = []
        if created:
            parts.append(f"細分化 {created}件")
        if moved:
            parts.append(f"Someday移動 {moved}件")
        if deleted:
            parts.append(f"削除 {deleted}件")
        if memo_created:
            parts.append(f"メモ→タスク {memo_created}件")
        if memo_archived:
            parts.append(f"資料化 {memo_archived}件")
        if memo_skipped:
            parts.append(f"メモ削除 {memo_skipped}件")
        return " / ".join(parts) if parts else "変更はありません"
