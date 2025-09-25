#!/usr/bin/env python3
"""Simple test of the registry system without complex dependencies"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import Mock

from sqlmodel import Session

# Import our registry system
from logic.registry import RegistryError, RepositoryRegistry, ServiceRegistry


class MockRepository:
    """Test repository"""

    def __init__(self, session: Session) -> None:
        self.session = session


class MockService:
    """Test service with repository dependency"""

    def __init__(self, mock_repo: MockRepository) -> None:
        self.mock_repo = mock_repo


class MockServiceNoRepo:
    """Test service without dependencies"""

    def __init__(self) -> None:
        pass


def test_repository_registry() -> None:
    """Test repository registry functionality"""
    print("Testing RepositoryRegistry...")

    registry = RepositoryRegistry()
    session = Mock(spec=Session)

    # Test registration
    registry.register("mock", MockRepository)
    assert registry.is_registered("mock")
    assert "mock" in registry.get_registered_names()

    # Test creation
    instance = registry.create("mock", session)
    assert isinstance(instance, MockRepository)
    assert instance.session is session

    print("✓ RepositoryRegistry tests passed")


def test_service_registry() -> None:
    """Test service registry functionality"""
    print("Testing ServiceRegistry...")

    repo_registry = RepositoryRegistry()
    service_registry = ServiceRegistry(repo_registry)
    session = Mock(spec=Session)

    # Register repository
    repo_registry.register("mock", MockRepository)

    # Register service without dependencies
    service_registry.register("mock_no_repo", MockServiceNoRepo)
    assert service_registry.is_registered("mock_no_repo")

    # Create service without dependencies
    instance = service_registry.create("mock_no_repo", session)
    assert isinstance(instance, MockServiceNoRepo)

    # Register service with repository dependency
    service_registry.register("mock", MockService)

    # Create service with dependencies
    instance = service_registry.create("mock", session)
    assert isinstance(instance, MockService)
    assert isinstance(instance.mock_repo, MockRepository)

    print("✓ ServiceRegistry tests passed")


def test_error_cases() -> None:
    """Test error handling"""
    print("Testing error cases...")

    repo_registry = RepositoryRegistry()
    service_registry = ServiceRegistry(repo_registry)
    session = Mock(spec=Session)

    # Test unregistered repository
    try:
        repo_registry.create("unregistered", session)
        msg = "Should have raised RegistryError"
        raise AssertionError(msg)
    except RegistryError:
        pass

    # Test unregistered service
    try:
        service_registry.create("unregistered", session)
        msg = "Should have raised RegistryError"
        raise AssertionError(msg)
    except RegistryError:
        pass

    print("✓ Error case tests passed")


if __name__ == "__main__":
    print("Running simple registry tests...")

    test_repository_registry()
    test_service_registry()
    test_error_cases()

    print("\n✓ All tests passed!")
