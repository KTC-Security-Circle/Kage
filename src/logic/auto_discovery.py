"""自動発見システム

このモジュールは、サービスとリポジトリクラスを自動発見し、
レジストリに登録する機能を提供します。
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any

from loguru import logger

from logic.registry import get_repository_registry, get_service_registry


class AutoDiscovery:
    """サービスとリポジトリの自動発見クラス"""

    def __init__(self) -> None:
        """AutoDiscoveryを初期化する"""
        self.repository_registry = get_repository_registry()
        self.service_registry = get_service_registry()

    def discover_and_register_all(self) -> None:
        """全てのサービスとリポジトリを発見して登録する"""
        logger.info("Starting auto-discovery of services and repositories")

        try:
            self._discover_repositories()
            self._discover_services()
            logger.info("Auto-discovery completed successfully")
        except Exception as e:
            logger.exception(f"Auto-discovery failed: {e}")
            raise

    def _discover_repositories(self) -> None:
        """リポジトリクラスを自動発見して登録する"""
        logger.debug("Discovering repositories")

        try:
            # [AI GENERATED] repositoriesモジュールをインポート
            import logic.repositories as repositories_module

            package_path = Path(repositories_module.__file__).parent

            # [AI GENERATED] repositoriesパッケージ内の全モジュールを検索
            for module_info in pkgutil.iter_modules([str(package_path)]):
                if module_info.name.startswith("__"):
                    continue

                module_name = f"logic.repositories.{module_info.name}"
                try:
                    module = importlib.import_module(module_name)
                    self._register_repositories_from_module(module)
                except Exception as e:
                    logger.warning(f"Failed to import repository module {module_name}: {e}")

        except Exception as e:
            logger.exception(f"Failed to discover repositories: {e}")
            raise

    def _discover_services(self) -> None:
        """サービスクラスを自動発見して登録する"""
        logger.debug("Discovering services")

        try:
            # [AI GENERATED] servicesモジュールをインポート
            import logic.services as services_module

            package_path = Path(services_module.__file__).parent

            # [AI GENERATED] servicesパッケージ内の全モジュールを検索
            for module_info in pkgutil.iter_modules([str(package_path)]):
                if module_info.name.startswith("__") or module_info.name in ["base"]:
                    continue

                module_name = f"logic.services.{module_info.name}"
                try:
                    module = importlib.import_module(module_name)
                    self._register_services_from_module(module)
                except Exception as e:
                    logger.warning(f"Failed to import service module {module_name}: {e}")

        except Exception as e:
            logger.exception(f"Failed to discover services: {e}")
            raise

    def _register_repositories_from_module(self, module: Any) -> None:
        """モジュールからリポジトリクラスを登録する

        Args:
            module: インポートしたモジュール
        """
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # [AI GENERATED] モジュール内で定義されたクラスかチェック
            if not self._is_class_defined_in_module(obj, module):
                continue

            # [AI GENERATED] リポジトリクラスかチェック（名前がRepositoryで終わる）
            if name.endswith("Repository") and name != "BaseRepository":
                try:
                    # [AI GENERATED] 登録名を生成（例：MemoRepository -> memo）
                    registry_name = self._generate_repository_name(name)
                    self.repository_registry.register(registry_name, obj)
                    logger.debug(f"Auto-registered repository: {registry_name} -> {obj}")
                except Exception as e:
                    logger.warning(f"Failed to register repository {name}: {e}")

    def _register_services_from_module(self, module: Any) -> None:
        """モジュールからサービスクラスを登録する

        Args:
            module: インポートしたモジュール
        """
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # [AI GENERATED] モジュール内で定義されたクラスかチェック
            if not self._is_class_defined_in_module(obj, module):
                continue

            # [AI GENERATED] サービスクラスかチェック（名前がServiceで終わる）
            if name.endswith("Service") and name not in ["ServiceBase", "BaseService"]:
                try:
                    # [AI GENERATED] 登録名を生成（例：MemoService -> memo）
                    registry_name = self._generate_service_name(name)
                    self.service_registry.register(registry_name, obj)
                    logger.debug(f"Auto-registered service: {registry_name} -> {obj}")
                except Exception as e:
                    logger.warning(f"Failed to register service {name}: {e}")

    def _is_class_defined_in_module(self, cls: type, module: Any) -> bool:
        """クラスがモジュール内で定義されているかチェック

        Args:
            cls: チェックするクラス
            module: モジュール

        Returns:
            bool: モジュール内で定義されている場合True
        """
        return cls.__module__ == module.__name__

    def _generate_repository_name(self, class_name: str) -> str:
        """リポジトリクラス名から登録名を生成

        Args:
            class_name: クラス名（例：MemoRepository）

        Returns:
            str: 登録名（例：memo）
        """
        # [AI GENERATED] Repositoryサフィックスを削除し、小文字に変換
        name = class_name[:-len("Repository")]
        return self._convert_to_snake_case(name)

    def _generate_service_name(self, class_name: str) -> str:
        """サービスクラス名から登録名を生成

        Args:
            class_name: クラス名（例：MemoService）

        Returns:
            str: 登録名（例：memo）
        """
        # [AI GENERATED] Serviceサフィックスを削除し、小文書に変換
        name = class_name[:-len("Service")]
        return self._convert_to_snake_case(name)

    def _convert_to_snake_case(self, name: str) -> str:
        """PascalCaseをsnake_caseに変換

        Args:
            name: PascalCase文字列

        Returns:
            str: snake_case文字列
        """
        import re

        # [AI GENERATED] PascalCaseをsnake_caseに変換
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def list_registered_items(self) -> dict[str, Any]:
        """登録されているアイテムの一覧を取得

        Returns:
            dict[str, Any]: 登録されているアイテム
        """
        return {
            "repositories": self.repository_registry.get_registered_names(),
            "services": self.service_registry.get_registered_names(),
        }


# [AI GENERATED] グローバルインスタンス
_auto_discovery = AutoDiscovery()


def get_auto_discovery() -> AutoDiscovery:
    """AutoDiscoveryインスタンスを取得

    Returns:
        AutoDiscovery: AutoDiscoveryインスタンス
    """
    return _auto_discovery


def initialize_auto_discovery() -> None:
    """自動発見を初期化（アプリケーション起動時に呼び出し）"""
    _auto_discovery.discover_and_register_all()