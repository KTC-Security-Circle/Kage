"""Container テストモジュール

ServiceContainer の依存性注入とシングルトン動作をテストします。
"""

import pytest

from logic.application.memo_application_service import MemoApplicationService
from logic.application.project_application_service import ProjectApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.application.task_tag_application_service import TaskTagApplicationService
from logic.container import ServiceContainer, ServiceContainerError

# [AI GENERATED] テスト対象のサービスクラス
SERVICE_TEST_CASES = [
    MemoApplicationService,
    TaskApplicationService,
    ProjectApplicationService,
    TagApplicationService,
    TaskTagApplicationService,
]


class TestServiceContainer:
    """ServiceContainer のテストクラス

    依存性注入とシングルトンパターンの動作を検証します。
    """

    @pytest.mark.parametrize("service_class", SERVICE_TEST_CASES)
    def test_get_service_creates_instance(self, service_class: type) -> None:
        """各ApplicationServiceインスタンスが作成されることをテスト"""
        # Arrange
        container = ServiceContainer()

        # Act
        service = container.get_service(service_class)

        # Assert
        assert isinstance(service, service_class)

    @pytest.mark.parametrize("service_class", SERVICE_TEST_CASES)
    def test_get_service_returns_singleton(self, service_class: type) -> None:
        """各ApplicationServiceがシングルトンとして動作することをテスト"""
        # Arrange
        container = ServiceContainer()

        # Act
        service1 = container.get_service(service_class)
        service2 = container.get_service(service_class)

        # Assert - [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2
        assert isinstance(service1, service_class)
        assert isinstance(service2, service_class)

    def test_reset_clears_all_services(self) -> None:
        """reset() メソッドが全てのサービスインスタンスをクリアすることをテスト"""
        # Arrange
        container = ServiceContainer()

        # [AI GENERATED] 各サービスのインスタンスを取得
        services_before = {service_class: container.get_service(service_class) for service_class in SERVICE_TEST_CASES}

        # Act - [AI GENERATED] コンテナをリセット
        container.reset()

        # [AI GENERATED] リセット後に新しいインスタンスを取得
        services_after = {service_class: container.get_service(service_class) for service_class in SERVICE_TEST_CASES}

        # Assert - [AI GENERATED] 全て新しいインスタンスであることを確認
        for service_class, service_before in services_before.items():
            assert service_before is not services_after[service_class], (
                f"{service_class.__name__} service should be different after reset"
            )

    def test_all_services_are_independent(self) -> None:
        """各サービスが独立したインスタンスであることをテスト"""
        # Arrange
        container = ServiceContainer()

        # Act
        services = [container.get_service(service_class) for service_class in SERVICE_TEST_CASES]

        # Assert - [AI GENERATED] 各サービスが異なるインスタンスであることを確認
        for i in range(len(services)):
            for j in range(i + 1, len(services)):
                assert services[i] is not services[j], (
                    f"Service at index {i} should be different from service at index {j}"
                )

    def test_get_service_raises_error_for_unregistered_service(self) -> None:
        """未登録のサービスを要求した場合に例外が発生することをテスト"""
        container = ServiceContainer()

        class DummyService:
            pass

        with pytest.raises(ServiceContainerError):
            container.get_service(DummyService)
