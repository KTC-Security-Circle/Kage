import os
import sqlite3

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from loguru import logger

from agents.agent_conf import SQLITE_DB_PATH, LLMProvider


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


def get_model(provider: LLMProvider, model: str = "") -> BaseChatModel:
    """指定されたプロバイダに基づいてLLMを取得する関数。

    Args:
        provider (LLMProvider): 使用するLLMプロバイダ。
        model (str, optional): 使用するモデル名。デフォルトは空文字列。

    Raises:
        NotImplementedError: 指定されたプロバイダがサポートされていない場合に発生します。

    Returns:
        BaseChatModel: 取得したLLMモデル。
    """
    if provider == LLMProvider.GOOGLE:
        if "GOOGLE_API_KEY" not in os.environ:
            err_msg = "GOOGLE_API_KEY is not set in environment variables."
            logger.bind(agents=True).error(err_msg)
            raise OSError(err_msg)

        gemini_model = model if model else "gemini-2.0-flash"
        llm = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=0.2,
            max_retries=3,
        )
    elif provider == LLMProvider.HUGGINGFACE:
        err_msg = "Hugging Face LLM is not implemented yet."
        logger.bind(agents=True).error(err_msg)
        raise NotImplementedError(err_msg)
    elif provider == LLMProvider.FAKE:
        responses = [
            "これはテスト用のダミー応答です。",
            "AIを使用しない場合の応答です。",
        ]
        llm = FakeListChatModel(responses=responses)
    else:
        err_msg = f"Unsupported LLM provider: {provider}"
        logger.bind(agents=True).error(err_msg)
        raise NotImplementedError(err_msg)

    return llm
