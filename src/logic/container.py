"""依存性注入コンテナ

Application Service層の依存性を管理するコンテナ
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.application.project_application_service import ProjectApplicationService
    from logic.application.tag_application_service import TagApplicationService
    from logic.application.task_application_service import TaskApplicationService


class ServiceContainer:
    """サービスコンテナ（Dependency Injection）

    Application Serviceの依存性を管理し、シングルトンパターンで提供します。
    """

    def __init__(self) -> None:
        """ServiceContainerの初期化"""
        self._task_app_service: TaskApplicationService | None = None
        self._project_app_service: ProjectApplicationService | None = None
        self._tag_app_service: TagApplicationService | None = None

    def get_task_application_service(self) -> TaskApplicationService:
        """タスクApplication Serviceを取得

        Returns:
            TaskApplicationService: タスクApplication Serviceインスタンス
        """
        if self._task_app_service is None:
            from logic.application.task_application_service import TaskApplicationService

            self._task_app_service = TaskApplicationService()
        return self._task_app_service

    def get_project_application_service(self) -> ProjectApplicationService:
        """プロジェクトApplication Serviceを取得

        Returns:
            ProjectApplicationService: プロジェクトApplication Serviceインスタンス
        """
        if self._project_app_service is None:
            from logic.application.project_application_service import ProjectApplicationService

            self._project_app_service = ProjectApplicationService()
        return self._project_app_service

    def get_tag_application_service(self) -> TagApplicationService:
        """タグApplication Serviceを取得

        Returns:
            TagApplicationService: タグApplication Serviceインスタンス
        """
        if self._tag_app_service is None:
            from logic.application.tag_application_service import TagApplicationService

            self._tag_app_service = TagApplicationService()
        return self._tag_app_service

    def reset(self) -> None:
        """コンテナをリセット（主にテスト用）"""
        self._task_app_service = None
        self._project_app_service = None
        self._tag_app_service = None


# グローバルなサービスコンテナのインスタンス
service_container = ServiceContainer()
