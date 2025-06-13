import sys

from loguru import logger

from config import DB_DIR


def setup_logger() -> None:
    """ロガーの設定を行う関数。

    ログのフォーマットや出力先を設定する。
    """
    logger.remove()  # 既存のハンドラを削除

    logger.add(
        sys.stderr,  # 標準エラー出力にログを出力
        level="DEBUG",
        enqueue=True,
    )

    logger.add(
        f"{DB_DIR}/logs/app.log",  # ファイルにログを出力
        rotation="10 MB",  # ログファイルのローテーション設定
        retention="30 days",  # ログファイルの保持期間
        level="DEBUG",  # ファイルにはDEBUGレベル以上のログを出力
        enqueue=True,
    )

    logger.debug("ロガーの設定が完了しました。")
