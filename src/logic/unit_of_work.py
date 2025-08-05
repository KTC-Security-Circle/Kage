"""Unit of Workパターンの実装

トランザクション境界を管理し、複数のリポジトリ操作を一つの作業単位として扱います。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Self

from sqlmodel import Session

from config import engine
from logic.factory import RepositoryFactory, ServiceFactory

if TYPE_CHECKING:
    from collections.abc import Generator
    from types import TracebackType


class UnitOfWork(ABC):
    """Unit of Workパターンの抽象基底クラス

    トランザクション境界を管理し、複数のリポジトリ操作を
    一つの作業単位として扱うためのインターフェース。
    """

    @abstractmethod
    def __enter__(self) -> Self:
        """コンテキストマネージャーの開始"""

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """コンテキストマネージャーの終了"""

    @abstractmethod
    def commit(self) -> None:
        """変更をコミット"""

    @abstractmethod
    def rollback(self) -> None:
        """変更をロールバック"""

    @property
    @abstractmethod
    def service_factory(self) -> ServiceFactory:
        """サービスファクトリを取得"""

    @contextmanager
    @abstractmethod
    def get_service_factory(self) -> Generator[ServiceFactory, None, None]:
        """サービスファクトリーを取得するコンテキストマネージャー"""


class SqlModelUnitOfWork(UnitOfWork):
    """SQLModel用Unit of Work実装

    SQLModelのSessionを使用してトランザクション管理を行います。
    """

    def __init__(self) -> None:
        """SqlModelUnitOfWorkの初期化"""
        self._session: Session | None = None
        self._repository_factory: RepositoryFactory | None = None
        self._service_factory: ServiceFactory | None = None

    def __enter__(self) -> Self:
        """セッション開始とファクトリ初期化"""
        self._session = Session(engine)
        self._repository_factory = RepositoryFactory(self._session)
        self._service_factory = ServiceFactory(self._repository_factory)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """セッション終了とクリーンアップ"""
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()

    def commit(self) -> None:
        """変更をコミット"""
        if self._session:
            self._session.commit()

    def rollback(self) -> None:
        """変更をロールバック"""
        if self._session:
            self._session.rollback()

    @property
    def session(self) -> Session:
        """現在のセッションを取得

        Returns:
            Session: データベースセッション

        Raises:
            RuntimeError: Unit of Workが初期化されていない場合
        """
        if self._session is None:
            msg = "Unit of Work not initialized"
            raise RuntimeError(msg)
        return self._session

    @property
    def repository_factory(self) -> RepositoryFactory:
        """リポジトリファクトリを取得

        Returns:
            RepositoryFactory: リポジトリファクトリインスタンス

        Raises:
            RuntimeError: Unit of Workが初期化されていない場合
        """
        if self._repository_factory is None:
            msg = "Unit of Work not initialized"
            raise RuntimeError(msg)
        return self._repository_factory

    @property
    def service_factory(self) -> ServiceFactory:
        """サービスファクトリを取得

        Returns:
            ServiceFactory: サービスファクトリインスタンス

        Raises:
            RuntimeError: Unit of Workが初期化されていない場合
        """
        if self._service_factory is None:
            msg = "Unit of Work not initialized"
            raise RuntimeError(msg)
        return self._service_factory

    @contextmanager
    def get_service_factory(self) -> Generator[ServiceFactory, None, None]:
        """サービスファクトリーを取得するコンテキストマネージャー

        Yields:
            ServiceFactory: サービスファクトリインスタンス
        """
        yield self.service_factory
