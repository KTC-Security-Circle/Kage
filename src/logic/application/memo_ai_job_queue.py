"""Memo→タスク生成ジョブのシリアライズ処理キュー。"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from threading import Event, Lock, Thread
from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

from loguru import logger

if TYPE_CHECKING:  # pragma: no cover - 型チェック用
    from collections.abc import Callable

    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from models import MemoRead


class MemoAiJobStatus(str, Enum):
    """メモAIジョブの状態。"""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class GeneratedTaskPayload:
    """UI層へ渡す生成タスク情報。"""

    task_id: str
    title: str
    description: str | None
    tags: tuple[str, ...]
    route: str | None
    due_date: str | None
    project_title: str | None


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

    def __init__(self) -> None:
        self._jobs: dict[UUID, _MemoAiJobRecord] = {}
        self._queue: deque[UUID] = deque()
        self._lock = Lock()
        self._has_items = Event()
        self._worker = Thread(target=self._worker_loop, name="MemoAiJobWorker", daemon=True)
        self._worker.start()

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

    def _process(self, record: _MemoAiJobRecord) -> None:
        self._update_status(record, MemoAiJobStatus.RUNNING)
        try:
            logger.debug(
                f"MemoAIジョブ処理開始: job_id={record.job_id} memo_id={record.memo.id}"
            )
            output = self._run_agent(record.memo)
            record.tasks = [self._convert_task(task) for task in output.tasks]
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

        service = MemoToTaskApplicationService.get_instance()
        return service.clarify_memo(memo)

    def _convert_task(self, draft: TaskDraft) -> GeneratedTaskPayload:
        return GeneratedTaskPayload(
            task_id=str(uuid4()),
            title=draft.title,
            description=draft.description,
            tags=tuple(draft.tags or []),
            route=draft.route,
            due_date=draft.due_date,
            project_title=draft.project_title,
        )

    def _update_status(self, record: _MemoAiJobRecord, status: MemoAiJobStatus) -> None:
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
