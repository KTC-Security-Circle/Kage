"""一言コメント Application Service

`logic.services.one_liner_service.OneLinerService` を Application Service 層へ移行した新版。

利用側は `OneLinerApplicationService.generate_one_liner(OneLinerContextQuery())` の
ように空のクエリ DTO を渡すだけで、自動的にタスク件数/ユーザー名などの
コンテキスト情報が収集され一言コメントが生成されます。

後方互換: 旧 `OneLinerService` はラッパーとして残し、本実装を継承します。
"""

from __future__ import annotations

import datetime
from typing import Any, NoReturn, cast, override
from uuid import uuid4

from loguru import logger

from agents.agent_conf import HuggingFaceModel, LLMProvider, OpenVINODevice
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

    Note:
        キャッシュはクラスレベルで共有され、全インスタンス間で再利用されます。
        これにより、ホーム画面を開くたびにAIメッセージが再生成されることを防ぎます。
    """

    # クラスレベルのキャッシュ（全インスタンス共有）
    cached_message: str | None = None
    cached_at: datetime.datetime | None = None
    cache_ttl = datetime.timedelta(hours=1)  # デフォルト1時間

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
        runtime_cfg = getattr(agents_cfg, "runtime", None)
        raw_device = getattr(runtime_cfg, "device", None)
        if isinstance(raw_device, OpenVINODevice):
            self._device = raw_device.value
        else:
            self._device = str(raw_device or OpenVINODevice.CPU.value).upper()

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
        self._agent = OneLinerAgent(provider=self._provider, model_name=self._model_name, device=self._device)
        logger.debug(
            "OneLinerApplicationService initialized (provider=%s, model=%s)",
            self._provider.name,
            self._model_name,
        )

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> OneLinerApplicationService: ...

    # Public API ---------------------------------------------------------
    def generate_one_liner(self, query: OneLinerState | None = None, *, force_refresh: bool = False) -> str:
        """一言コメント生成 (空のクエリで自動集計).

        Args:
            query: コンテキスト情報（Noneの場合は自動収集）
            force_refresh: Trueの場合はキャッシュを無視して強制再生成

        Returns:
            生成されたメッセージ
        """
        if query is not None:
            message, _ = self._generate_with_agent(query)
            return message

        # 強制リフレッシュでない場合はキャッシュをチェック
        if not force_refresh:
            cached_message = self._get_cached_message()
            if cached_message is not None:
                return cached_message

        try:
            logger.info("[OneLiner] 新規メッセージ生成開始")
            ctx = self._build_context_auto()
            message, should_cache = self._generate_with_agent(ctx)
            if should_cache:
                self._update_cache(message)
            else:
                self._clear_cache()
        except Exception as e:  # pragma: no cover - LLM 実行例外など
            logger.exception(f"一言コメント生成中にエラー: {e}")
            self._clear_cache()
            return self._get_default_message()
        return message

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
    ) -> tuple[str, bool]:
        thread_id = str(uuid4())
        result = self._agent.invoke(cast("OneLinerState", state), thread_id)
        from agents.base import AgentError

        if isinstance(result, AgentError) or not getattr(result, "response", ""):
            logger.warning("OneLinerAgent が期待する応答を返しませんでした。デフォルトに置換します。")
            return self._get_default_message(), False
        return result.response, True

    def _get_default_message(self) -> str:
        return "今日も一日、お疲れさまです。"

    def _log_error_and_raise(self, msg: str) -> NoReturn:
        logger.error(msg)
        raise OneLinerServiceError(msg)

    def _get_cached_message(self) -> str | None:
        """キャッシュされたメッセージを取得する（有効期限チェック付き）。

        Returns:
            有効なキャッシュがあればメッセージ、なければNone
        """
        if self.__class__.cached_message is None or self.__class__.cached_at is None:
            logger.debug("[OneLiner] キャッシュが空です")
            return None
        if self.__class__.cached_at + self.__class__.cache_ttl <= self._now():
            logger.info("[OneLiner] キャッシュ期限切れ（TTL: 1時間）")
            self._clear_cache()
            return None
        logger.info(f"[OneLiner] キャッシュヒット（生成時刻: {self.__class__.cached_at}）")
        return self.__class__.cached_message

    def _update_cache(self, message: str) -> None:
        """キャッシュを更新する。

        Args:
            message: キャッシュするメッセージ
        """
        self.__class__.cached_message = message
        self.__class__.cached_at = self._now()
        logger.info(f"[OneLiner] キャッシュ更新（有効期限: {self.__class__.cached_at + self.__class__.cache_ttl}）")

    def _clear_cache(self) -> None:
        """キャッシュをクリアする。"""
        self.__class__.cached_message = None
        self.__class__.cached_at = None
        logger.debug("[OneLiner] キャッシュクリア")

    def _now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)


__all__ = [
    "OneLinerApplicationService",
    "OneLinerServiceError",
]
