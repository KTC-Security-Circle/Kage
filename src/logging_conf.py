import sys
from pathlib import Path

from loguru import logger

from config import LOG_DIR


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
        f"{LOG_DIR}/app.log",  # ファイルにログを出力
        rotation="10 MB",  # ログファイルのローテーション設定
        retention="30 days",  # ログファイルの保持期間
        level="DEBUG",  # ファイルにはDEBUGレベル以上のログを出力
        enqueue=True,
    )

    logger.debug("ロガーの設定が完了しました。")


def check_log_dir() -> None:
    """ログディレクトリの存在を確認し、なければ作成する関数。

    ログディレクトリが存在しない場合は作成し、ログ出力の準備を整える。

    Example:
    ```python
    log_dir_path = Path(LOG_DIR)  # ログディレクトリのパスを変数に格納

    if not log_dir_path.exists():
        log_dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ログディレクトリ '{LOG_DIR}' を作成しました。")
    ```

    Returns:
        None: 何も返しません。
    """
    log_dir_path = Path(LOG_DIR)  # ログディレクトリのパスを変数に格納

    if not log_dir_path.exists():
        log_dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"ログディレクトリ '{LOG_DIR}' を作成しました。")
