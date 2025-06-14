"""agentで使用する設定を定義するモジュール"""

from enum import Enum

from config import DB_DIR


class LLMProvider(Enum):
    """LLMプロバイダのEnum"""

    GOOGLE = "google"
    HUGGINGFACE = "huggingface"


SQLITE_DB_PATH = f"{DB_DIR}/agents.db"
