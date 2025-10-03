"""依存性注入コンテナ

Application Service層の依存性を管理するコンテナ
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Callable

_ApplicationServiceT = TypeVar("_ApplicationServiceT")


class ServiceContainerError(Exception):
    """ServiceContainer に関連する例外"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ServiceContainer:
    """サービスコンテナ（Dependency Injection）

    Application Serviceの依存性を管理し、必要に応じて遅延初期化したシングルトンとして提供します。
    """

    def __init__(self) -> None:
        """ServiceContainerの初期化"""
        self._service_builders: dict[type[object], Callable[[ServiceContainer], object]] = {}
        self._service_instances: dict[type[object], object] = {}
        self._defaults_registered = False

    def register_service(
        self,
        service_type: type[_ApplicationServiceT],
        builder: Callable[[ServiceContainer], _ApplicationServiceT],
    ) -> None:
        """Application Service を登録する

        Args:
            service_type: 登録対象のApplication Serviceクラス
            builder: Application Serviceインスタンスを生成するビルダー
        """
        self._service_builders[service_type] = cast("Callable[[ServiceContainer], object]", builder)

    def get_service(self, service_type: type[_ApplicationServiceT]) -> _ApplicationServiceT:
        """登録済みのApplication Serviceを取得する

        遅延初期化を行い、初回アクセス時にビルダーを使用してインスタンスを生成します。

        Args:
            service_type: 取得対象のApplication Serviceクラス

        Returns:
            Application Serviceインスタンス

        Raises:
            ServiceContainerError: 未登録のサービスが要求された場合、または生成に失敗した場合
        """
        instance = self._service_instances.get(service_type)
        if instance is not None:
            return cast("_ApplicationServiceT", instance)

        builder = self._service_builders.get(service_type)
        if builder is None and not self._defaults_registered:
            self.register_default_services()
            builder = self._service_builders.get(service_type)
        if builder is None:
            message = f"ServiceContainerに登録されていないサービスが要求されました: {service_type.__name__}"
            raise ServiceContainerError(message)

        try:
            instance = builder(self)
        except Exception as exc:
            message = f"ServiceContainerでサービスの初期化に失敗しました: {service_type.__name__}"
            raise ServiceContainerError(message) from exc

        self._service_instances[service_type] = instance
        return cast("_ApplicationServiceT", instance)

    def reset(self) -> None:
        """コンテナをリセット（主にテスト用）"""
        self._service_instances.clear()

    def register_default_services(self) -> None:
        """アプリケーションで使用するデフォルトのサービスを登録する"""
        if self._defaults_registered:
            return

        from logic.application.memo_application_service import MemoApplicationService
        from logic.application.one_liner_application_service import OneLinerApplicationService
        from logic.application.project_application_service import ProjectApplicationService
        from logic.application.tag_application_service import TagApplicationService
        from logic.application.task_application_service import TaskApplicationService
        from logic.application.task_tag_application_service import TaskTagApplicationService

        self.register_service(MemoApplicationService, lambda _: MemoApplicationService())
        self.register_service(TaskApplicationService, lambda _: TaskApplicationService())
        self.register_service(ProjectApplicationService, lambda _: ProjectApplicationService())
        self.register_service(TagApplicationService, lambda _: TagApplicationService())
        self.register_service(TaskTagApplicationService, lambda _: TaskTagApplicationService())
        self.register_service(OneLinerApplicationService, lambda _: OneLinerApplicationService())
        self._defaults_registered = True


# グローバルなサービスコンテナのインスタンス
service_container = ServiceContainer()
