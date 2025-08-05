"""Factory テストモジュール

RepositoryFactory と ServiceFactory の依存性注入動作をテストします。
"""

from sqlmodel import Session

from logic.container import ServiceContainer
from logic.factory import RepositoryFactory, ServiceFactory, create_service_factory, get_application_service_container
from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.project_service import ProjectService
from logic.services.tag_service import TagService
from logic.services.task_service import TaskService
from logic.services.task_tag_service import TaskTagService


class TestRepositoryFactory:
    """RepositoryFactory のテストクラス

    リポジトリファクトリの動作を検証します。
    """

    def test_create_task_repository(self, test_session: Session) -> None:
        """TaskRepository が正しく作成されることをテスト"""
        factory = RepositoryFactory(test_session)

        repository = factory.create_task_repository()

        assert isinstance(repository, TaskRepository)
        assert repository.session is test_session

    def test_create_project_repository(self, test_session: Session) -> None:
        """ProjectRepository が正しく作成されることをテスト"""
        factory = RepositoryFactory(test_session)

        repository = factory.create_project_repository()

        assert isinstance(repository, ProjectRepository)
        assert repository.session is test_session

    def test_create_tag_repository(self, test_session: Session) -> None:
        """TagRepository が正しく作成されることをテスト"""
        factory = RepositoryFactory(test_session)

        repository = factory.create_tag_repository()

        assert isinstance(repository, TagRepository)
        assert repository.session is test_session

    def test_create_task_tag_repository(self, test_session: Session) -> None:
        """TaskTagRepository が正しく作成されることをテスト"""
        factory = RepositoryFactory(test_session)

        repository = factory.create_task_tag_repository()

        assert isinstance(repository, TaskTagRepository)
        assert repository.session is test_session

    def test_repository_factory_creates_different_instances(self, test_session: Session) -> None:
        """RepositoryFactory が呼び出しごとに新しいインスタンスを作成することをテスト"""
        factory = RepositoryFactory(test_session)

        repo1 = factory.create_task_repository()
        repo2 = factory.create_task_repository()

        # [AI GENERATED] 異なるインスタンスが作成されることを確認
        assert repo1 is not repo2
        assert isinstance(repo1, TaskRepository)
        assert isinstance(repo2, TaskRepository)


class TestServiceFactory:
    """ServiceFactory のテストクラス

    サービスファクトリの動作を検証します。
    """

    def test_create_task_service(self, test_session: Session) -> None:
        """TaskService が正しい依存性で作成されることをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        service = service_factory.create_task_service()

        assert isinstance(service, TaskService)
        # [AI GENERATED] 依存性が正しく注入されていることを確認
        assert isinstance(service.task_repo, TaskRepository)
        assert isinstance(service.project_repo, ProjectRepository)
        assert isinstance(service.tag_repo, TagRepository)
        assert isinstance(service.task_tag_repo, TaskTagRepository)

    def test_create_project_service(self, test_session: Session) -> None:
        """ProjectService が正しい依存性で作成されることをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        service = service_factory.create_project_service()

        assert isinstance(service, ProjectService)
        # [AI GENERATED] 依存性が正しく注入されていることを確認
        assert isinstance(service.project_repo, ProjectRepository)
        assert isinstance(service.task_repo, TaskRepository)

    def test_create_tag_service(self, test_session: Session) -> None:
        """TagService が正しい依存性で作成されることをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        service = service_factory.create_tag_service()

        assert isinstance(service, TagService)
        # [AI GENERATED] 依存性が正しく注入されていることを確認
        assert isinstance(service.tag_repo, TagRepository)
        assert isinstance(service.task_tag_repo, TaskTagRepository)

    def test_create_task_tag_service(self, test_session: Session) -> None:
        """TaskTagService が正しい依存性で作成されることをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        service = service_factory.create_task_tag_service()

        assert isinstance(service, TaskTagService)
        # [AI GENERATED] 依存性が正しく注入されていることを確認
        assert isinstance(service.task_tag_repo, TaskTagRepository)

    def test_service_factory_creates_different_instances(self, test_session: Session) -> None:
        """ServiceFactory が呼び出しごとに新しいインスタンスを作成することをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        service1 = service_factory.create_task_service()
        service2 = service_factory.create_task_service()

        # [AI GENERATED] 異なるインスタンスが作成されることを確認
        assert service1 is not service2
        assert isinstance(service1, TaskService)
        assert isinstance(service2, TaskService)


class TestFactoryFunctions:
    """ファクトリ関数のテストクラス

    便利関数の動作を検証します。
    """

    def test_create_service_factory(self, test_session: Session) -> None:
        """create_service_factory 関数が正しく ServiceFactory を作成することをテスト"""
        service_factory = create_service_factory(test_session)

        assert isinstance(service_factory, ServiceFactory)
        assert isinstance(service_factory.repository_factory, RepositoryFactory)
        assert service_factory.repository_factory.session is test_session

    def test_create_service_factory_creates_working_services(self, test_session: Session) -> None:
        """create_service_factory で作成されたファクトリが動作するサービスを作成することをテスト"""
        service_factory = create_service_factory(test_session)

        task_service = service_factory.create_task_service()
        project_service = service_factory.create_project_service()

        assert isinstance(task_service, TaskService)
        assert isinstance(project_service, ProjectService)

    def test_get_application_service_container(self) -> None:
        """get_application_service_container 関数が ServiceContainer を返すことをテスト"""
        container = get_application_service_container()

        assert isinstance(container, ServiceContainer)

    def test_get_application_service_container_returns_singleton(self) -> None:
        """get_application_service_container がシングルトンを返すことをテスト"""
        container1 = get_application_service_container()
        container2 = get_application_service_container()

        # [AI GENERATED] 同じインスタンスが返されることを確認
        assert container1 is container2


class TestFactoryIntegration:
    """ファクトリ統合テストクラス

    ファクトリ間の連携動作を検証します。
    """

    def test_repository_factory_session_consistency(self, test_session: Session) -> None:
        """RepositoryFactory で作成された全リポジトリが同じセッションを使用することをテスト"""
        factory = RepositoryFactory(test_session)

        task_repo = factory.create_task_repository()
        project_repo = factory.create_project_repository()
        tag_repo = factory.create_tag_repository()
        task_tag_repo = factory.create_task_tag_repository()

        # [AI GENERATED] 全てのリポジトリが同じセッションを使用していることを確認
        assert task_repo.session is test_session
        assert project_repo.session is test_session
        assert tag_repo.session is test_session
        assert task_tag_repo.session is test_session

    def test_service_factory_repository_consistency(self, test_session: Session) -> None:
        """ServiceFactory で作成されたサービスが同じリポジトリファクトリを使用することをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        task_service = service_factory.create_task_service()
        project_service = service_factory.create_project_service()

        # [AI GENERATED] TaskService のリポジトリのセッションを確認
        assert task_service.task_repo.session is test_session
        assert task_service.project_repo.session is test_session

        # [AI GENERATED] ProjectService のリポジトリのセッションを確認
        assert project_service.project_repo.session is test_session
        assert project_service.task_repo.session is test_session
