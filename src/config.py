"""アプリケーション全体で使用する定数や設定値を定義するモジュール。"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlmodel import SQLModel

# データベース保存先ディレクトリ（環境変数がなければFlet指定のstorageフォルダ）
STORAGE_DIR: str = os.environ.get("FLET_APP_STORAGE_DATA", "./storage/data")
# データベースファイルのパス
DB_PATH: Path = Path(STORAGE_DIR) / "tasks.db"
# データベースエンジンの作成
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


# アプリケーション起動時にテーブルを作成するための関数
def create_db_and_tables() -> None:
    """アプリケーション起動時にテーブルを作成するための関数"""
    # この関数は main.py の最初で一度だけ呼び出す
    from sqlmodel import SQLModel

    # from models import __all__  # これで全てのモデルがインポートされる noqa: F401
    import models  # noqa: F401  # メタデータ登録のため副作用インポート

    SQLModel.metadata.create_all(engine)


# SQLModelの基礎クラスを使用
Base = SQLModel

# アプリケーションのタイトル
APP_TITLE: str = "Kage"

# タスク用の定数
TASK_TITLE_MAX_LENGTH = 100
TASK_DESCRIPTION_MAX_LENGTH = 500
DESCRIPTION_TRUNCATE_LENGTH = 50

# loguru
LOG_DIR: str = f"{STORAGE_DIR}/logs"

CONFIG_PATH: Path = Path(STORAGE_DIR) / "app_config.yaml"
