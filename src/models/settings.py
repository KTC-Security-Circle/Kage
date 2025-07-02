import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlmodel import SQLModel

# データベース保存先ディレクトリ（環境変数がなければsrc/modelsから見た相対パス）
DB_DIR: str = os.environ.get("FLET_APP_STORAGE_DATA", "../../storage/data")

# データベースファイルのパス
DB_PATH: Path = Path(DB_DIR) / "tasks.db"

# データベースディレクトリが存在しない場合は作成
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLiteのデータベースURL
DATABASE_URL: str = f"sqlite:///{DB_PATH}"

# Engine の作成
Engine = create_engine(DATABASE_URL, echo=False)

# SQLModelの基底クラスを使用（SQLAlchemyとの互換性を保持）
Base = SQLModel
