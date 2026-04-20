# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../", editable = true }
# ///
"""データベースファイルを削除するスクリプト。"""

from loguru import logger

from config import DB_PATH
from logging_conf import setup_logger

setup_logger()


def remove_database() -> None:
    """データベースファイルを削除する関数。"""
    if DB_PATH.exists():
        DB_PATH.unlink()
        logger.info(f"データベースファイルを削除しました: {DB_PATH}")
    else:
        logger.warning(f"データベースファイルが存在しません: {DB_PATH}")


if __name__ == "__main__":
    remove_database()
