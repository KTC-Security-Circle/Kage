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

    check_log_dir()  # ログディレクトリの存在を確認し、なければ作成

    logger.add(
        f"{LOG_DIR}/app.log",  # ファイルにログを出力
        rotation="10 MB",  # ログファイルのローテーション設定
        retention="30 days",  # ログファイルの保持期間
        level="DEBUG",  # ファイルにはDEBUGレベル以上のログを出力
        enqueue=True,
    )

    # ai用ログの設定
    logger.add(
        f"{LOG_DIR}/agents.log",  # AI関連のログを別ファイルに出力
        filter=lambda record: "agents" in record["extra"],  # "agents"が含まれるログのみ出力
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        enqueue=True,
    )

    logger.debug("ロガーの設定が完了しました。")


class AgentLogger:
    """エージェント用のロガークラス。

    エージェント関連のログを出力するためのクラス。
    """

    def __init__(self) -> None:
        """初期化メソッド。"""

    @staticmethod
    def _log(msg: str, level: str) -> None:
        """ログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
            level (str): ログレベル。
        """
        logger.bind(agents=True).log(level, msg)

    @staticmethod
    def debug(msg: str) -> None:
        """DEBUGレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "DEBUG")

    @staticmethod
    def info(msg: str) -> None:
        """INFOレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "INFO")

    @staticmethod
    def success(msg: str) -> None:
        """SUCCESSレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "SUCCESS")

    @staticmethod
    def warning(msg: str) -> None:
        """WARNINGレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "WARNING")

    @staticmethod
    def error(msg: str) -> None:
        """ERRORレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "ERROR")

    @staticmethod
    def critical(msg: str) -> None:
        """CRITICALレベルのログを出力するメソッド。

        Args:
            msg (str): ログメッセージ。
        """
        AgentLogger._log(msg, "CRITICAL")


agent_logger = AgentLogger()  # エージェント用のロガーインスタンスを作成


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
