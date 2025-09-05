"""agentで使用する設定を定義するモジュール"""

from enum import Enum

from config import STORAGE_DIR


class LLMProvider(Enum):
    """利用可能な言語モデルプロバイダを指定するLLMProvider列挙型。

    Attributes:
        FAKE (str): AIを使用しない場合とテスト用のダミープロバイダ
        GOOGLE (str): Googleの言語モデルサービスに対応するプロバイダ
        HUGGINGFACE (str): Hugging Faceの言語モデルサービスに対応するプロバイダ

    Note:
        各プロバイダは、対応するAPIやサービスを利用して言語モデルを提供するための設定や認証情報が必要です。
        具体的な実装は、各プロバイダに対応するクラスやモジュールで行われます。
        追加のプロバイダをサポートする場合は、この列挙型に新しいメンバーを追加し、対応する実装を提供してください。
    """

    FAKE = "fake"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"


SQLITE_DB_PATH = f"{STORAGE_DIR}/agents.db"
