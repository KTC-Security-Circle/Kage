"""アプリケーション全体で使用する定数や設定値を定義するモジュール。"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlmodel import SQLModel

# データベース保存先ディレクトリ（環境変数がなければFlet指定のstorageフォルダ）
DB_DIR: str = os.environ.get("FLET_APP_STORAGE_DATA", "./storage/data")
# データベースファイルのパス
DB_PATH: Path = Path(DB_DIR) / "tasks.db"
# データベースエンジンの作成
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# SQLModelの基礎クラスを使用
Base = SQLModel

# アプリケーションのタイトル
APP_TITLE: str = "タスク管理アプリ"

# タスク用の定数
TASK_TITLE_MAX_LENGTH = 100
TASK_DESCRIPTION_MAX_LENGTH = 500
DESCRIPTION_TRUNCATE_LENGTH = 50

# loguru
LOG_DIR: str = f"{DB_DIR}/logs"
