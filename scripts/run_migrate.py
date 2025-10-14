# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../", editable = true }
# ///
"""データベースのマイグレーションを実行するスクリプト。

実行手順:
    # workspace ルートで実行
    uv run scripts/run_migrate.py
"""

from config import migrate_db
from logging_conf import setup_logger

if __name__ == "__main__":
    setup_logger()
    migrate_db()
