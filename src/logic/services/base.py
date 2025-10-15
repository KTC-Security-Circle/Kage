"""サービスの基底クラスとカスタム例外の定義

このモジュールは、サービスの基底クラスとカスタム例外を定義します。
サービスはビジネスロジックを実装するためのクラスで、リポジトリを利用してデータ操作を行います。
"""

import functools
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any, Literal, ParamSpec, Self, TypeVar, overload

from loguru import logger

from errors import NotFoundError, RepositoryError
from models import BaseModel


class MyBaseError(Exception):
    """カスタム例外クラス"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:
        self.message = message
        self.operation = operation


class ServiceError(MyBaseError):
    """サービス層で発生する汎用的なエラー"""

    def __str__(self) -> str:
        return f"{self.operation}処理でエラーが発生しました: {self.message}"


class ModelConversionError(TypeError):
    """モデル変換時に予期しない型が返された場合のエラー"""

    def __str__(self) -> str:
        return "モデル変換エラー: 予期しない型が返されました"


_P = ParamSpec("_P")
_R_In = TypeVar("_R_In")
_ErrorType = TypeVar("_ErrorType", bound=MyBaseError)
_ReadModelType = TypeVar("_ReadModelType", bound=BaseModel)


def handle_service_errors(
    service_name: str, operation: str, error_cls: type[_ErrorType] = ServiceError
) -> Callable[[Callable[_P, _R_In]], Callable[_P, _R_In]]:
    def decorator(func: Callable[_P, _R_In]) -> Callable[_P, _R_In]:
        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R_In:
            try:
                return func(*args, **kwargs)

            except NotFoundError:
                # ドメイン相当の条件不一致はそのまま透過（UI/CLIで情報表示する想定）
                raise
            except RepositoryError as e:
                # インフラ失敗はサービス層で抽象化
                msg = f"<{service_name}> {operation}処理でリポジトリエラーが発生しました: {e}"
                logger.debug(msg)
                raise error_cls(message=msg, operation=operation) from e
            except Exception as e:
                msg = f"<{service_name}> {operation}処理で予期しないエラーが発生しました: {e}"
                logger.exception(msg)
                raise error_cls(message=msg, operation=operation) from e

        return wrapper

    return decorator


@overload
def convert_read_model(
    to_model: type[_ReadModelType], *, is_list: Literal[False] = False
) -> Callable[[Callable[_P, BaseModel]], Callable[_P, _ReadModelType]]: ...


@overload
def convert_read_model(
    to_model: type[_ReadModelType], *, is_list: Literal[True]
) -> Callable[[Callable[_P, Sequence[BaseModel]]], Callable[_P, list[_ReadModelType]]]: ...


def convert_read_model(
    to_model: type[_ReadModelType], *, is_list: bool = False
) -> Callable[[Callable[_P, Any]], Callable[_P, Any]]:
    """読み取りモデルへの変換デコレータを生成する

    単一の BaseModel または BaseModel のシーケンス（list/tuple 等）を
    指定の読み取りモデル型に変換して返す。

    Args:
        to_model: model_validate を持つ読み取り用モデルの型
        is_list: シーケンスとして扱うかどうか（デフォルトは False）

    Returns:
        変換を行うデコレータ
    """

    def decorator(
        func: Callable[_P, Any],
    ) -> Callable[_P, Any]:
        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Any:  # noqa: ANN401
            result = func(*args, **kwargs)

            # [AI GENERATED] シーケンス（list/tuple 等）の場合
            if is_list:
                if isinstance(result, Sequence) and not isinstance(result, (str, bytes, bytearray)):
                    if all(isinstance(item, BaseModel) for item in result):
                        return [to_model.model_validate(item) for item in result]
                    raise ModelConversionError
                raise ModelConversionError
            # [AI GENERATED] 単一モデルの場合
            if isinstance(result, BaseModel):
                return to_model.model_validate(result)
            raise ModelConversionError

        return wrapper

    return decorator


class ServiceBase(ABC):
    """サービスの基底クラス

    サービスはビジネスロジックを実装するためのクラスで、リポジトリを利用してデータ操作を行います。
    依存性注入により必要なリポジトリを受け取ります。
    """

    @classmethod
    @abstractmethod
    def build_service(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ANN401
        """サービスのインスタンスを生成するファクトリメソッド

        Args:
            *args: 任意の位置引数
            **kwargs: 任意のキーワード引数

        Returns:
            ServiceBase: サービスのインスタンス
        """
        msg = "Subclasses must implement build_service method"
        raise NotImplementedError(msg)

    @classmethod
    def get_service_name(cls) -> str:
        """サービス名を取得する

        Returns:
            str: サービス名
        """
        return cls.__name__
