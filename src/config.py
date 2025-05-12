"""アプリケーション全体で使用する定数や設定値を定義するモジュール。"""

import os
from pathlib import Path

from sqlmodel import create_engine

# データベース保存先ディレクトリ（環境変数がなければカレントディレクトリ）
DB_DIR: str = os.environ.get("FLET_APP_STORAGE_DATA", ".")
# データベースファイルのパス
DB_PATH: Path = Path(DB_DIR) / "tasks.db"
# データベースエンジンの作成
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


# アプリケーションのタイトル
APP_TITLE: str = "タスク管理アプリ"
