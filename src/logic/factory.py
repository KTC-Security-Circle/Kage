"""依存性注入のためのファクトリクラス

このモジュールは、サービスとリポジトリの依存性を管理し、
適切な形で注入するためのファクトリクラスを提供します。

Application Service層への移行をサポートするため、
従来のcreate_service_factory関数は引き続き利用可能です。

新しいレジストリベースシステムでは、リフレクションを使用して
サービスとリポジトリを自動発見し、依存性を自動解決します。
"""

import warnings
from typing import Any, TypeVar

from sqlmodel import Session

from logic.auto_discovery import initialize_auto_discovery
from logic.container import ServiceContainer
from logic.registry import get_repository_registry, get_service_registry

T = TypeVar("T")


class RepositoryFactory:
    """リポジトリファクトリ

    データベースセッションを使用してリポジトリインスタンスを生成するファクトリクラス。

    新しいレジストリベースのcreateメソッドと、
    後方互換性のための従来のcreate_*メソッドを提供します。
    """

    def __init__(self, session: Session) -> None:
        """RepositoryFactoryを初期化する

        Args:
            session: データベースセッション
        """
        self.session = session
        # [AI GENERATED] 初回実行時に自動発見を実行
        self._ensure_auto_discovery()

    def _ensure_auto_discovery(self) -> None:
        """自動発見が実行されていることを確認"""
        try:
            initialize_auto_discovery()
        except Exception:
            # [AI GENERATED] 既に初期化済みの場合はエラーを無視
            pass

    def create(self, repository_name: str) -> Any:
        """レジストリを使用してリポジトリを作成する

        Args:
            repository_name: リポジトリ名（例: "memo", "task"）

        Returns:
            Any: リポジトリインスタンス

        Raises:
            ValueError: 登録されていないリポジトリ名の場合

        Example:
            >>> factory = RepositoryFactory(session)
            >>> memo_repo = factory.create("memo")
            >>> task_repo = factory.create("task")
        """
        registry = get_repository_registry()
        if not registry.is_registered(repository_name):
            raise ValueError(f"Repository '{repository_name}' is not registered")

        return registry.create(repository_name, self.session)

    def get_available_repositories(self) -> list[str]:
        """利用可能なリポジトリ名の一覧を取得

        Returns:
            list[str]: 利用可能なリポジトリ名のリスト
        """
        registry = get_repository_registry()
        return registry.get_registered_names()

    def create_memo_repository(self) -> Any:
        """MemoRepositoryを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("memo") を使用してください。

        Returns:
            MemoRepository: メモリポジトリインスタンス
        """
        warnings.warn(
            "create_memo_repository is deprecated. Use create('memo') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.repositories.memo import MemoRepository

        return MemoRepository(self.session)

    def create_task_repository(self) -> Any:
        """TaskRepositoryを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("task") を使用してください。

        Returns:
            TaskRepository: タスクリポジトリインスタンス
        """
        warnings.warn(
            "create_task_repository is deprecated. Use create('task') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.repositories.task import TaskRepository

        return TaskRepository(self.session)

    def create_project_repository(self) -> Any:
        """ProjectRepositoryを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("project") を使用してください。

        Returns:
            ProjectRepository: プロジェクトリポジトリインスタンス
        """
        warnings.warn(
            "create_project_repository is deprecated. Use create('project') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.repositories.project import ProjectRepository

        return ProjectRepository(self.session)

    def create_tag_repository(self) -> Any:
        """TagRepositoryを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("tag") を使用してください。

        Returns:
            TagRepository: タグリポジトリインスタンス
        """
        warnings.warn(
            "create_tag_repository is deprecated. Use create('tag') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.repositories.tag import TagRepository

        return TagRepository(self.session)

    def create_task_tag_repository(self) -> Any:
        """TaskTagRepositoryを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("task_tag") を使用してください。

        Returns:
            TaskTagRepository: タスクタグリポジトリインスタンス
        """
        warnings.warn(
            "create_task_tag_repository is deprecated. Use create('task_tag') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.repositories.task_tag import TaskTagRepository

        return TaskTagRepository(self.session)


class ServiceFactory:
    """サービスファクトリ

    リポジトリファクトリを使用してサービスインスタンスを生成するファクトリクラス。

    新しいレジストリベースのcreateメソッドと、
    後方互換性のための従来のcreate_*メソッドを提供します。
    """

    def __init__(self, repository_factory: RepositoryFactory) -> None:
        """ServiceFactoryを初期化する

        Args:
            repository_factory: リポジトリファクトリ
        """
        self.repository_factory = repository_factory

    def create(self, service_name: str) -> Any:
        """レジストリを使用してサービスを作成する

        Args:
            service_name: サービス名（例: "memo", "task"）

        Returns:
            Any: サービスインスタンス

        Raises:
            ValueError: 登録されていないサービス名の場合

        Example:
            >>> factory = ServiceFactory(repository_factory)
            >>> memo_service = factory.create("memo")
            >>> task_service = factory.create("task")
        """
        registry = get_service_registry()
        if not registry.is_registered(service_name):
            raise ValueError(f"Service '{service_name}' is not registered")

        return registry.create(service_name, self.repository_factory.session)

    def get_available_services(self) -> list[str]:
        """利用可能なサービス名の一覧を取得

        Returns:
            list[str]: 利用可能なサービス名のリスト
        """
        registry = get_service_registry()
        return registry.get_registered_names()

    def create_memo_service(self) -> Any:
        """MemoServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("memo") を使用してください。

        Returns:
            MemoService: メモサービスインスタンス
        """
        warnings.warn(
            "create_memo_service is deprecated. Use create('memo') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.memo_service import MemoService

        memo_repo = self.repository_factory.create_memo_repository()
        task_repo = self.repository_factory.create_task_repository()

        return MemoService(
            memo_repo=memo_repo,
            task_repo=task_repo,
        )

    def create_task_service(self) -> Any:
        """TaskServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("task") を使用してください。

        Returns:
            TaskService: タスクサービスインスタンス
        """
        warnings.warn(
            "create_task_service is deprecated. Use create('task') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.task_service import TaskService

        task_repo = self.repository_factory.create_task_repository()
        project_repo = self.repository_factory.create_project_repository()
        tag_repo = self.repository_factory.create_tag_repository()
        task_tag_repo = self.repository_factory.create_task_tag_repository()

        return TaskService(
            task_repo=task_repo,
            project_repo=project_repo,
            tag_repo=tag_repo,
            task_tag_repo=task_tag_repo,
        )

    def create_project_service(self) -> Any:
        """ProjectServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("project") を使用してください。

        Returns:
            ProjectService: プロジェクトサービスインスタンス
        """
        warnings.warn(
            "create_project_service is deprecated. Use create('project') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.project_service import ProjectService

        project_repo = self.repository_factory.create_project_repository()
        task_repo = self.repository_factory.create_task_repository()

        return ProjectService(
            project_repo=project_repo,
            task_repo=task_repo,
        )

    def create_tag_service(self) -> Any:
        """TagServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("tag") を使用してください。

        Returns:
            TagService: タグサービスインスタンス
        """
        warnings.warn(
            "create_tag_service is deprecated. Use create('tag') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.tag_service import TagService

        tag_repo = self.repository_factory.create_tag_repository()
        task_tag_repo = self.repository_factory.create_task_tag_repository()

        return TagService(
            tag_repo=tag_repo,
            task_tag_repo=task_tag_repo,
        )

    def create_task_tag_service(self) -> Any:
        """TaskTagServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("task_tag") を使用してください。

        Returns:
            TaskTagService: タスクタグサービスインスタンス
        """
        warnings.warn(
            "create_task_tag_service is deprecated. Use create('task_tag') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.task_tag_service import TaskTagService

        task_tag_repo = self.repository_factory.create_task_tag_repository()

        return TaskTagService(
            task_tag_repo=task_tag_repo,
        )

    def create_one_liner_service(self) -> Any:
        """OneLinerServiceを作成する

        .. deprecated::
            このメソッドは非推奨です。代わりに create("one_liner") を使用してください。

        Returns:
            OneLinerService: 一言コメントサービスインスタンス
        """
        warnings.warn(
            "create_one_liner_service is deprecated. Use create('one_liner') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from logic.services.one_liner_service import OneLinerService

        # [AI GENERATED] OneLinerServiceはリポジトリに依存しないため、直接インスタンス化
        return OneLinerService()


def create_service_factory(session: Session) -> ServiceFactory:
    """サービスファクトリを作成する

    Args:
        session: データベースセッション

    Returns:
        ServiceFactory: サービスファクトリインスタンス
    """
    repository_factory = RepositoryFactory(session)
    return ServiceFactory(repository_factory)


def get_application_service_container() -> ServiceContainer:
    """Application Service コンテナを取得

    View層での使用を推奨。Session管理が不要になります。

    Returns:
        ServiceContainer: Application Serviceコンテナ

    Example:
        >>> container = get_application_service_container()
        >>> task_app_service = container.get_task_application_service()
        >>> command = CreateTaskCommand(title="新しいタスク")
        >>> task = task_app_service.create_task(command)
    """
    from logic.container import service_container

    return service_container
