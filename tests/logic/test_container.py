"""Container テストモジュール

ServiceContainer の依存性注入とシングルトン動作をテストします。
"""

from logic.application.project_application_service import ProjectApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.application.task_tag_application_service import TaskTagApplicationService
from logic.container import ServiceContainer


class TestServiceContainer:
    """ServiceContainer のテストクラス

    依存性注入とシングルトンパターンの動作を検証します。
    """

    def test_get_task_application_service_creates_instance(self) -> None:
        """TaskApplicationService インスタンスが作成されることをテスト"""
        container = ServiceContainer()

        service = container.get_task_application_service()

        assert isinstance(service, TaskApplicationService)

    def test_get_task_application_service_returns_singleton(self) -> None:
        """TaskApplicationService がシングルトンとして動作することをテスト"""
        container = ServiceContainer()

        service1 = container.get_task_application_service()
        service2 = container.get_task_application_service()

        # [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2

    def test_get_project_application_service_creates_instance(self) -> None:
        """ProjectApplicationService インスタンスが作成されることをテスト"""
        container = ServiceContainer()

        service = container.get_project_application_service()

        assert isinstance(service, ProjectApplicationService)

    def test_get_project_application_service_returns_singleton(self) -> None:
        """ProjectApplicationService がシングルトンとして動作することをテスト"""
        container = ServiceContainer()

        service1 = container.get_project_application_service()
        service2 = container.get_project_application_service()

        # [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2

    def test_get_tag_application_service_creates_instance(self) -> None:
        """TagApplicationService インスタンスが作成されることをテスト"""
        container = ServiceContainer()

        service = container.get_tag_application_service()

        assert isinstance(service, TagApplicationService)

    def test_get_tag_application_service_returns_singleton(self) -> None:
        """TagApplicationService がシングルトンとして動作することをテスト"""
        container = ServiceContainer()

        service1 = container.get_tag_application_service()
        service2 = container.get_tag_application_service()

        # [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2

    def test_get_task_tag_application_service_creates_instance(self) -> None:
        """TaskTagApplicationService インスタンスが作成されることをテスト"""
        container = ServiceContainer()

        service = container.get_task_tag_application_service()

        assert isinstance(service, TaskTagApplicationService)

    def test_get_task_tag_application_service_returns_singleton(self) -> None:
        """TaskTagApplicationService がシングルトンとして動作することをテスト"""
        container = ServiceContainer()

        service1 = container.get_task_tag_application_service()
        service2 = container.get_task_tag_application_service()

        # [AI GENERATED] 同じインスタンスが返されることを確認
        assert service1 is service2

    def test_reset_clears_all_services(self) -> None:
        """reset() メソッドが全てのサービスインスタンスをクリアすることをテスト"""
        container = ServiceContainer()

        # [AI GENERATED] 各サービスのインスタンスを取得
        task_service1 = container.get_task_application_service()
        project_service1 = container.get_project_application_service()
        tag_service1 = container.get_tag_application_service()
        task_tag_service1 = container.get_task_tag_application_service()

        # [AI GENERATED] コンテナをリセット
        container.reset()

        # [AI GENERATED] リセット後に新しいインスタンスが作成されることを確認
        task_service2 = container.get_task_application_service()
        project_service2 = container.get_project_application_service()
        tag_service2 = container.get_tag_application_service()
        task_tag_service2 = container.get_task_tag_application_service()

        # [AI GENERATED] 全て新しいインスタンスであることを確認
        assert task_service1 is not task_service2
        assert project_service1 is not project_service2
        assert tag_service1 is not tag_service2
        assert task_tag_service1 is not task_tag_service2

    def test_all_services_are_independent(self) -> None:
        """各サービスが独立したインスタンスであることをテスト"""
        container = ServiceContainer()

        task_service = container.get_task_application_service()
        project_service = container.get_project_application_service()
        tag_service = container.get_tag_application_service()
        task_tag_service = container.get_task_tag_application_service()

        # [AI GENERATED] 各サービスが異なるインスタンスであることを確認
        assert task_service is not project_service
        assert task_service is not tag_service
        assert task_service is not task_tag_service
        assert project_service is not tag_service
        assert project_service is not task_tag_service
        assert tag_service is not task_tag_service
