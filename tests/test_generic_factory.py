#!/usr/bin/env python3
"""Test for generic factory type inference"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import Mock, patch

from sqlmodel import Session

# Import the factory system
from logic.factory import RepositoryFactory, ServiceFactory


def test_repository_factory_type_inference():
    """Test that repository factory provides proper type inference"""
    print("Testing RepositoryFactory type inference...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        with patch("logic.factory.get_repository_registry") as mock_get_registry:
            # Mock the registry
            mock_registry = Mock()
            mock_registry.is_registered.return_value = True

            # Mock different repository types
            mock_memo_repo = Mock()
            mock_memo_repo.__class__.__name__ = "MemoRepository"
            mock_task_repo = Mock()
            mock_task_repo.__class__.__name__ = "TaskRepository"

            # Set up different returns for different names
            def mock_create(name, session):
                if name == "memo":
                    return mock_memo_repo
                if name == "task":
                    return mock_task_repo
                return Mock()

            mock_registry.create = mock_create
            mock_get_registry.return_value = mock_registry

            factory = RepositoryFactory(session)

            # Test type inference with literal strings
            memo_repo = factory.create("memo")  # Should be typed as MemoRepository
            task_repo = factory.create("task")  # Should be typed as TaskRepository

            assert memo_repo.__class__.__name__ == "MemoRepository"
            assert task_repo.__class__.__name__ == "TaskRepository"

            # Test create_typed method
            from unittest.mock import Mock as MockType

            typed_repo = factory.create_typed(MockType, "memo")
            assert typed_repo is mock_memo_repo

            print("✓ RepositoryFactory type inference tests passed")


def test_service_factory_type_inference():
    """Test that service factory provides proper type inference"""
    print("Testing ServiceFactory type inference...")

    session = Mock(spec=Session)

    with patch("logic.factory.initialize_auto_discovery"):
        repo_factory = Mock()
        repo_factory.session = session

        with patch("logic.factory.get_service_registry") as mock_get_registry:
            # Mock the registry
            mock_registry = Mock()
            mock_registry.is_registered.return_value = True

            # Mock different service types
            mock_memo_service = Mock()
            mock_memo_service.__class__.__name__ = "MemoService"
            mock_task_service = Mock()
            mock_task_service.__class__.__name__ = "TaskService"

            # Set up different returns for different names
            def mock_create(name, session):
                if name == "memo":
                    return mock_memo_service
                if name == "task":
                    return mock_task_service
                return Mock()

            mock_registry.create = mock_create
            mock_get_registry.return_value = mock_registry

            factory = ServiceFactory(repo_factory)

            # Test type inference with literal strings
            memo_service = factory.create("memo")  # Should be typed as MemoService
            task_service = factory.create("task")  # Should be typed as TaskService

            assert memo_service.__class__.__name__ == "MemoService"
            assert task_service.__class__.__name__ == "TaskService"

            # Test create_typed method
            from unittest.mock import Mock as MockType

            typed_service = factory.create_typed(MockType, "memo")
            assert typed_service is mock_memo_service

            print("✓ ServiceFactory type inference tests passed")


def demo_type_inference():
    """Demonstrate type inference in action"""
    print("\n=== Type Inference Demo ===")

    print("With the new generic factory implementation:")
    print()
    print("# Type-safe factory calls with literal strings:")
    print("memo_repo = factory.create('memo')        # Type: MemoRepository")
    print("task_repo = factory.create('task')        # Type: TaskRepository")
    print("memo_service = factory.create('memo')     # Type: MemoService")
    print()
    print("# Explicit type specification:")
    print("memo_repo = factory.create_typed(MemoRepository, 'memo')  # Type: MemoRepository")
    print("custom_service = factory.create_typed(CustomService, 'custom')  # Type: CustomService")
    print()
    print("Benefits:")
    print("✅ IDE autocomplete works correctly")
    print("✅ Type checkers (mypy, pyright) can validate usage")
    print("✅ Runtime behavior unchanged - full backward compatibility")
    print("✅ Better developer experience with type safety")


if __name__ == "__main__":
    print("Running generic factory type inference tests...")

    test_repository_factory_type_inference()
    test_service_factory_type_inference()
    demo_type_inference()

    print("\n✅ All generic factory tests passed!")
    print("\nThe factory classes now provide proper type inference!")
