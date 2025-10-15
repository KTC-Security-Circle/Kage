"""依存性注入のためのファクトリクラス

このモジュールは、サービスとリポジトリの依存性を管理し、
適切な形で注入するためのファクトリクラスを提供します。

Application Service層への移行をサポートするため、
従来のcreate_service_factory関数は引き続き利用可能です。
"""

from inspect import signature
from typing import TypeVar

from sqlmodel import Session

from logic.repositories import RepositoryFactory
from logic.services.base import ServiceBase

ServiceType = TypeVar("ServiceType", bound=ServiceBase)


class ServiceFactoryError(Exception):
    """サービスファクトリ関連の例外"""

    def __init__(self, message: str) -> None:
        """ServiceFactoryError を初期化する

        Args:
            message (str): エラーメッセージ
        """
        super().__init__(message)


class ServiceFactory:
    """サービスファクトリ

    リポジトリファクトリを使用してサービスインスタンスを生成するファクトリクラス。
    """

    def __init__(self, repo_factory: RepositoryFactory) -> None:
        """ServiceFactoryを初期化する

        Args:
            repo_factory: リポジトリファクトリ
        """
        self.repo_factory = repo_factory

        self._services: dict[type[ServiceBase], ServiceBase] = {}

    def _register_service(
        self,
        service_type: type[ServiceType],
    ) -> ServiceType:
        """サービスのビルダーを登録する

        Args:
            service_type: 登録対象のサービスクラス
        """
        try:
            if signature(service_type.build_service).parameters == {"self"}:
                # self のみを引数としている場合
                # 引数なしのビルドメソッド
                built = service_type.build_service()
            else:
                # それ以外はリポジトリファクトリを引数に取るビルドメソッドとしてビルド
                built = service_type.build_service(self.repo_factory)
        except Exception as e:
            error_message = f"サービスのビルドに失敗しました: {service_type.__name__} - {e}"
            raise ServiceFactoryError(error_message) from e
        self._services[service_type] = built
        return built

    def get_service(self, service_type: type[ServiceType]) -> ServiceType:
        """サービスインスタンスを取得する

        Args:
            service_type: 取得対象のサービスクラス

        Returns:
            ServiceBase: サービスインスタンス

        Raises:
            ServiceFactoryError: サービスが登録されていない場合
        """
        built = self._services.get(service_type)
        if built is not None:
            if not isinstance(built, service_type):
                error_message = (
                    f"ServiceFactoryが保持するサービスの型が不正です: 期待される型 {service_type.__name__}, "
                    f"実際の型 {type(built).__name__}"
                )
                raise ServiceFactoryError(error_message)
            return built

        return self._register_service(service_type)


def create_service_factory(session: Session) -> ServiceFactory:
    """サービスファクトリを作成する

    Args:
        session: データベースセッション

    Returns:
        ServiceFactory: サービスファクトリインスタンス
    """
    repository_factory = RepositoryFactory(session)
    return ServiceFactory(repository_factory)
