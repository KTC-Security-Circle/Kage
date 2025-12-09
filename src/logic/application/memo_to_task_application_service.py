"""メモ→タスク変換 Application Service

`agents.task_agents.memo_to_task.MemoToTaskAgent` をアプリケーション層から直接扱うサービス。

利用側は `MemoToTaskApplicationService.clarify_memo(memo)` を呼ぶだけで、
内部で既存タグの収集や現在時刻(ISO8601)の組み立てなどのコンテキスト準備を行い、
エージェントの応答(`MemoToTaskAgentOutput`)を返します。

補助APIとして、タスク案のみを返す `generate_tasks_from_memo()` も提供します。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, TypedDict, override
from uuid import uuid4

from loguru import logger

from agents.agent_conf import LLMProvider, OpenVINODevice
from agents.base import AgentError
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from errors import ApplicationError
from logic.application.base import BaseApplicationService
from logic.application.settings_application_service import SettingsApplicationService
from logic.unit_of_work import SqlModelUnitOfWork
from models import MemoRead
from settings.models import AgentDetailLevel

TASK_COUNT_HINT_BY_LEVEL: dict[AgentDetailLevel, str] = {
    AgentDetailLevel.BRIEF: "最優先度の 2 件を中心に提示してください。",
    AgentDetailLevel.BALANCED: "状況に応じて 3 件前後を提案してください。",
    AgentDetailLevel.DETAILED: "観点が異なる最大 5 件を整理してください。",
}

RECOMMENDED_TASK_COUNT_BY_LEVEL: dict[AgentDetailLevel, int] = {
    AgentDetailLevel.BRIEF: 2,
    AgentDetailLevel.BALANCED: 3,
    AgentDetailLevel.DETAILED: 5,
}


class PromptOverrides(TypedDict):
    """プロンプトオーバーライド設定。"""

    custom_instructions: str
    detail_hint: str
    task_count_hint: str
    recommended_task_count: int


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
        agent: MemoToTaskAgent | None = None,
    ) -> None:
        super().__init__(unit_of_work_factory)
        self._agent: MemoToTaskAgent | None = agent

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> MemoToTaskApplicationService:
        from typing import cast

        instance = super().get_instance(*args, **kwargs)
        return cast("MemoToTaskApplicationService", instance)

    # Public API ---------------------------------------------------------
    def clarify_memo(self, memo: MemoRead) -> MemoToTaskAgentOutput:
        """自由記述メモを解析し、タスク候補とメモ状態の提案を返す。

        Args:
            memo: 解析対象のメモ情報

        Returns:
            MemoToTaskAgentOutput: 推定タスクとメモ状態の提案
        """
        from agents.task_agents.memo_to_task.schema import (
            MemoToTaskAgentOutput as OutputModel,
        )

        # 空入力は Clarify 継続を提案
        memo_content = getattr(memo, "content", "")
        if not str(memo_content).strip():
            return OutputModel(tasks=[], suggested_memo_status="clarify")

        if self._get_provider() == LLMProvider.FAKE:
            agent = self._get_agent()
            fake_output = agent.next_fake_response()
            if fake_output is not None:
                logger.debug(f"MemoToTaskApplicationService: returning fake output tasks={len(fake_output.tasks)}")
                return fake_output

        state: MemoToTaskState = {
            "memo": memo,
            "existing_tags": self._collect_existing_tag_names(),
            "current_datetime_iso": self._current_datetime_iso(),
        }
        self._apply_prompt_overrides(state)

        result = self._invoke_agent(state)
        if result is None:
            msg = "エージェント応答が None でした"
            self._log_error_and_raise(msg)

        if isinstance(result, AgentError):
            self._log_error_and_raise(f"エージェントがエラーを返しました: {result}")

        if isinstance(result, MemoToTaskResult):
            return OutputModel(
                tasks=list(result.tasks),
                suggested_memo_status=result.suggested_memo_status,
                requires_project=result.requires_project,
                project_plan=result.project_plan,
            )

        # ここには通常到達しない（AgentError か MemoToTaskResult のどちらか）
        msg_invalid = "エージェント応答の型が不正です"
        raise MemoToTaskServiceError(msg_invalid)

    def generate_tasks_from_memo(self, memo: MemoRead) -> list[TaskDraft]:
        """メモ本文からタスク案だけを抽出するヘルパー。"""
        output = self.clarify_memo(memo)
        return list(output.tasks)

    # Internal helpers --------------------------------------------------
    def _get_agent(self) -> MemoToTaskAgent:
        if self._agent is None:
            from agents.task_agents.memo_to_task.agent import MemoToTaskAgent

            self._agent = MemoToTaskAgent(provider=self._get_provider(), device=self._get_device())
        return self._agent

    def _invoke_agent(self, state: MemoToTaskState) -> MemoToTaskResult | AgentError:
        agent = self._get_agent()
        thread_id = str(uuid4())
        return agent.invoke(state, thread_id)

    # --- settings accessors -------------------------------------------
    def _get_provider(self) -> LLMProvider:
        """現在の LLM プロバイダを取得する（常に設定から）。"""
        from typing import cast

        settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
        return settings_app.get_agents_settings().provider

    def _get_device(self) -> str:
        """OPENVINO 用の実行デバイスを設定から取得する。"""
        from typing import cast

        settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
        runtime_cfg = settings_app.get_agents_settings().runtime
        raw_device = getattr(runtime_cfg, "device", None)
        if isinstance(raw_device, OpenVINODevice):
            return raw_device.value
        return str(raw_device or OpenVINODevice.CPU.value).upper()

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

    def _apply_prompt_overrides(self, state: MemoToTaskState) -> None:
        overrides = self._get_prompt_overrides()
        state["custom_instructions"] = overrides["custom_instructions"]
        state["detail_hint"] = overrides["detail_hint"]
        state["task_count_hint"] = overrides["task_count_hint"]
        state["recommended_task_count"] = overrides["recommended_task_count"]

    def get_prompt_overrides_snapshot(self) -> PromptOverrides:
        """アプリ設定に基づくプロンプト上書き値を取得する。"""
        overrides = self._get_prompt_overrides()
        return PromptOverrides(
            custom_instructions=str(overrides["custom_instructions"]),
            detail_hint=str(overrides["detail_hint"]),
            task_count_hint=str(overrides["task_count_hint"]),
            recommended_task_count=int(overrides["recommended_task_count"]),
        )

    def get_configured_provider(self) -> LLMProvider:
        """設定で指定された LLM プロバイダを返す。"""
        return self._get_provider()

    def get_configured_device(self) -> str:
        """設定で指定された推論デバイスを返す。"""
        return self._get_device()

    def _get_prompt_overrides(self) -> PromptOverrides:
        from typing import cast

        settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
        agents_settings = settings_app.get_agents_settings()
        prompt_cfg = getattr(agents_settings, "memo_to_task_prompt", None)
        if prompt_cfg is None:
            level_enum = AgentDetailLevel.BALANCED
            return {
                "custom_instructions": "",
                "detail_hint": self._detail_hint_from_level(level_enum),
                "task_count_hint": self._task_count_hint_from_level(level_enum),
                "recommended_task_count": self._recommended_task_count_from_level(level_enum),
            }

        custom_text = str(getattr(prompt_cfg, "custom_instructions", "") or "").strip()
        detail_level = getattr(prompt_cfg, "detail_level", AgentDetailLevel.BALANCED)
        try:
            level_enum = (
                detail_level if isinstance(detail_level, AgentDetailLevel) else AgentDetailLevel(str(detail_level))
            )
        except ValueError:
            level_enum = AgentDetailLevel.BALANCED
        return {
            "custom_instructions": custom_text,
            "detail_hint": self._detail_hint_from_level(level_enum),
            "task_count_hint": self._task_count_hint_from_level(level_enum),
            "recommended_task_count": self._recommended_task_count_from_level(level_enum),
        }

    @staticmethod
    def _detail_hint_from_level(level: AgentDetailLevel) -> str:
        if level == AgentDetailLevel.BRIEF:
            return "回答は要点のみを簡潔にまとめてください。"
        if level == AgentDetailLevel.DETAILED:
            return "背景や理由も含めて丁寧に説明してください。"
        return "バランスよく適度な詳細度で回答してください。"

    @staticmethod
    def _task_count_hint_from_level(level: AgentDetailLevel) -> str:
        fallback = TASK_COUNT_HINT_BY_LEVEL[AgentDetailLevel.BALANCED]
        return TASK_COUNT_HINT_BY_LEVEL.get(level, fallback)

    @staticmethod
    def _recommended_task_count_from_level(level: AgentDetailLevel) -> int:
        fallback = RECOMMENDED_TASK_COUNT_BY_LEVEL[AgentDetailLevel.BALANCED]
        return RECOMMENDED_TASK_COUNT_BY_LEVEL.get(level, fallback)


# 型ヒント用の前方宣言
if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from agents.task_agents.memo_to_task.state import MemoToTaskState
    from models import MemoRead

__all__ = [
    "MemoToTaskApplicationService",
    "MemoToTaskServiceError",
]
