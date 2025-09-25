#!/usr/bin/env python3
"""Simple test of the auto-discovery system"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import MagicMock, Mock, patch

from sqlmodel import Session

# Import our auto-discovery system
from logic.auto_discovery import AutoDiscovery
from logic.registry import get_repository_registry, get_service_registry


def test_name_conversion():
    """Test name conversion functions"""
    print("Testing name conversion...")

    discovery = AutoDiscovery()

    # Test snake_case conversion
    assert discovery._convert_to_snake_case("MemoService") == "memo_service"
    assert discovery._convert_to_snake_case("TaskTagRepository") == "task_tag_repository"
    assert discovery._convert_to_snake_case("OneLinearService") == "one_linear_service"
    assert discovery._convert_to_snake_case("Memo") == "memo"

    # Test repository name generation
    assert discovery._generate_repository_name("MemoRepository") == "memo"
    assert discovery._generate_repository_name("TaskTagRepository") == "task_tag"

    # Test service name generation
    assert discovery._generate_service_name("MemoService") == "memo"
    assert discovery._generate_service_name("OneLinerService") == "one_liner"

    print("✓ Name conversion tests passed")


def test_class_module_detection():
    """Test class module detection"""
    print("Testing class module detection...")

    discovery = AutoDiscovery()

    # Mock module and class
    mock_module = Mock()
    mock_module.__name__ = "test_module"

    mock_class = Mock()
    mock_class.__module__ = "test_module"

    mock_external_class = Mock()
    mock_external_class.__module__ = "external_module"

    # Test detection
    assert discovery._is_class_defined_in_module(mock_class, mock_module) is True
    assert discovery._is_class_defined_in_module(mock_external_class, mock_module) is False

    print("✓ Class module detection tests passed")


@patch("logic.auto_discovery.pkgutil.iter_modules")
@patch("logic.auto_discovery.importlib.import_module")
@patch("logic.auto_discovery.inspect.getmembers")
def test_repository_discovery(mock_getmembers, mock_import_module, mock_iter_modules):
    """Test repository discovery process"""
    print("Testing repository discovery...")

    discovery = AutoDiscovery()

    # Mock module info
    mock_module_info = Mock()
    mock_module_info.name = "memo"
    mock_iter_modules.return_value = [mock_module_info]

    # Mock module
    mock_module = Mock()
    mock_module.__name__ = "logic.repositories.memo"
    mock_import_module.return_value = mock_module

    # Mock repository class
    mock_repo_class = Mock()
    mock_repo_class.__module__ = "logic.repositories.memo"
    mock_getmembers.return_value = [("MemoRepository", mock_repo_class)]

    # Mock registry
    with patch.object(discovery.repository_registry, "register") as mock_register:
        discovery._discover_repositories()
        mock_register.assert_called_once_with("memo", mock_repo_class)

    print("✓ Repository discovery tests passed")


@patch("logic.auto_discovery.pkgutil.iter_modules")
@patch("logic.auto_discovery.importlib.import_module")
@patch("logic.auto_discovery.inspect.getmembers")
def test_service_discovery(mock_getmembers, mock_import_module, mock_iter_modules):
    """Test service discovery process"""
    print("Testing service discovery...")

    discovery = AutoDiscovery()

    # Mock module info
    mock_module_info = Mock()
    mock_module_info.name = "memo_service"
    mock_iter_modules.return_value = [mock_module_info]

    # Mock module
    mock_module = Mock()
    mock_module.__name__ = "logic.services.memo_service"
    mock_import_module.return_value = mock_module

    # Mock service class
    mock_service_class = Mock()
    mock_service_class.__module__ = "logic.services.memo_service"
    mock_getmembers.return_value = [("MemoService", mock_service_class)]

    # Mock registry
    with patch.object(discovery.service_registry, "register") as mock_register:
        discovery._discover_services()
        mock_register.assert_called_once_with("memo", mock_service_class)

    print("✓ Service discovery tests passed")


def test_list_registered_items():
    """Test listing registered items"""
    print("Testing list registered items...")

    discovery = AutoDiscovery()

    # Mock the registries
    with patch.object(discovery.repository_registry, "get_registered_names", return_value=["memo", "task"]):
        with patch.object(discovery.service_registry, "get_registered_names", return_value=["memo", "task"]):
            result = discovery.list_registered_items()

            expected = {"repositories": ["memo", "task"], "services": ["memo", "task"]}
            assert result == expected

    print("✓ List registered items tests passed")


if __name__ == "__main__":
    print("Running simple auto-discovery tests...")

    test_name_conversion()
    test_class_module_detection()
    test_repository_discovery()
    test_service_discovery()
    test_list_registered_items()

    print("\n✓ All auto-discovery tests passed!")
