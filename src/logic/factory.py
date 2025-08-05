"""依存性注入のためのファクトリクラス

このモジュールは、サービスとリポジトリの依存性を管理し、
適切な形で注入するためのファクトリクラスを提供します。
"""

from sqlmodel import Session

from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.project_service import ProjectService
from logic.services.tag_service import TagService
from logic.services.task_service import TaskService


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


def create_service_factory(session: Session) -> ServiceFactory:
    """サービスファクトリを作成する

    Args:
        session: データベースセッション

    Returns:
        ServiceFactory: サービスファクトリインスタンス
    """
    repository_factory = RepositoryFactory(session)
    return ServiceFactory(repository_factory)
