"""依存性注入レジストリシステム

このモジュールは、サービスとリポジトリの自動発見と依存性解決を提供します。
新しいサービスやリポジトリを追加する際に、ファクトリクラスの変更が不要になります。
"""

import inspect
from abc import ABC, abstractmethod
from typing import Any, TypeVar, get_type_hints

from loguru import logger
from sqlmodel import Session

T = TypeVar("T")


class RegistryError(Exception):
    """レジストリ操作時のエラー"""



class BaseRegistry(ABC):
    """レジストリの基底クラス"""

    def __init__(self) -> None:
        """レジストリを初期化する"""
        self._registry: dict[str, type] = {}
        self._instances: dict[str, Any] = {}

    @abstractmethod
    def register(self, name: str, cls: type) -> None:
        """クラスをレジストリに登録する

        Args:
            name: 登録名
            cls: 登録するクラス
        """

    @abstractmethod
    def create(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """登録されたクラスのインスタンスを作成する

        Args:
            name: 登録名
            *args: 位置引数
            **kwargs: キーワード引数

        Returns:
            Any: 作成されたインスタンス
        """

    def is_registered(self, name: str) -> bool:
        """指定された名前がレジストリに登録されているかチェック

        Args:
            name: チェックする名前

        Returns:
            bool: 登録されている場合True
        """
        return name in self._registry

    def get_registered_names(self) -> list[str]:
        """登録されている名前の一覧を取得

        Returns:
            list[str]: 登録名のリスト
        """
        return list(self._registry.keys())


class RepositoryRegistry(BaseRegistry):
    """リポジトリレジストリ

    リポジトリクラスの登録と作成を管理します。
    全てのリポジトリはSessionを第一引数として受け取る必要があります。
    """

    def register(self, name: str, cls: type) -> None:
        """リポジトリクラスをレジストリに登録する

        Args:
            name: 登録名
            cls: リポジトリクラス

        Raises:
            RegistryError: 無効なリポジトリクラスの場合
        """
        # [AI GENERATED] リポジトリクラスの検証
        if not self._is_valid_repository_class(cls):
            raise RegistryError(f"Invalid repository class: {cls}")

        self._registry[name] = cls
        logger.debug(f"Registered repository: {name} -> {cls}")

    def create(self, name: str, session: Session) -> Any:
        """リポジトリインスタンスを作成する

        Args:
            name: 登録名
            session: データベースセッション

        Returns:
            Any: リポジトリインスタンス

        Raises:
            RegistryError: 登録されていない名前の場合
        """
        if name not in self._registry:
            raise RegistryError(f"Repository not registered: {name}")

        cls = self._registry[name]
        try:
            instance = cls(session)
            logger.debug(f"Created repository instance: {name}")
            return instance
        except Exception as e:
            logger.exception(f"Failed to create repository {name}: {e}")
            raise RegistryError(f"Failed to create repository {name}: {e}") from e

    def _is_valid_repository_class(self, cls: type) -> bool:
        """リポジトリクラスが有効かチェック

        Args:
            cls: チェックするクラス

        Returns:
            bool: 有効な場合True
        """
        try:
            # [AI GENERATED] __init__メソッドのシグネチャをチェック
            init_sig = inspect.signature(cls.__init__)
            params = list(init_sig.parameters.values())[1:]  # selfを除く

            # 最初の引数がSessionかをチェック
            if not params:
                return False

            first_param = params[0]
            if first_param.annotation != Session:
                return False

            return True
        except Exception:
            return False


class ServiceRegistry(BaseRegistry):
    """サービスレジストリ

    サービスクラスの登録と依存性解決を管理します。
    依存性は型ヒントから自動解決されます。
    """

    def __init__(self, repository_registry: RepositoryRegistry) -> None:
        """サービスレジストリを初期化する

        Args:
            repository_registry: リポジトリレジストリ
        """
        super().__init__()
        self.repository_registry = repository_registry

    def register(self, name: str, cls: type) -> None:
        """サービスクラスをレジストリに登録する

        Args:
            name: 登録名
            cls: サービスクラス
        """
        self._registry[name] = cls
        logger.debug(f"Registered service: {name} -> {cls}")

    def create(self, name: str, session: Session) -> Any:
        """サービスインスタンスを作成する

        依存性は型ヒントから自動解決されます。

        Args:
            name: 登録名
            session: データベースセッション

        Returns:
            Any: サービスインスタンス

        Raises:
            RegistryError: 登録されていない名前や依存性解決エラーの場合
        """
        if name not in self._registry:
            raise RegistryError(f"Service not registered: {name}")

        cls = self._registry[name]
        try:
            dependencies = self._resolve_dependencies(cls, session)
            instance = cls(**dependencies)
            logger.debug(f"Created service instance: {name}")
            return instance
        except Exception as e:
            logger.exception(f"Failed to create service {name}: {e}")
            raise RegistryError(f"Failed to create service {name}: {e}") from e

    def _resolve_dependencies(self, cls: type, session: Session) -> dict[str, Any]:
        """サービスクラスの依存性を解決する

        Args:
            cls: サービスクラス
            session: データベースセッション

        Returns:
            dict[str, Any]: 解決された依存性

        Raises:
            RegistryError: 依存性解決エラーの場合
        """
        dependencies = {}

        try:
            # [AI GENERATED] __init__メソッドの型ヒントを取得
            init_sig = inspect.signature(cls.__init__)
            type_hints = get_type_hints(cls.__init__)

            for param_name, param in init_sig.parameters.items():
                if param_name == "self":
                    continue

                param_type = type_hints.get(param_name)
                if param_type is None:
                    continue

                # [AI GENERATED] リポジトリクラスの場合、レジストリから取得
                repo_instance = self._find_repository_by_type(param_type, session)
                if repo_instance:
                    dependencies[param_name] = repo_instance
                    continue

                # [AI GENERATED] その他の依存性は現在サポートしない
                logger.warning(f"Unsupported dependency type: {param_type} for {param_name}")

            return dependencies

        except Exception as e:
            logger.exception(f"Failed to resolve dependencies for {cls}: {e}")
            raise RegistryError(f"Failed to resolve dependencies for {cls}: {e}") from e

    def _find_repository_by_type(self, repo_type: type, session: Session) -> Any:
        """指定された型のリポジトリを検索して作成

        Args:
            repo_type: リポジトリの型
            session: データベースセッション

        Returns:
            Any: リポジトリインスタンス、見つからない場合None
        """
        for name, registered_cls in self.repository_registry._registry.items():
            if registered_cls == repo_type:
                return self.repository_registry.create(name, session)
        return None


# [AI GENERATED] グローバルレジストリインスタンス
_repository_registry = RepositoryRegistry()
_service_registry = ServiceRegistry(_repository_registry)


def get_repository_registry() -> RepositoryRegistry:
    """リポジトリレジストリを取得

    Returns:
        RepositoryRegistry: リポジトリレジストリインスタンス
    """
    return _repository_registry


def get_service_registry() -> ServiceRegistry:
    """サービスレジストリを取得

    Returns:
        ServiceRegistry: サービスレジストリインスタンス
    """
    return _service_registry
