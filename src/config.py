"""アプリケーション全体で使用する定数や設定値を定義するモジュール。"""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel

# データベース保存先ディレクトリ（環境変数がなければFlet指定のstorageフォルダ）
STORAGE_DIR: str = os.environ.get("FLET_APP_STORAGE_DATA", "./storage/data")
# データベースファイルのパス
DB_PATH: Path = Path(STORAGE_DIR) / "tasks.db"
# データベースエンジンの作成
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


# Alembicの設定ファイルのパス
ALEMBIC_INI_PATH = Path(__file__).parent / "models" / "migrations" / "alembic.ini"
alembic_cfg = Config(ALEMBIC_INI_PATH)
Base = SQLModel


# Alembicを使用してデータベースを最新の状態にマイグレーションする関数
def migrate_db() -> None:
    # alembicを介してマイグレーションを実行
    logger.info("Migrating database...")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrated to the latest version.")


# アプリケーションのタイトル
APP_TITLE: str = "Kage"

# タスク用の定数
TASK_TITLE_MAX_LENGTH = 100
TASK_DESCRIPTION_MAX_LENGTH = 500
DESCRIPTION_TRUNCATE_LENGTH = 50

# loguru
LOG_DIR: str = f"{STORAGE_DIR}/logs"

CONFIG_PATH: Path = Path(STORAGE_DIR) / "app_config.yaml"
