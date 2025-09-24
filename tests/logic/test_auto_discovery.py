"""自動発見システムのテスト"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from logic.auto_discovery import AutoDiscovery
from logic.registry import RepositoryRegistry, ServiceRegistry


class TestAutoDiscovery:
    """AutoDiscoveryのテストクラス"""

    def test_convert_to_snake_case(self) -> None:
        """PascalCaseからsnake_caseへの変換をテスト"""
        discovery = AutoDiscovery()
        
        # 基本的な変換
        assert discovery._convert_to_snake_case("MemoService") == "memo_service"
        assert discovery._convert_to_snake_case("TaskTagRepository") == "task_tag_repository"
        assert discovery._convert_to_snake_case("OneLinearService") == "one_linear_service"
        
        # 単語が1つの場合
        assert discovery._convert_to_snake_case("Memo") == "memo"
        
        # 既にlowercaseの場合
        assert discovery._convert_to_snake_case("memo") == "memo"

    def test_generate_repository_name(self) -> None:
        """リポジトリ名生成をテスト"""
        discovery = AutoDiscovery()
        
        assert discovery._generate_repository_name("MemoRepository") == "memo"
        assert discovery._generate_repository_name("TaskRepository") == "task"
        assert discovery._generate_repository_name("TaskTagRepository") == "task_tag"

    def test_generate_service_name(self) -> None:
        """サービス名生成をテスト"""
        discovery = AutoDiscovery()
        
        assert discovery._generate_service_name("MemoService") == "memo"
        assert discovery._generate_service_name("TaskService") == "task"
        assert discovery._generate_service_name("OneLinerService") == "one_liner"

    def test_is_class_defined_in_module(self) -> None:
        """クラスがモジュール内で定義されているかの判定をテスト"""
        discovery = AutoDiscovery()
        
        # モックモジュールとクラス
        mock_module = Mock()
        mock_module.__name__ = "test_module"
        
        mock_class = Mock()
        mock_class.__module__ = "test_module"
        
        mock_external_class = Mock()
        mock_external_class.__module__ = "external_module"
        
        # 同一モジュール内で定義されたクラス
        assert discovery._is_class_defined_in_module(mock_class, mock_module) is True
        
        # 外部モジュールで定義されたクラス
        assert discovery._is_class_defined_in_module(mock_external_class, mock_module) is False

    @patch('logic.auto_discovery.pkgutil.iter_modules')
    @patch('logic.auto_discovery.importlib.import_module')
    @patch('logic.auto_discovery.inspect.getmembers')
    def test_discover_repositories(self, mock_getmembers, mock_import_module, mock_iter_modules) -> None:
        """リポジトリ自動発見をテスト"""
        discovery = AutoDiscovery()
        
        # モックモジュール情報
        mock_module_info = Mock()
        mock_module_info.name = "memo"
        mock_iter_modules.return_value = [mock_module_info]
        
        # モックモジュール
        mock_module = Mock()
        mock_module.__name__ = "logic.repositories.memo"
        mock_import_module.return_value = mock_module
        
        # モックリポジトリクラス
        mock_repo_class = Mock()
        mock_repo_class.__module__ = "logic.repositories.memo"
        mock_getmembers.return_value = [("MemoRepository", mock_repo_class)]
        
        # レジストリのモック
        with patch.object(discovery.repository_registry, 'register') as mock_register:
            discovery._discover_repositories()
            mock_register.assert_called_once_with("memo", mock_repo_class)

    @patch('logic.auto_discovery.pkgutil.iter_modules')
    @patch('logic.auto_discovery.importlib.import_module')
    @patch('logic.auto_discovery.inspect.getmembers')
    def test_discover_services(self, mock_getmembers, mock_import_module, mock_iter_modules) -> None:
        """サービス自動発見をテスト"""
        discovery = AutoDiscovery()
        
        # モックモジュール情報
        mock_module_info = Mock()
        mock_module_info.name = "memo_service"
        mock_iter_modules.return_value = [mock_module_info]
        
        # モックモジュール
        mock_module = Mock()
        mock_module.__name__ = "logic.services.memo_service"
        mock_import_module.return_value = mock_module
        
        # モックサービスクラス
        mock_service_class = Mock()
        mock_service_class.__module__ = "logic.services.memo_service"
        mock_getmembers.return_value = [("MemoService", mock_service_class)]
        
        # レジストリのモック
        with patch.object(discovery.service_registry, 'register') as mock_register:
            discovery._discover_services()
            mock_register.assert_called_once_with("memo", mock_service_class)

    @patch('logic.auto_discovery.pkgutil.iter_modules')
    @patch('logic.auto_discovery.importlib.import_module')
    def test_discover_repositories_skip_invalid_modules(self, mock_import_module, mock_iter_modules) -> None:
        """無効なモジュールをスキップすることをテスト"""
        discovery = AutoDiscovery()
        
        # __で始まるモジュール（スキップされるべき）
        mock_module_info = Mock()
        mock_module_info.name = "__init__"
        mock_iter_modules.return_value = [mock_module_info]
        
        discovery._discover_repositories()
        
        # import_moduleが呼ばれないことを確認
        mock_import_module.assert_not_called()

    @patch('logic.auto_discovery.pkgutil.iter_modules')
    @patch('logic.auto_discovery.importlib.import_module')
    def test_discover_services_skip_base_module(self, mock_import_module, mock_iter_modules) -> None:
        """baseモジュールをスキップすることをテスト"""
        discovery = AutoDiscovery()
        
        # baseモジュール（スキップされるべき）
        mock_module_info = Mock()
        mock_module_info.name = "base"
        mock_iter_modules.return_value = [mock_module_info]
        
        discovery._discover_services()
        
        # import_moduleが呼ばれないことを確認
        mock_import_module.assert_not_called()

    def test_list_registered_items(self) -> None:
        """登録されたアイテム一覧取得をテスト"""
        discovery = AutoDiscovery()
        
        # レジストリにモックデータを設定
        with patch.object(discovery.repository_registry, 'get_registered_names', return_value=["memo", "task"]):
            with patch.object(discovery.service_registry, 'get_registered_names', return_value=["memo", "task"]):
                result = discovery.list_registered_items()
                
                expected = {
                    "repositories": ["memo", "task"],
                    "services": ["memo", "task"]
                }
                assert result == expected

    @patch('logic.auto_discovery.AutoDiscovery._discover_repositories')
    @patch('logic.auto_discovery.AutoDiscovery._discover_services')
    def test_discover_and_register_all(self, mock_discover_services, mock_discover_repos) -> None:
        """全体の自動発見プロセスをテスト"""
        discovery = AutoDiscovery()
        
        discovery.discover_and_register_all()
        
        # 両方のメソッドが呼ばれることを確認
        mock_discover_repos.assert_called_once()
        mock_discover_services.assert_called_once()