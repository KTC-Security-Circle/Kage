import json
import os
import sqlite3
from collections.abc import Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openvino_genai import ChatOpenVINO, OpenVINOLLM, load_model
from langgraph.checkpoint.sqlite import SqliteSaver
from loguru import logger
from pydantic import BaseModel

from agents.agent_conf import LLM_MODEL_DIR, SQLITE_DB_PATH, HuggingFaceModel, LLMProvider

agents_logger = logger.bind(agents=True)


def get_sqlite_conn() -> sqlite3.Connection:
    """SQLiteデータベースへの接続を取得する関数。

    Returns:
        sqlite3.Connection: SQLiteデータベースへの接続オブジェクト。
    """
    return sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)


def get_memory() -> SqliteSaver:
    """メモリ用のSQLiteセーバーを取得する関数。

    Returns:
        SqliteSaver: メモリ用のSQLiteセーバーオブジェクト。
    """
    return SqliteSaver(get_sqlite_conn())


class FakeListChatModelWithBindTools(FakeListChatModel):
    """FakeListChatModel に最小限の tool binding 互換層を与える拡張。

    with_structured_output() が内部で bind_tools() を呼ぶ際、
    BaseChatModel の NotImplementedError を避けるためにスタブ実装を提供する。

    振る舞い:
        - bind_tools(tools=[PydanticModel]) 呼び出し時に *新しい* ラッパーモデルを返す。
        - ラッパーの invoke() は事前に用意された responses から 1 件取り出し、
          それを JSON としてパースできれば tool_calls[0]['args'] に格納した AIMessage を返す。
        - JSON でなければ空 dict を args として返す（パーサ側でバリデーション失敗→フォールバック判定可能）。

    制約:
        - ツール強制選択 (tool_choice) / 複数ツール選択ロジックは未対応（最初のツールのみ）。
        - ストリーミングは未対応（必要になれば AIMessageChunk 実装を追加）。
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._response_index: int = 0  # internal pointer

    def next_raw_response(self) -> str:
        if self._response_index < len(self.responses):
            raw = self.responses[self._response_index]
            self._response_index += 1
            return raw
        return ""

    def bind_tools(
        self,
        tools: Sequence[object],
        *,
        tool_choice: object | None = None,
        **_unused: object,
    ) -> "FakeListChatModelWithBindTools":
        from langchain_core.messages import AIMessage

        parent = self

        class _BoundFakeListChatModel(FakeListChatModelWithBindTools):
            """bind_tools 後に返す軽量ラッパー。

            invoke() 毎に parent 側の responses 進行度を共有し、AIMessage を生成。
            """

            def __init__(self) -> None:
                self._parent = parent
                self._bound_tools = list(tools)
                self._tool_choice = tool_choice

            def invoke(self, _input: object, *_a: object, **_k: object) -> AIMessage:
                raw = self._parent.next_raw_response()
                try:
                    parsed_args = json.loads(raw) if raw else {}
                    if not isinstance(parsed_args, dict):
                        parsed_args = {"value": parsed_args}
                except Exception:
                    parsed_args = {}
                tool = self._bound_tools[0] if self._bound_tools else None
                name = getattr(tool, "__name__", getattr(tool, "name", "Tool")) if tool else "Tool"
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": name,
                            "args": parsed_args,
                            "id": "fake_tool_call_1",
                        }
                    ],
                )

        return _BoundFakeListChatModel()


def get_model(
    provider: LLMProvider,
    model_name: HuggingFaceModel | str | None = None,
    fake_responses: list[BaseModel] | None = None,
) -> BaseChatModel:
    """指定されたプロバイダに基づいてLLMを取得する関数。

    Args:
        provider (LLMProvider): 使用するLLMプロバイダ。
        model_name (str | None): 使用するモデルの名前。デフォルトはNone。
        fake_responses (list[BaseModel] | None): FAKEプロバイダ用のダミー応答リスト。デフォルトはNone。

    Raises:
        NotImplementedError: 指定されたプロバイダがサポートされていない場合に発生します。

    Returns:
        BaseChatModel: 取得したLLMモデル。
    """
    if provider == LLMProvider.GOOGLE:
        if "GOOGLE_API_KEY" not in os.environ:
            err_msg = "GOOGLE_API_KEY is not set in environment variables."
            agents_logger.error(err_msg)
            raise OSError(err_msg)

        gemini_model = model_name if model_name else "gemini-2.0-flash"
        llm = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=0.2,
            max_retries=3,
        )
    elif provider == LLMProvider.OPENVINO:
        if model_name is None:
            warning_msg = "Model name is not specified. Using default model."
            agents_logger.warning(warning_msg)
            model_name = HuggingFaceModel.QWEN_3_8B_INT4

        if not isinstance(model_name, HuggingFaceModel):
            err_msg = f"Invalid model name for OPENVINO provider: {model_name}. Must be a HuggingFaceModel enum."
            agents_logger.error(err_msg)
            raise ValueError(err_msg)

        # モデルのロード
        model_path = load_model(
            model_name.value,
            download_path=LLM_MODEL_DIR,
        )
        ov_llm = OpenVINOLLM.from_model_path(
            model_path=model_path,
            device="CPU",
        )
        llm = ChatOpenVINO(llm=ov_llm)
    elif provider == LLMProvider.FAKE:
        # FAKEプロバイダ用のダミー応答を設定
        # もし指定されていない場合はデフォルトの応答を使用
        responses = (
            [resp.model_dump_json() for resp in fake_responses]  # PydanticモデルのリストをJSON文字列に変換
            if fake_responses
            else [
                "これはテスト用のダミー応答です。",
                "AIを使用しない場合の応答です。",
            ]
        )
        llm = FakeListChatModelWithBindTools(responses=responses)
    else:
        err_msg = f"Unsupported LLM provider: {provider}"
        agents_logger.error(err_msg)
        raise NotImplementedError(err_msg)

    return llm
