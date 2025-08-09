"""依存性注入のためのファクトリクラス

このモジュールは、サービスとリポジトリの依存性を管理し、
適切な形で注入するためのファクトリクラスを提供します。

Application Service層への移行をサポートするため、
従来のcreate_service_factory関数は引き続き利用可能です。
"""

from sqlmodel import Session

from logic.container import ServiceContainer
from logic.repositories.memo import MemoRepository
from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.memo_service import MemoService
from logic.services.project_service import ProjectService
from logic.services.tag_service import TagService
from logic.services.task_service import TaskService
from logic.services.task_tag_service import TaskTagService


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

    def create_memo_service(self) -> MemoService:
        """MemoServiceを作成する

        Returns:
            MemoService: メモサービスインスタンス
        """
        memo_repo = self.repository_factory.create_memo_repository()
        task_repo = self.repository_factory.create_task_repository()

        return MemoService(
            memo_repo=memo_repo,
            task_repo=task_repo,
        )

    def create_task_service(self) -> TaskService:
        """TaskServiceを作成する

        Returns:
            TaskService: タスクサービスインスタンス
        """
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

    def create_project_service(self) -> ProjectService:
        """ProjectServiceを作成する

        Returns:
            ProjectService: プロジェクトサービスインスタンス
        """
        project_repo = self.repository_factory.create_project_repository()
        task_repo = self.repository_factory.create_task_repository()

        return ProjectService(
            project_repo=project_repo,
            task_repo=task_repo,
        )

    def create_tag_service(self) -> TagService:
        """TagServiceを作成する

        Returns:
            TagService: タグサービスインスタンス
        """
        tag_repo = self.repository_factory.create_tag_repository()
        task_tag_repo = self.repository_factory.create_task_tag_repository()

        return TagService(
            tag_repo=tag_repo,
            task_tag_repo=task_tag_repo,
        )

    def create_task_tag_service(self) -> TaskTagService:
        """TaskTagServiceを作成する

        Returns:
            TaskTagService: タスクタグサービスインスタンス
        """
        task_tag_repo = self.repository_factory.create_task_tag_repository()

        return TaskTagService(
            task_tag_repo=task_tag_repo,
        )


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
