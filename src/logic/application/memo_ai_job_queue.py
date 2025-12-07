"""Memo→タスク生成ジョブのシリアライズ処理キュー。"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from threading import Event, Lock, Thread
from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

from loguru import logger

if TYPE_CHECKING:  # pragma: no cover - 型チェック用
    from collections.abc import Callable

    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from logic.application.apps import ApplicationServices
    from models import MemoRead, TaskStatus


class MemoAiJobStatus(str, Enum):
    """メモAIジョブの状態。"""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class GeneratedTaskPayload:
    """UI層へ渡す生成タスク情報。"""

    task_id: UUID
    title: str
    description: str | None
    tags: tuple[str, ...]
    route: str | None
    due_date: str | None
    project_title: str | None
    status: TaskStatus


@dataclass(slots=True)
class MemoAiJobSnapshot:
    """ジョブ状態を外部に公開するスナップショット。"""

    job_id: UUID
    memo_id: UUID
    status: MemoAiJobStatus
    tasks: tuple[GeneratedTaskPayload, ...] = field(default_factory=tuple)
    suggested_memo_status: str | None = None
    error_message: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class _MemoAiJobRecord:
    job_id: UUID
    memo: MemoRead
    status: MemoAiJobStatus = MemoAiJobStatus.QUEUED
    tasks: list[GeneratedTaskPayload] = field(default_factory=list)
    suggested_memo_status: str | None = None
    error_message: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    callback: Callable[[MemoAiJobSnapshot], None] | None = None

    def to_snapshot(self) -> MemoAiJobSnapshot:
        return MemoAiJobSnapshot(
            job_id=self.job_id,
            memo_id=self.memo.id,
            status=self.status,
            tasks=tuple(self.tasks),
            suggested_memo_status=self.suggested_memo_status,
            error_message=self.error_message,
            updated_at=self.updated_at,
        )


class MemoAiJobQueue:
    """単一並列で MemoToTaskAgent を実行するメモリキュー。"""

    def __init__(self, *, apps: ApplicationServices | None = None) -> None:
        self._jobs: dict[UUID, _MemoAiJobRecord] = {}
        self._queue: deque[UUID] = deque()
        self._lock = Lock()
        self._has_items = Event()
        self._worker = Thread(target=self._worker_loop, name="MemoAiJobWorker", daemon=True)
        self._worker.start()
        from logic.application.apps import ApplicationServices

        self._apps: ApplicationServices = apps or ApplicationServices.create()

        # Cleanup/retention configuration
        self._job_retention_seconds: int = 600  # 完了したジョブの保持期間（秒）
        self._job_max_entries: int = 10  # 最大件数制限（無制限増加防止）
        self._cleanup_interval_seconds: int = 60  # クリーナー実行間隔（秒）

        # Start background cleaner to evict old/too-many jobs
        self._cleaner = Thread(target=self._cleaner_loop, name="MemoAiJobCleaner", daemon=True)
        self._cleaner.start()

    def enqueue(
        self,
        memo: MemoRead,
        *,
        callback: Callable[[MemoAiJobSnapshot], None] | None = None,
    ) -> MemoAiJobSnapshot:
        """メモを生成キューへ登録する。"""
        job_id = uuid4()
        record = _MemoAiJobRecord(job_id=job_id, memo=memo, callback=callback)
        with self._lock:
            self._jobs[job_id] = record
            self._queue.append(job_id)
            self._has_items.set()
        logger.info(f"MemoAIジョブを登録しました: job_id={job_id} memo_id={memo.id}")
        return record.to_snapshot()

    def get_snapshot(self, job_id: UUID) -> MemoAiJobSnapshot | None:
        """ジョブの最新状態を返す。"""
        with self._lock:
            record = self._jobs.get(job_id)
            if record is None:
                return None
            return record.to_snapshot()

    def _worker_loop(self) -> None:
        while True:
            self._has_items.wait()
            job_id = self._pop_left()
            if job_id is None:
                self._has_items.clear()
                continue
            record = self._jobs.get(job_id)
            if record is None:
                continue
            self._process(record)

    def _pop_left(self) -> UUID | None:
        with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()

    def _cleaner_loop(self) -> None:
        """バックグラウンドで古い完了ジョブを削除し、最大件数を超えたら古いものから削除する。"""
        while True:
            # Sleep via Event wait to be interruptible in future if needed
            self._has_items.wait(timeout=self._cleanup_interval_seconds)
            try:
                self._cleanup_jobs()
            except Exception:
                logger.exception("MemoAIジョブクリーナーで例外が発生しました")

    def _cleanup_jobs(self) -> None:
        """内部ジョブ辞書を掃除する。

        - 完了（SUCCEEDED/FAILED）してから一定時間経過したジョブを削除する。
        - 総件数が `_job_max_entries` を超えた場合、古いジョブから削除する。
        """
        now = datetime.now(UTC)
        retention = timedelta(seconds=self._job_retention_seconds)
        removed: list[UUID] = []
        with self._lock:
            removed.extend(self._remove_old_completed(now, retention))
            removed.extend(self._enforce_max_entries())

        if removed:
            logger.info("MemoAIジョブをクリーンアップしました: removed=%d", len(removed))

    def _remove_old_completed(self, now: datetime, retention: timedelta) -> list[UUID]:
        """完了済みで保持期間を超えたジョブを削除して、その job_id を返す。"""
        removed: list[UUID] = []
        for job_id, record in list(self._jobs.items()):
            if record.status in (MemoAiJobStatus.SUCCEEDED, MemoAiJobStatus.FAILED) and (
                now - record.updated_at > retention
            ):
                removed.append(job_id)
                del self._jobs[job_id]
                try:
                    while job_id in self._queue:
                        self._queue.remove(job_id)
                except ValueError:
                    pass
        return removed

    def _enforce_max_entries(self) -> list[UUID]:
        """総件数が上限を超えていたら、古いジョブから削除する。削除した job_id を返す。"""
        removed: list[UUID] = []
        if len(self._jobs) <= self._job_max_entries:
            return removed

        # sort candidates: prefer completed then by updated_at asc
        candidates = sorted(
            self._jobs.items(),
            key=lambda kv: (
                0 if kv[1].status in (MemoAiJobStatus.SUCCEEDED, MemoAiJobStatus.FAILED) else 1,
                kv[1].updated_at,
            ),
        )
        to_remove = len(self._jobs) - self._job_max_entries
        for i in range(to_remove):
            job_id, _ = candidates[i]
            try:
                del self._jobs[job_id]
            except KeyError:
                continue
            try:
                while job_id in self._queue:
                    self._queue.remove(job_id)
            except ValueError:
                pass
            removed.append(job_id)
        return removed

    def _process(self, record: _MemoAiJobRecord) -> None:
        self._update_status(record, MemoAiJobStatus.RUNNING)
        try:
            logger.debug(f"MemoAIジョブ処理開始: job_id={record.job_id} memo_id={record.memo.id}")
            output = self._run_agent(record.memo)
            record.tasks = self._create_draft_tasks(record.memo, output.tasks)
            record.suggested_memo_status = output.suggested_memo_status
            self._update_status(record, MemoAiJobStatus.SUCCEEDED)
            logger.debug(
                f"MemoAIジョブ処理完了: job_id={record.job_id} tasks={len(record.tasks)} "
                f"status={record.suggested_memo_status}"
            )
        except Exception as exc:  # pragma: no cover - エージェント内部の例外
            logger.exception("MemoAIジョブで例外が発生しました: job_id=%s", record.job_id)
            record.error_message = str(exc)
            self._update_status(record, MemoAiJobStatus.FAILED)
        finally:
            snapshot = record.to_snapshot()
            if record.callback:
                try:
                    record.callback(snapshot)
                except Exception:
                    logger.exception("MemoAIジョブ完了後のコールバックで例外が発生しました")

    def _run_agent(self, memo: MemoRead) -> MemoToTaskAgentOutput:
        from logic.application.memo_to_task_application_service import MemoToTaskApplicationService

        service = self._apps.get_service(MemoToTaskApplicationService)
        return service.clarify_memo(memo)

    def _create_draft_tasks(self, memo: MemoRead, drafts: list[TaskDraft]) -> list[GeneratedTaskPayload]:
        from logic.application.task_application_service import TaskApplicationService
        from models import TaskStatus

        task_service = self._apps.get_service(TaskApplicationService)
        payloads: list[GeneratedTaskPayload] = []
        for draft in drafts:
            due_date_value = self._coerce_due_date(draft.due_date)
            created_task = task_service.create(
                title=draft.title,
                description=draft.description or "",
                status=TaskStatus.DRAFT,
                memo_id=memo.id,
                due_date=due_date_value,
            )
            payloads.append(
                GeneratedTaskPayload(
                    task_id=created_task.id,
                    title=created_task.title,
                    description=created_task.description,
                    tags=tuple(tag.name for tag in created_task.tags) or tuple(draft.tags or []),
                    route=draft.route,
                    due_date=draft.due_date,
                    project_title=draft.project_title,
                    status=created_task.status,
                )
            )
        return payloads

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

    def _update_status(self, record: _MemoAiJobRecord, status: MemoAiJobStatus) -> None:
        with self._lock:
            record.status = status
            record.updated_at = datetime.now(UTC)


_queue_instance: MemoAiJobQueue | None = None
_queue_lock = Lock()


def get_memo_ai_job_queue() -> MemoAiJobQueue:
    """シングルトンの MemoAiJobQueue を返す。"""
    instance = cast("MemoAiJobQueue | None", globals().get("_queue_instance"))
    if instance is None:
        with _queue_lock:
            instance = cast("MemoAiJobQueue | None", globals().get("_queue_instance"))
            if instance is None:
                instance = MemoAiJobQueue()
                globals()["_queue_instance"] = instance
    return instance


__all__ = [
    "GeneratedTaskPayload",
    "MemoAiJobQueue",
    "MemoAiJobSnapshot",
    "MemoAiJobStatus",
    "get_memo_ai_job_queue",
]
