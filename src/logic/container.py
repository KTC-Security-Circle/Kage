"""依存性注入コンテナ

Application Service層の依存性を管理するコンテナ
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService


class ServiceContainer:
    """サービスコンテナ（Dependency Injection）

    Application Serviceの依存性を管理し、シングルトンパターンで提供します。
    """

    def __init__(self) -> None:
        """ServiceContainerの初期化"""
        self._task_app_service: TaskApplicationService | None = None

    def get_task_application_service(self) -> TaskApplicationService:
        """タスクApplication Serviceを取得

        Returns:
            TaskApplicationService: タスクApplication Serviceインスタンス
        """
        if self._task_app_service is None:
            from logic.application.task_application_service import TaskApplicationService

            self._task_app_service = TaskApplicationService()
        return self._task_app_service

    def reset(self) -> None:
        """コンテナをリセット（主にテスト用）"""
        self._task_app_service = None


# グローバルなサービスコンテナのインスタンス
service_container = ServiceContainer()
