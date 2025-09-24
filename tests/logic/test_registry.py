"""レジストリシステムのテスト"""

import pytest
from unittest.mock import Mock
from sqlmodel import Session

from logic.registry import RepositoryRegistry, ServiceRegistry, RegistryError


class MockRepository:
    """テスト用モックリポジトリ"""
    
    def __init__(self, session: Session) -> None:
        self.session = session


class MockRepositoryInvalid:
    """テスト用無効なリポジトリ（Sessionを受け取らない）"""
    
    def __init__(self, other_arg: str) -> None:
        self.other_arg = other_arg


class MockService:
    """テスト用モックサービス"""
    
    def __init__(self, mock_repo: MockRepository) -> None:
        self.mock_repo = mock_repo


class MockServiceNoRepo:
    """テスト用モックサービス（リポジトリ依存なし）"""
    
    def __init__(self) -> None:
        pass


class TestRepositoryRegistry:
    """RepositoryRegistryのテストクラス"""

    def test_register_valid_repository(self) -> None:
        """有効なリポジトリが正しく登録されることをテスト"""
        registry = RepositoryRegistry()
        
        registry.register("mock", MockRepository)
        
        assert registry.is_registered("mock")
        assert "mock" in registry.get_registered_names()

    def test_register_invalid_repository_raises_error(self) -> None:
        """無効なリポジトリの登録でエラーが発生することをテスト"""
        registry = RepositoryRegistry()
        
        with pytest.raises(RegistryError):
            registry.register("invalid", MockRepositoryInvalid)

    def test_create_registered_repository(self) -> None:
        """登録されたリポジトリが正しく作成されることをテスト"""
        registry = RepositoryRegistry()
        session = Mock(spec=Session)
        
        registry.register("mock", MockRepository)
        instance = registry.create("mock", session)
        
        assert isinstance(instance, MockRepository)
        assert instance.session is session

    def test_create_unregistered_repository_raises_error(self) -> None:
        """未登録のリポジトリ作成でエラーが発生することをテスト"""
        registry = RepositoryRegistry()
        session = Mock(spec=Session)
        
        with pytest.raises(RegistryError):
            registry.create("unregistered", session)

    def test_get_registered_names(self) -> None:
        """登録名一覧が正しく取得されることをテスト"""
        registry = RepositoryRegistry()
        
        registry.register("repo1", MockRepository)
        registry.register("repo2", MockRepository)
        
        names = registry.get_registered_names()
        assert set(names) == {"repo1", "repo2"}


class TestServiceRegistry:
    """ServiceRegistryのテストクラス"""

    def test_register_service(self) -> None:
        """サービスが正しく登録されることをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        
        service_registry.register("mock", MockServiceNoRepo)
        
        assert service_registry.is_registered("mock")
        assert "mock" in service_registry.get_registered_names()

    def test_create_service_without_dependencies(self) -> None:
        """依存性のないサービスが正しく作成されることをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        session = Mock(spec=Session)
        
        service_registry.register("mock", MockServiceNoRepo)
        instance = service_registry.create("mock", session)
        
        assert isinstance(instance, MockServiceNoRepo)

    def test_create_service_with_repository_dependency(self) -> None:
        """リポジトリ依存のサービスが正しく作成されることをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        session = Mock(spec=Session)
        
        # リポジトリを登録
        repo_registry.register("mock", MockRepository)
        # サービスを登録
        service_registry.register("mock", MockService)
        
        instance = service_registry.create("mock", session)
        
        assert isinstance(instance, MockService)
        assert isinstance(instance.mock_repo, MockRepository)
        assert instance.mock_repo.session is session

    def test_create_unregistered_service_raises_error(self) -> None:
        """未登録のサービス作成でエラーが発生することをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        session = Mock(spec=Session)
        
        with pytest.raises(RegistryError):
            service_registry.create("unregistered", session)

    def test_create_service_with_unresolved_dependency_raises_error(self) -> None:
        """解決できない依存性がある場合エラーが発生することをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        session = Mock(spec=Session)
        
        # リポジトリを登録しない状態でサービスを登録
        service_registry.register("mock", MockService)
        
        with pytest.raises(RegistryError):
            service_registry.create("mock", session)

    def test_get_registered_names(self) -> None:
        """登録名一覧が正しく取得されることをテスト"""
        repo_registry = RepositoryRegistry()
        service_registry = ServiceRegistry(repo_registry)
        
        service_registry.register("service1", MockServiceNoRepo)
        service_registry.register("service2", MockServiceNoRepo)
        
        names = service_registry.get_registered_names()
        assert set(names) == {"service1", "service2"}