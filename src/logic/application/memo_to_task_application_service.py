"""メモ→タスク変換 Application Service

`agents.task_agents.memo_to_task.MemoToTaskAgent` をアプリケーション層から直接扱うサービス。

利用側は `MemoToTaskApplicationService.clarify_memo(memo_text)` を呼ぶだけで、
内部で既存タグの収集や現在時刻(ISO8601)の組み立てなどのコンテキスト準備を行い、
エージェントの応答(`MemoToTaskAgentOutput`)を返します。

補助APIとして、タスク案のみを返す `generate_tasks_from_memo()` も提供します。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, override
from uuid import uuid4

from loguru import logger

from agents.base import AgentError
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from errors import ApplicationError
from logic.application.base import BaseApplicationService
from logic.unit_of_work import SqlModelUnitOfWork
from settings.manager import get_config_manager


class MemoToTaskServiceError(ApplicationError):
    """メモ→タスク変換時のアプリケーション層エラー。"""

    def __init__(self, message: str) -> None:
        super().__init__(f"MemoToTask 変換エラー: {message}")


class MemoToTaskApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """メモ→タスク変換 Application Service。

    既存タグや現在時刻などの付帯情報を収集し、`MemoToTaskAgent` を実行します。
    """

    def __init__(
        self,
        unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork,
        *,
        provider: LLMProvider | None = None,
        agent: MemoToTaskAgent | None = None,
    ) -> None:
        super().__init__(unit_of_work_factory)

        settings = get_config_manager().settings
        self._provider: LLMProvider = provider if provider is not None else settings.agents.provider
        self._agent: MemoToTaskAgent | None = agent

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> MemoToTaskApplicationService: ...

    # Public API ---------------------------------------------------------
    def clarify_memo(self, memo_text: str) -> MemoToTaskAgentOutput:
        """自由記述メモを解析し、タスク候補とメモ状態の提案を返す。

        Args:
            memo_text: ユーザーが入力したメモ本文

        Returns:
            MemoToTaskAgentOutput: 推定タスクとメモ状態の提案
        """
        from agents.task_agents.memo_to_task.schema import (
            MemoToTaskAgentOutput as OutputModel,
        )

        # 空入力は Clarify 継続を提案
        if not memo_text.strip():
            return OutputModel(tasks=[], suggested_memo_status="clarify")

        state: MemoToTaskState = {
            "memo_text": memo_text,
            "existing_tags": self._collect_existing_tag_names(),
            "current_datetime_iso": self._current_datetime_iso(),
        }

        result = self._invoke_agent(state)
        if result is None:
            msg = "エージェント応答が None でした"
            self._log_error_and_raise(msg)

        if isinstance(result, AgentError):
            self._log_error_and_raise(f"エージェントがエラーを返しました: {result}")

        if isinstance(result, MemoToTaskResult):
            return OutputModel(tasks=list(result.tasks), suggested_memo_status=result.suggested_memo_status)

        # ここには通常到達しない（AgentError か MemoToTaskResult のどちらか）
        msg_invalid = "エージェント応答の型が不正です"
        raise MemoToTaskServiceError(msg_invalid)

    def generate_tasks_from_memo(self, memo_text: str) -> list[TaskDraft]:
        """メモ本文からタスク案だけを抽出するヘルパー。"""
        output = self.clarify_memo(memo_text)
        return list(output.tasks)

    # Internal helpers --------------------------------------------------
    def _get_agent(self) -> MemoToTaskAgent:
        if self._agent is None:
            from agents.task_agents.memo_to_task.agent import MemoToTaskAgent

            self._agent = MemoToTaskAgent(provider=self._provider)
        return self._agent

    def _invoke_agent(self, state: MemoToTaskState) -> MemoToTaskResult | AgentError:
        agent = self._get_agent()
        thread_id = str(uuid4())
        return agent.invoke(state, thread_id)

    def _collect_existing_tag_names(self) -> list[str]:
        """既存タグの名称一覧を取得する。"""
        names: list[str] = []
        # 遅延 import で循環を回避
        from logic.services.tag_service import TagService

        with self._unit_of_work_factory() as uow:
            tag_service = uow.get_service(TagService)
            tags = tag_service.get_all()

        for tag in tags:
            name = getattr(tag, "name", "").strip()
            if not name or name in names:
                continue
            names.append(name)
        return names

    def _current_datetime_iso(self) -> str:
        """現在日時のISO8601文字列を返す。"""
        return datetime.now(UTC).isoformat()

    def _log_error_and_raise(self, msg: str) -> None:
        logger.error(msg)
        raise MemoToTaskServiceError(msg)


# 型ヒント用の前方宣言
if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from agents.agent_conf import LLMProvider
    from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from agents.task_agents.memo_to_task.state import MemoToTaskState

__all__ = [
    "MemoToTaskApplicationService",
    "MemoToTaskServiceError",
]
