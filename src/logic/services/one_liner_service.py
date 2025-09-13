"""一言コメント生成サービス

ロジック層アダプタ (`OneLinerLogicAgent`) を廃止し、本サービスが直接
`OneLinerAgent` を呼び出して一言コメントを生成する最小構成。
失敗時は固定メッセージを返すのみで、旧フォールバック分岐は削除。
"""

from typing import NoReturn, cast

from loguru import logger

from agents.agent_conf import HuggingFaceModel, LLMProvider
from agents.task_agents.one_liner.agent import OneLinerAgent
from agents.task_agents.one_liner.state import OneLinerState
from logic.queries.one_liner_queries import OneLinerContext
from logic.services.base import MyBaseError, ServiceBase
from settings.manager import get_config_manager


class OneLinerServiceError(MyBaseError):
    """一言コメント生成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"一言コメント生成エラー: {self.arg}"


class OneLinerService(ServiceBase[OneLinerServiceError]):
    """一言コメント生成サービス (OneLinerAgent 直接利用)."""

    def __init__(self) -> None:
        cfg = get_config_manager().settings
        provider = cfg.agents.provider
        self._use_llm = True  # 旧テスト互換フラグ (常に True)

        raw_model = None
        try:
            raw_model = cfg.agents.get_model_name("one_liner")  # HuggingFaceModel | str | None
        except Exception as e:
            logger.debug(f"モデル名取得失敗(無視): {e}")

        # OPENVINO(HuggingFaceModel) の場合は Enum、Gemini は str、それ以外 None
        if provider == LLMProvider.OPENVINO and raw_model is not None:
            if isinstance(raw_model, HuggingFaceModel):
                model_name = raw_model
            elif isinstance(raw_model, str):
                # 型安全性のため、OPENVINO で文字列モデル名は許容しない
                err_msg = (
                    "OneLinerService: OPENVINO でモデル名が文字列として設定されています。Enum 型で指定してください。"
                )
                raise OneLinerServiceError(err_msg)
            else:
                err_msg = f"OneLinerService: OPENVINO で不明な型のモデル名が設定されています: {type(raw_model)}"
                raise OneLinerServiceError(err_msg)
        elif provider == LLMProvider.GOOGLE:
            model_name = raw_model
        else:
            model_name = None

        self._agent = OneLinerAgent(provider=provider, model_name=model_name)
        logger.debug(
            f"OneLinerService initialized (LLM flag env={self._use_llm}, provider={provider.name}, model={model_name})"
        )

    def generate(self, context: OneLinerContext) -> str:
        try:
            return self._generate_with_agent(context)
        except Exception as e:
            logger.exception(f"一言コメント生成中にエラーが発生しました: {e}")
            return self._get_default_message()

    def _generate_with_agent(self, context: OneLinerContext) -> str:
        logger.debug(f"Generating agent-based comment for context: {context}")
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
        super()._log_error_and_raise(msg, OneLinerServiceError)
