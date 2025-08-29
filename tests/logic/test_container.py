"""Container テストモジュール

ServiceContainer の依存性注入とシングルトン動作をテストします。
"""

import pytest

from logic.application.project_application_service import ProjectApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.application.task_tag_application_service import TaskTagApplicationService
from logic.container import ServiceContainer

# [AI GENERATED] テスト用定数 - サービス設定のテストケース
SERVICE_TEST_CASES = [
    ("task", "get_task_application_service", TaskApplicationService),
    ("project", "get_project_application_service", ProjectApplicationService),
    ("tag", "get_tag_application_service", TagApplicationService),
    ("task_tag", "get_task_tag_application_service", TaskTagApplicationService),
]


class TestServiceContainer:
    """ServiceContainer のテストクラス

    依存性注入とシングルトンパターンの動作を検証します。
    """

    @pytest.mark.parametrize(("service_name", "method_name", "expected_class"), SERVICE_TEST_CASES)
    def test_get_service_creates_instance(self, service_name: str, method_name: str, expected_class: type) -> None:
        """各ApplicationServiceインスタンスが作成されることをテスト"""
        # Arrange
        container = ServiceContainer()

        # Act
        service = getattr(container, method_name)()

        # Assert
        assert isinstance(service, expected_class)

    @pytest.mark.parametrize(("service_name", "method_name", "expected_class"), SERVICE_TEST_CASES)
    def test_get_service_returns_singleton(self, service_name: str, method_name: str, expected_class: type) -> None:
        """各ApplicationServiceがシングルトンとして動作することをテスト"""
        # Arrange
        container = ServiceContainer()
        get_service = getattr(container, method_name)

        # Act
        service1 = get_service()
        service2 = get_service()

        # Assert - [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2
        assert isinstance(service1, expected_class)
        assert isinstance(service2, expected_class)

    def test_reset_clears_all_services(self) -> None:
        """reset() メソッドが全てのサービスインスタンスをクリアすることをテスト"""
        # Arrange
        container = ServiceContainer()

        # [AI GENERATED] 各サービスのインスタンスを取得
        services_before = {
            "task": container.get_task_application_service(),
            "project": container.get_project_application_service(),
            "tag": container.get_tag_application_service(),
            "task_tag": container.get_task_tag_application_service(),
        }

        # Act - [AI GENERATED] コンテナをリセット
        container.reset()

        # [AI GENERATED] リセット後に新しいインスタンスを取得
        services_after = {
            "task": container.get_task_application_service(),
            "project": container.get_project_application_service(),
            "tag": container.get_tag_application_service(),
            "task_tag": container.get_task_tag_application_service(),
        }

        # Assert - [AI GENERATED] 全て新しいインスタンスであることを確認
        for service_type, service_before in services_before.items():
            assert service_before is not services_after[service_type], (
                f"{service_type} service should be different after reset"
            )

    def test_all_services_are_independent(self) -> None:
        """各サービスが独立したインスタンスであることをテスト"""
        # Arrange
        container = ServiceContainer()

        # Act
        services = [
            container.get_task_application_service(),
            container.get_project_application_service(),
            container.get_tag_application_service(),
            container.get_task_tag_application_service(),
        ]

        # Assert - [AI GENERATED] 各サービスが異なるインスタンスであることを確認
        for i in range(len(services)):
            for j in range(i + 1, len(services)):
                assert services[i] is not services[j], (
                    f"Service at index {i} should be different from service at index {j}"
                )
