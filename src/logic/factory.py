"""依存性注入のためのファクトリクラス

このモジュールは、サービスとリポジトリの依存性を管理し、
適切な形で注入するためのファクトリクラスを提供します。

Application Service層への移行をサポートするため、
従来のcreate_service_factory関数は引き続き利用可能です。
"""

from collections.abc import Callable
from typing import TypeVar, cast

from sqlmodel import Session
from typing_extensions import deprecated

from logic.container import ServiceContainer
from logic.repositories.memo import MemoRepository
from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.memo_service import MemoService
from logic.services.one_liner_service import OneLinerService
from logic.services.project_service import ProjectService
from logic.services.tag_service import TagService
from logic.services.task_service import TaskService
from logic.services.task_tag_service import TaskTagService

_ServiceT = TypeVar("_ServiceT")


class ServiceFactoryError(Exception):
    """サービスファクトリ関連の例外"""

    def __init__(self, message: str) -> None:
        """ServiceFactoryError を初期化する

        Args:
            message (str): エラーメッセージ
        """
        super().__init__(message)


class RepositoryFactory:
    """リポジトリファクトリ

    データベースセッションを使用してリポジトリインスタンスを生成するファクトリクラス。
    """

    def __init__(self, session: Session) -> None:
        """RepositoryFactoryを初期化する

        Args:
            session: データベースセッション
        """
        self.session = session

    def create_memo_repository(self) -> MemoRepository:
        """MemoRepositoryを作成する

        Returns:
            MemoRepository: メモリポジトリインスタンス
        """
        return MemoRepository(self.session)

    def create_task_repository(self) -> TaskRepository:
        """TaskRepositoryを作成する

        Returns:
            TaskRepository: タスクリポジトリインスタンス
        """
        return TaskRepository(self.session)

    def create_project_repository(self) -> ProjectRepository:
        """ProjectRepositoryを作成する

        Returns:
            ProjectRepository: プロジェクトリポジトリインスタンス
        """
        return ProjectRepository(self.session)

    def create_tag_repository(self) -> TagRepository:
        """TagRepositoryを作成する

        Returns:
            TagRepository: タグリポジトリインスタンス
        """
        return TagRepository(self.session)

    def create_task_tag_repository(self) -> TaskTagRepository:
        """TaskTagRepositoryを作成する

        Returns:
            TaskTagRepository: タスクタグリポジトリインスタンス
        """
        return TaskTagRepository(self.session)


class ServiceFactory:
    """サービスファクトリ

    リポジトリファクトリを使用してサービスインスタンスを生成するファクトリクラス。
    """

    def __init__(self, repository_factory: RepositoryFactory) -> None:
        """ServiceFactoryを初期化する

        Args:
            repository_factory: リポジトリファクトリ
        """
        self.repository_factory = repository_factory

        self._service_builders: dict[type[object], Callable[[RepositoryFactory], object]] = {}
        self._register_default_services()

    def register_service(
        self,
        service_type: type[_ServiceT],
        builder: Callable[[RepositoryFactory], _ServiceT],
    ) -> None:
        """サービスのビルダーを登録する

        Args:
            service_type (type[_ServiceT]): 登録対象のサービスクラス
            builder (Callable[[RepositoryFactory], _ServiceT]): サービスインスタンスを生成するビルダー
        """
        self._service_builders[service_type] = cast(
            "Callable[[RepositoryFactory], object]",
            builder,
        )

    def get_service(self, service_type: type[_ServiceT]) -> _ServiceT:
        """サービスインスタンスを取得する

        Args:
            service_type (type[_ServiceT]): 取得対象のサービスクラス

        Returns:
            _ServiceT: サービスインスタンス

        Raises:
            ServiceFactoryError: サービスが登録されていない場合
        """
        builder = self._service_builders.get(service_type)
        if builder is None:
            error_message = f"ServiceFactoryに登録されていないサービスが要求されました: {service_type.__name__}"
            raise ServiceFactoryError(error_message)

        return cast("_ServiceT", builder(self.repository_factory))

    def _register_default_services(self) -> None:
        """既定のサービスビルダーを登録する"""
        self.register_service(
            MemoService,
            lambda repo_factory: MemoService(
                memo_repo=repo_factory.create_memo_repository(),
                task_repo=repo_factory.create_task_repository(),
            ),
        )
        self.register_service(
            TaskService,
            lambda repo_factory: TaskService(
                task_repo=repo_factory.create_task_repository(),
                project_repo=repo_factory.create_project_repository(),
                tag_repo=repo_factory.create_tag_repository(),
                task_tag_repo=repo_factory.create_task_tag_repository(),
            ),
        )
        self.register_service(
            ProjectService,
            lambda repo_factory: ProjectService(
                project_repo=repo_factory.create_project_repository(),
                task_repo=repo_factory.create_task_repository(),
            ),
        )
        self.register_service(
            TagService,
            lambda repo_factory: TagService(
                tag_repo=repo_factory.create_tag_repository(),
                task_tag_repo=repo_factory.create_task_tag_repository(),
            ),
        )
        self.register_service(
            TaskTagService,
            lambda repo_factory: TaskTagService(
                task_tag_repo=repo_factory.create_task_tag_repository(),
            ),
        )
        self.register_service(
            OneLinerService,
            lambda _: OneLinerService(),
        )

    @deprecated("Use get_service(MemoService) instead")
    def create_memo_service(self) -> MemoService:
        """MemoServiceを作成する

        Returns:
            MemoService: メモサービスインスタンス
        """
        return self.get_service(MemoService)

    @deprecated("Use get_service(TaskService) instead")
    def create_task_service(self) -> TaskService:
        """TaskServiceを作成する

        Returns:
            TaskService: タスクサービスインスタンス
        """
        return self.get_service(TaskService)

    @deprecated("Use get_service(ProjectService) instead")
    def create_project_service(self) -> ProjectService:
        """ProjectServiceを作成する

        Returns:
            ProjectService: プロジェクトサービスインスタンス
        """
        return self.get_service(ProjectService)

    @deprecated("Use get_service(TagService) instead")
    def create_tag_service(self) -> TagService:
        """TagServiceを作成する

        Returns:
            TagService: タグサービスインスタンス
        """
        return self.get_service(TagService)

    @deprecated("Use get_service(TaskTagService) instead")
    def create_task_tag_service(self) -> TaskTagService:
        """TaskTagServiceを作成する

        Returns:
            TaskTagService: タスクタグサービスインスタンス
        """
        return self.get_service(TaskTagService)

    @deprecated("Use get_service(OneLinerService) instead")
    def create_one_liner_service(self) -> OneLinerService:
        """OneLinerServiceを作成する

        Returns:
            OneLinerService: 一言コメントサービスインスタンス
        """
        return self.get_service(OneLinerService)


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
