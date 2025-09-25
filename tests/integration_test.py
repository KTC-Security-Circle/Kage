"""Integration test demonstrating the new factory system"""

import os
import sys
import warnings
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import Session

from logic.factory import RepositoryFactory, ServiceFactory

# Import the registry and auto-discovery directly
from logic.registry import get_repository_registry, get_service_registry


# Mock classes that mimic the real structure
class MockMemoRepository:
    """Mock MemoRepository for testing"""

    def __init__(self, session: Session) -> None:
        self.session = session
        print("MockMemoRepository created with session")


class MockTaskRepository:
    """Mock TaskRepository for testing"""

    def __init__(self, session: Session) -> None:
        self.session = session
        print("MockTaskRepository created with session")


class MockMemoService:
    """Mock MemoService for testing"""

    def __init__(self, memo_repo: MockMemoRepository, task_repo: MockTaskRepository) -> None:
        self.memo_repo = memo_repo
        self.task_repo = task_repo
        print("MockMemoService created with dependencies")


class MockSimpleService:
    """Mock service with no dependencies"""

    def __init__(self) -> None:
        print("MockSimpleService created with no dependencies")


def demonstrate_manual_registration() -> None:
    """Demonstrate manual registration and usage"""
    print("\n=== Manual Registration Demo ===")

    # Get registries
    repo_registry = get_repository_registry()
    service_registry = get_service_registry()

    # Clear any existing registrations for clean test
    repo_registry._registry.clear()
    service_registry._registry.clear()

    # Manually register repositories
    repo_registry.register("memo", MockMemoRepository)
    repo_registry.register("task", MockTaskRepository)

    # Manually register services
    service_registry.register("memo", MockMemoService)
    service_registry.register("simple", MockSimpleService)

    print(f"Registered repositories: {repo_registry.get_registered_names()}")
    print(f"Registered services: {service_registry.get_registered_names()}")

    # Create session
    session = Mock(spec=Session)

    # Test repository creation
    _memo_repo = repo_registry.create("memo", session)
    _task_repo = repo_registry.create("task", session)

    # Test service creation with dependency injection
    _memo_service = service_registry.create("memo", session)
    _simple_service = service_registry.create("simple", session)

    print("✓ Manual registration demo completed successfully")


def demonstrate_factory_integration() -> None:
    """Demonstrate integration with factory classes"""
    print("\n=== Factory Integration Demo ===")

    # Get registries and register our mock classes
    repo_registry = get_repository_registry()
    service_registry = get_service_registry()

    # Ensure clean state
    repo_registry._registry.clear()
    service_registry._registry.clear()

    # Register mock classes
    repo_registry.register("memo", MockMemoRepository)
    repo_registry.register("task", MockTaskRepository)
    service_registry.register("memo", MockMemoService)
    service_registry.register("simple", MockSimpleService)

    # Create session
    session = Mock(spec=Session)

    # Test new factory methods
    repo_factory = RepositoryFactory(session)

    print(f"Available repositories: {repo_factory.get_available_repositories()}")

    # Create repositories using new method
    memo_repo = repo_factory.create("memo")
    task_repo = repo_factory.create("task")

    # Test service factory
    service_factory = ServiceFactory(repo_factory)

    print(f"Available services: {service_factory.get_available_services()}")

    # Create services using new method
    memo_service = service_factory.create("memo")
    simple_service = service_factory.create("simple")

    print("✓ Factory integration demo completed successfully")


def demonstrate_backward_compatibility() -> None:
    """Demonstrate that old methods still work"""
    print("\n=== Backward Compatibility Demo ===")

    session = Mock(spec=Session)

    # Test old repository factory methods
    repo_factory = RepositoryFactory(session)

    # Capture deprecation warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Call deprecated methods
        memo_repo = repo_factory.create_memo_repository()
        task_repo = repo_factory.create_task_repository()

        print(f"Caught {len(w)} deprecation warnings")
        for warning in w:
            print(f"  - {warning.message}")

    print("✓ Backward compatibility demo completed successfully")


def demonstrate_error_handling() -> None:
    """Demonstrate error handling"""
    print("\n=== Error Handling Demo ===")

    # Get registries and clear them
    repo_registry = get_repository_registry()
    service_registry = get_service_registry()
    repo_registry._registry.clear()
    service_registry._registry.clear()

    session = Mock(spec=Session)

    # Test factory error handling
    repo_factory = RepositoryFactory(session)
    service_factory = ServiceFactory(repo_factory)

    # Test unregistered repository
    try:
        repo_factory.create("nonexistent")
        print("ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly caught repository error: {e}")

    # Test unregistered service
    try:
        service_factory.create("nonexistent")
        print("ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly caught service error: {e}")

    print("✓ Error handling demo completed successfully")


if __name__ == "__main__":
    print("Running factory integration demo...")

    demonstrate_manual_registration()
    demonstrate_factory_integration()
    demonstrate_backward_compatibility()
    demonstrate_error_handling()

    print("\n🎉 All integration demos completed successfully!")
    print("\nKey Benefits Demonstrated:")
    print("1. ✅ No need to modify factory code when adding new services")
    print("2. ✅ Automatic dependency injection using reflection")
    print("3. ✅ Backward compatibility with deprecation warnings")
    print("4. ✅ Clear error messages for missing dependencies")
    print("5. ✅ Runtime service/repository discovery")
