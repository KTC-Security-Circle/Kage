"""一言コメント Application Service

`logic.services.one_liner_service.OneLinerService` を Application Service 層へ移行した新版。

利用側は `OneLinerApplicationService.generate_one_liner(OneLinerContextQuery())` の
ように空のクエリ DTO を渡すだけで、自動的にタスク件数/ユーザー名などの
コンテキスト情報が収集され一言コメントが生成されます。

後方互換: 旧 `OneLinerService` はラッパーとして残し、本実装を継承します。
"""

from __future__ import annotations

from typing import NoReturn, cast

from loguru import logger

from agents.agent_conf import HuggingFaceModel, LLMProvider
from agents.task_agents.one_liner.agent import OneLinerAgent
from agents.task_agents.one_liner.state import OneLinerState
from logic.application.base import BaseApplicationService
from logic.queries.one_liner_queries import OneLinerContext

# 既存テスト互換のため MyBaseError を継承した同名エラーを維持
from logic.services.base import MyBaseError
from logic.unit_of_work import SqlModelUnitOfWork
from settings.manager import get_config_manager


class OneLinerServiceError(MyBaseError):
    """一言コメント生成時のカスタム例外クラス"""

    def __str__(self) -> str:  # pragma: no cover - フォーマットのみ
        return f"一言コメント生成エラー: {self.arg}"


class OneLinerApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """一言コメント生成 Application Service

    Task/設定情報を内部で収集し LLM Agent を直接呼び出します。
    """

    def __init__(
        self,
        unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork,
        *,
        provider: LLMProvider | None = None,
        model_name: HuggingFaceModel | str | None = None,
    ) -> None:
        super().__init__(unit_of_work_factory)

        cfg = get_config_manager().settings
        self._provider = provider if provider else cfg.agents.provider
        self._use_llm = True  # 常時 LLM 経路

        raw_model = None
        try:  # 設定から one_liner 用モデル名を取得
            raw_model = model_name if model_name else cfg.agents.get_model_name("one_liner")
        except Exception as e:  # pragma: no cover - 設定未整備時は黙って続行
            logger.debug(f"モデル名取得失敗(無視): {e}")

        resolved_model: HuggingFaceModel | str | None
        if self._provider == LLMProvider.OPENVINO and raw_model is not None:
            if isinstance(raw_model, HuggingFaceModel):
                resolved_model = raw_model
            elif isinstance(raw_model, str):
                msg = (
                    "OneLinerApplicationService: OPENVINO でモデル名が文字列として設定されています。"
                    "Enum 型で指定してください。"
                )
                self._log_error_and_raise(msg)
            else:  # pragma: no cover - 型ガード
                msg = f"OneLinerApplicationService: OPENVINO で不明な型のモデル名: {type(raw_model)}"
                self._log_error_and_raise(msg)
        elif self._provider == LLMProvider.GOOGLE:
            resolved_model = raw_model  # str 期待
        else:
            resolved_model = None

        self._model_name = resolved_model
        self._agent = OneLinerAgent(provider=self._provider, model_name=self._model_name)
        logger.debug(
            "OneLinerApplicationService initialized (provider=%s, model=%s)",
            self._provider.name,
            self._model_name,
        )

    # Public API ---------------------------------------------------------
    def generate_one_liner(self, query: OneLinerContext | None = None) -> str:
        """一言コメント生成 (空のクエリで自動集計)."""
        if query is not None:
            return self._generate_with_agent(query)
        try:
            ctx = self._build_context_auto()
            return self._generate_with_agent(ctx)
        except Exception as e:  # pragma: no cover - LLM 実行例外など
            logger.exception(f"一言コメント生成中にエラー: {e}")
            return self._get_default_message()

    # Internal helpers --------------------------------------------------
    def _build_context_auto(self) -> OneLinerContext:
        """タスク件数とユーザー名を取得し `OneLinerContext` を構築."""
        # 循環 import 回避のため遅延 import
        from logic.application.task_application_service import TaskApplicationService
        from logic.queries.task_queries import GetTodayTasksCountQuery

        task_app = TaskApplicationService(self._unit_of_work_factory)
        today = task_app.get_today_tasks_count(GetTodayTasksCountQuery())
        completed = task_app.get_completed_tasks_count()
        overdue = task_app.get_overdue_tasks_count()

        try:
            user_name = get_config_manager().settings.user.user_name or ""
        except Exception:  # pragma: no cover
            user_name = ""

        return OneLinerContext(
            today_task_count=today,
            completed_task_count=completed,
            overdue_task_count=overdue,
            progress_summary="",  # 未来拡張
            user_name=user_name,
        )

    def _generate_with_agent(self, context: OneLinerContext) -> str:
        logger.debug(f"Generating one-liner with context={context}")
        state = OneLinerState(
            today_task_count=context.today_task_count,
            completed_task_count=context.completed_task_count,
            overdue_task_count=context.overdue_task_count,
            progress_summary=context.progress_summary,
            user_name=context.user_name,
            final_response="",
        )
        thread_id = f"{context.today_task_count}-{context.completed_task_count}-{context.overdue_task_count}"
        result = self._agent.invoke(cast("OneLinerState", state), thread_id)
        if not result or not getattr(result, "response", ""):
            logger.warning("OneLinerAgent が期待する応答を返しませんでした。デフォルトに置換します。")
            return self._get_default_message()
        return cast("str", result.response)  # type: ignore[attr-defined]

    def _get_default_message(self) -> str:
        return "今日も一日、お疲れさまです。"

    def _log_error_and_raise(self, msg: str) -> NoReturn:
        logger.error(msg)
        raise OneLinerServiceError(msg)


__all__ = [
    "OneLinerApplicationService",
    "OneLinerServiceError",
    "OneLinerContext",
]
