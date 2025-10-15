"""Factory テスト（現行仕様）

RepositoryFactory と ServiceFactory の依存性注入・生成戦略を検証する。
"""

import pytest
from sqlmodel import Session

from logic.factory import ServiceFactory, ServiceFactoryError, create_service_factory
from logic.repositories import RepositoryFactory, RepositoryFactoryError
from logic.repositories.task import TaskRepository
from logic.services.task_service import TaskService


class TestRepositoryFactory:
    """RepositoryFactory のテストクラス

    リポジトリファクトリの動作を検証します。
    """

    def test_create_repository(self, test_session: Session) -> None:
        """create() が任意のリポジトリを生成することをテスト"""
        factory = RepositoryFactory(test_session)
        repository = factory.create(TaskRepository)
        assert isinstance(repository, TaskRepository)
        assert repository.session is test_session

    def test_create_repository_invalid_type(self, test_session: Session) -> None:
        """create_repository に無効なクラスを渡した場合に例外が発生することをテスト"""
        factory = RepositoryFactory(test_session)

        class InvalidRepository:
            """BaseRepository を継承しないクラス"""

            def __init__(self, session: Session) -> None:
                self.session = session

        with pytest.raises(RepositoryFactoryError):
            factory.create(InvalidRepository)  # type: ignore[arg-type]

    def test_repository_factory_creates_different_instances(self, test_session: Session) -> None:
        """RepositoryFactory が呼び出しごとに新しいインスタンスを作成することをテスト"""
        factory = RepositoryFactory(test_session)
        repo1 = factory.create(TaskRepository)
        repo2 = factory.create(TaskRepository)

        # 異なるインスタンスが作成されることを確認
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

        service = service_factory.get_service(TaskService)

        assert isinstance(service, TaskService)
        # 依存性が正しく注入されていることを確認
        assert isinstance(service.task_repo, TaskRepository)
        assert service.task_repo.session is test_session

    def test_get_service_invalid_type_raises(self, test_session: Session) -> None:
        """ServiceBaseを継承しない型を渡すと ServiceFactoryError"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        class NotAService:
            pass

        with pytest.raises(ServiceFactoryError):
            service_factory.get_service(NotAService)  # type: ignore[arg-type]

    def test_service_factory_caches_same_instance(self, test_session: Session) -> None:
        """同じサービス型の取得は同一インスタンス（キャッシュ）"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        s1 = service_factory.get_service(TaskService)
        s2 = service_factory.get_service(TaskService)
        assert s1 is s2

    def test_service_factory_has_repo_factory(self, test_session: Session) -> None:
        """ServiceFactory は RepositoryFactory を保持している"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)
        assert service_factory.repo_factory is repository_factory

    # register_service は現行実装に存在しないため対象外

    # 未登録サービス/不正型は上のテストで網羅

    def test_service_factory_creates_cached_instance(self, test_session: Session) -> None:
        """ServiceFactory は同じ型のサービスをキャッシュして返す"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        s1 = service_factory.get_service(TaskService)
        s2 = service_factory.get_service(TaskService)
        # キャッシュにより同一インスタンスが返る
        assert s1 is s2
        assert isinstance(s1, TaskService)
        assert isinstance(s2, TaskService)


class TestFactoryFunctions:
    """ファクトリ関数のテストクラス

    便利関数の動作を検証します。
    """

    def test_create_service_factory(self, test_session: Session) -> None:
        """create_service_factory 関数が正しく ServiceFactory を作成することをテスト"""
        service_factory = create_service_factory(test_session)

        assert isinstance(service_factory, ServiceFactory)
        assert service_factory.repo_factory.session is test_session

    def test_create_service_factory_creates_working_services(self, test_session: Session) -> None:
        """create_service_factory で作成されたファクトリが動作するサービスを作成することをテスト"""
        service_factory = create_service_factory(test_session)

        task_service = service_factory.get_service(TaskService)
        assert isinstance(task_service, TaskService)

    # ApplicationServices 系は別モジュールでテスト


class TestFactoryIntegration:
    """ファクトリ統合テストクラス

    ファクトリ間の連携動作を検証します。
    """

    def test_repository_factory_session_consistency(self, test_session: Session) -> None:
        """RepositoryFactory で作成された全リポジトリが同じセッションを使用することをテスト"""
        factory = RepositoryFactory(test_session)

        task_repo = factory.create(TaskRepository)
        # 全てのリポジトリが同じセッションを使用していることを確認（ここではTaskで代表）
        assert task_repo.session is test_session

    def test_service_factory_repository_consistency(self, test_session: Session) -> None:
        """ServiceFactory で作成されたサービスが同じリポジトリファクトリを使用することをテスト"""
        repository_factory = RepositoryFactory(test_session)
        service_factory = ServiceFactory(repository_factory)

        task_service = service_factory.get_service(TaskService)
        # TaskService のリポジトリのセッションを確認
        assert task_service.task_repo.session is test_session
