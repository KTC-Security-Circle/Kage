"""一言コメント Application Service

`logic.services.one_liner_service.OneLinerService` を Application Service 層へ移行した新版。

利用側は `OneLinerApplicationService.generate_one_liner(OneLinerContextQuery())` の
ように空のクエリ DTO を渡すだけで、自動的にタスク件数/ユーザー名などの
コンテキスト情報が収集され一言コメントが生成されます。

後方互換: 旧 `OneLinerService` はラッパーとして残し、本実装を継承します。
"""

from __future__ import annotations

from typing import Any, NoReturn, cast, override
from uuid import uuid4

from loguru import logger

from agents.agent_conf import HuggingFaceModel, LLMProvider
from agents.task_agents.one_liner.agent import OneLinerAgent
from agents.task_agents.one_liner.state import OneLinerState
from errors import ApplicationError
from logic.application import BaseApplicationService
from logic.application.settings_application_service import SettingsApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.unit_of_work import SqlModelUnitOfWork
from models import TaskStatus


class OneLinerServiceError(ApplicationError):
    """一言コメント生成時のカスタム例外クラス"""

    def __init__(self, message: str) -> None:
        super().__init__(f"一言コメント生成エラー: {message}")


class OneLinerApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """一言コメント生成 Application Service

    Task/設定情報を内部で収集し LLM Agent を直接呼び出します。
    """

    def __init__(
        self,
        unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork,
        *,
        model_name: HuggingFaceModel | str | None = None,
    ) -> None:
        super().__init__(unit_of_work_factory)
        from typing import cast

        settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
        agents_cfg = settings_app.get_agents_settings()
        self._provider = agents_cfg.provider
        self._use_llm = True  # 常時 LLM 経路

        raw_model = None
        try:  # 設定から one_liner 用モデル名を取得
            raw_model = model_name if model_name else agents_cfg.get_model_name("one_liner")
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

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> OneLinerApplicationService: ...

    # Public API ---------------------------------------------------------
    def generate_one_liner(self, query: OneLinerState | None = None) -> str:
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
    def _build_context_auto(self) -> OneLinerState:
        """タスク件数とユーザー名を取得し `OneLinerContext` を構築."""
        from logic.application.apps import ApplicationServices

        apps = ApplicationServices.create()
        task_app = apps.get_service(TaskApplicationService)

        try:
            settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
            user_name = settings_app.get_user_settings().user_name or ""
        except Exception:  # pragma: no cover
            user_name = ""

        return OneLinerState(
            today_task_count=len(task_app.list_by_status(TaskStatus.TODAYS)),
            completed_task_count=len(task_app.list_by_status(TaskStatus.COMPLETED)),
            overdue_task_count=len(task_app.list_by_status(TaskStatus.OVERDUE)),
            progress_summary="",  # 未使用
            user_name=user_name,
        )

    def _generate_with_agent(
        self,
        state: OneLinerState,
    ) -> str:
        thread_id = str(uuid4())
        result = self._agent.invoke(cast("OneLinerState", state), thread_id)
        from agents.base import AgentError

        if isinstance(result, AgentError) or not getattr(result, "response", ""):
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
]
