#!/usr/bin/env python3
"""Simple test of the updated factory system"""

import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import Mock, patch

from sqlmodel import Session

# Import our factory system
from logic.factory import RepositoryFactory, ServiceFactory


def test_repository_factory_new_methods():
    """Test new repository factory methods"""
    print("Testing new RepositoryFactory methods...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        with patch("logic.factory.get_repository_registry") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.is_registered.return_value = True
            mock_registry.create.return_value = Mock()
            mock_registry.get_registered_names.return_value = ["memo", "task"]
            mock_get_registry.return_value = mock_registry

            factory = RepositoryFactory(session)

            # Test create method
            result = factory.create("memo")
            assert result is not None
            mock_registry.create.assert_called_with("memo", session)

            # Test get_available_repositories
            available = factory.get_available_repositories()
            assert available == ["memo", "task"]

            # Test error case
            mock_registry.is_registered.return_value = False
            try:
                factory.create("unknown")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "not registered" in str(e)

    print("✓ New RepositoryFactory methods tests passed")


def test_service_factory_new_methods():
    """Test new service factory methods"""
    print("Testing new ServiceFactory methods...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        repo_factory = Mock()
        repo_factory.session = session

        with patch("logic.factory.get_service_registry") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.is_registered.return_value = True
            mock_registry.create.return_value = Mock()
            mock_registry.get_registered_names.return_value = ["memo", "task"]
            mock_get_registry.return_value = mock_registry

            factory = ServiceFactory(repo_factory)

            # Test create method
            result = factory.create("memo")
            assert result is not None
            mock_registry.create.assert_called_with("memo", session)

            # Test get_available_services
            available = factory.get_available_services()
            assert available == ["memo", "task"]

            # Test error case
            mock_registry.is_registered.return_value = False
            try:
                factory.create("unknown")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "not registered" in str(e)

    print("✓ New ServiceFactory methods tests passed")


def test_deprecation_warnings():
    """Test that deprecated methods show warnings"""
    print("Testing deprecation warnings...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        # Test repository factory deprecation
        factory = RepositoryFactory(session)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            factory.create_memo_repository()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_memo_repository is deprecated" in str(w[0].message)

        # Test service factory deprecation
        repo_factory = Mock()
        repo_factory.create_memo_repository.return_value = Mock()
        repo_factory.create_task_repository.return_value = Mock()

        service_factory = ServiceFactory(repo_factory)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            service_factory.create_memo_service()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "create_memo_service is deprecated" in str(w[0].message)

    print("✓ Deprecation warnings tests passed")


def test_backward_compatibility():
    """Test that old methods still work"""
    print("Testing backward compatibility...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        factory = RepositoryFactory(session)

        # Suppress warnings for this test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Test that old methods still return objects
            memo_repo = factory.create_memo_repository()
            assert memo_repo is not None

            task_repo = factory.create_task_repository()
            assert task_repo is not None

            project_repo = factory.create_project_repository()
            assert project_repo is not None

    print("✓ Backward compatibility tests passed")


if __name__ == "__main__":
    print("Running simple factory tests...")

    test_repository_factory_new_methods()
    test_service_factory_new_methods()
    test_deprecation_warnings()
    test_backward_compatibility()

    print("\n✓ All factory tests passed!")
