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
    OPENVINO = "openvino"


class HuggingFaceModel(Enum):
    """Hugging Faceで利用可能なモデルタイプを指定するHuggingFaceModelType列挙型。

    Attributes:
        QWEN_3_8B_INT4 (str): Qwen3-8Bモデル（INT4量子化）
        MISTRAL_7B_INS_V03_INT4 (str): Mistral-7Bモデル（INT4量子化）

    Note:
        各モデルは、Hugging Faceのモデルリポジトリから取得され、対応するタスクに使用されます。
        追加のモデルをサポートする場合は、この列挙型に新しいメンバーを追加し、対応する実装を提供してください。
        この列挙型にあるモデルは必ず動くことを保証するものではありません。
    """

    QWEN_3_8B_INT4 = "OpenVINO/Qwen3-8B-int4-cw-ov"
    MISTRAL_7B_INS_V03_INT4 = "OpenVINO/Mistral-7B-Instruct-v0.3-int4-cw-ov"


class OpenVINODevice(Enum):
    """OpenVINO モデルの実行先デバイス。"""

    AUTO = "AUTO"
    CPU = "CPU"
    GPU = "GPU"
    NPU = "NPU"


SQLITE_DB_PATH = f"{STORAGE_DIR}/agents.db"
LLM_MODEL_DIR = f"{STORAGE_DIR}/llms"
