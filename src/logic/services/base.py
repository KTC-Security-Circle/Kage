"""サービスの基底クラスとカスタム例外の定義

このモジュールは、サービスの基底クラスとカスタム例外を定義します。
サービスはビジネスロジックを実装するためのクラスで、リポジトリを利用してデータ操作を行います。
"""

from typing import NoReturn

from loguru import logger


class MyBaseError(Exception):
    """カスタム例外クラス"""

    def __init__(self, arg: str = "") -> None:
        self.arg = arg


class ServiceBase[T: MyBaseError]:
    """サービスの基底クラス

    サービスはビジネスロジックを実装するためのクラスで、リポジトリを利用してデータ操作を行います。
    依存性注入により必要なリポジトリを受け取ります。
    """

    def _log_error_and_raise(self, msg: str, exception_class: type[T]) -> NoReturn:
        """エラーメッセージをログに記録し `MyBaseError` を発生させる

        Args:
            msg (str): エラーメッセージ
            exception_class (type[T]): 発生させる例外のクラス

        Raises:
            MyBaseError: カスタム例外
        """
        logger.error(msg)
        raise exception_class(msg)
