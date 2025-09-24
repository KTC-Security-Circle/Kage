"""更新されたファクトリクラスのテスト"""

import warnings
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session

from logic.factory import RepositoryFactory, ServiceFactory
from logic.repositories.memo import MemoRepository
from logic.services.memo_service import MemoService


class TestRepositoryFactoryNew:
    """更新されたRepositoryFactoryのテストクラス"""

    @patch('logic.factory.initialize_auto_discovery')
    def test_initialization_calls_auto_discovery(self, mock_init_discovery) -> None:
        """初期化時に自動発見が呼ばれることをテスト"""
        session = Mock(spec=Session)
        
        RepositoryFactory(session)
        
        mock_init_discovery.assert_called_once()

    @patch('logic.factory.get_repository_registry')
    @patch('logic.factory.initialize_auto_discovery')
    def test_create_repository_using_registry(self, mock_init_discovery, mock_get_registry) -> None:
        """レジストリを使用したリポジトリ作成をテスト"""
        session = Mock(spec=Session)
        mock_registry = Mock()
        mock_registry.is_registered.return_value = True
        mock_registry.create.return_value = Mock(spec=MemoRepository)
        mock_get_registry.return_value = mock_registry
        
        factory = RepositoryFactory(session)
        result = factory.create("memo")
        
        mock_registry.is_registered.assert_called_once_with("memo")
        mock_registry.create.assert_called_once_with("memo", session)
        assert result is not None

    @patch('logic.factory.get_repository_registry')
    @patch('logic.factory.initialize_auto_discovery')
    def test_create_unregistered_repository_raises_error(self, mock_init_discovery, mock_get_registry) -> None:
        """未登録のリポジトリ作成でエラーが発生することをテスト"""
        session = Mock(spec=Session)
        mock_registry = Mock()
        mock_registry.is_registered.return_value = False
        mock_get_registry.return_value = mock_registry
        
        factory = RepositoryFactory(session)
        
        with pytest.raises(ValueError, match="Repository 'unknown' is not registered"):
            factory.create("unknown")

    @patch('logic.factory.get_repository_registry')
    @patch('logic.factory.initialize_auto_discovery')
    def test_get_available_repositories(self, mock_init_discovery, mock_get_registry) -> None:
        """利用可能なリポジトリ一覧取得をテスト"""
        session = Mock(spec=Session)
        mock_registry = Mock()
        mock_registry.get_registered_names.return_value = ["memo", "task", "project"]
        mock_get_registry.return_value = mock_registry
        
        factory = RepositoryFactory(session)
        result = factory.get_available_repositories()
        
        assert result == ["memo", "task", "project"]
        mock_registry.get_registered_names.assert_called_once()

    @patch('logic.factory.initialize_auto_discovery')
    def test_deprecated_create_memo_repository_shows_warning(self, mock_init_discovery) -> None:
        """非推奨メソッドで警告が表示されることをテスト"""
        session = Mock(spec=Session)
        factory = RepositoryFactory(session)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_memo_repository()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_memo_repository is deprecated" in str(w[0].message)

    @patch('logic.factory.initialize_auto_discovery')
    def test_deprecated_create_task_repository_shows_warning(self, mock_init_discovery) -> None:
        """非推奨メソッドで警告が表示されることをテスト"""
        session = Mock(spec=Session)
        factory = RepositoryFactory(session)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_task_repository()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_task_repository is deprecated" in str(w[0].message)


class TestServiceFactoryNew:
    """更新されたServiceFactoryのテストクラス"""

    @patch('logic.factory.initialize_auto_discovery')
    def test_initialization(self, mock_init_discovery) -> None:
        """初期化をテスト"""
        session = Mock(spec=Session)
        repo_factory = RepositoryFactory(session)
        
        service_factory = ServiceFactory(repo_factory)
        
        assert service_factory.repository_factory is repo_factory

    @patch('logic.factory.get_service_registry')
    def test_create_service_using_registry(self, mock_get_registry) -> None:
        """レジストリを使用したサービス作成をテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        repo_factory.session = session
        
        mock_registry = Mock()
        mock_registry.is_registered.return_value = True
        mock_registry.create.return_value = Mock(spec=MemoService)
        mock_get_registry.return_value = mock_registry
        
        factory = ServiceFactory(repo_factory)
        result = factory.create("memo")
        
        mock_registry.is_registered.assert_called_once_with("memo")
        mock_registry.create.assert_called_once_with("memo", session)
        assert result is not None

    @patch('logic.factory.get_service_registry')
    def test_create_unregistered_service_raises_error(self, mock_get_registry) -> None:
        """未登録のサービス作成でエラーが発生することをテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        repo_factory.session = session
        
        mock_registry = Mock()
        mock_registry.is_registered.return_value = False
        mock_get_registry.return_value = mock_registry
        
        factory = ServiceFactory(repo_factory)
        
        with pytest.raises(ValueError, match="Service 'unknown' is not registered"):
            factory.create("unknown")

    @patch('logic.factory.get_service_registry')
    def test_get_available_services(self, mock_get_registry) -> None:
        """利用可能なサービス一覧取得をテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        
        mock_registry = Mock()
        mock_registry.get_registered_names.return_value = ["memo", "task", "project"]
        mock_get_registry.return_value = mock_registry
        
        factory = ServiceFactory(repo_factory)
        result = factory.get_available_services()
        
        assert result == ["memo", "task", "project"]
        mock_registry.get_registered_names.assert_called_once()

    def test_deprecated_create_memo_service_shows_warning(self) -> None:
        """非推奨メソッドで警告が表示されることをテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        repo_factory.create_memo_repository.return_value = Mock(spec=MemoRepository)
        repo_factory.create_task_repository.return_value = Mock()
        
        factory = ServiceFactory(repo_factory)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_memo_service()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_memo_service is deprecated" in str(w[0].message)

    def test_deprecated_create_task_service_shows_warning(self) -> None:
        """非推奨メソッドで警告が表示されることをテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        repo_factory.create_task_repository.return_value = Mock()
        repo_factory.create_project_repository.return_value = Mock()
        repo_factory.create_tag_repository.return_value = Mock()
        repo_factory.create_task_tag_repository.return_value = Mock()
        
        factory = ServiceFactory(repo_factory)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_task_service()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_task_service is deprecated" in str(w[0].message)

    def test_deprecated_create_one_liner_service_shows_warning(self) -> None:
        """非推奨メソッドで警告が表示されることをテスト"""
        session = Mock(spec=Session)
        repo_factory = Mock(spec=RepositoryFactory)
        
        factory = ServiceFactory(repo_factory)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_one_liner_service()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_one_liner_service is deprecated" in str(w[0].message)