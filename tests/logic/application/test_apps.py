from __future__ import annotations

from typing import Self
from unittest.mock import Mock

import pytest

from logic.application.apps import ApplicationServices, ApplicationServicesError
from logic.application.memo_application_service import MemoApplicationService
from logic.application.one_liner_application_service import OneLinerApplicationService
from logic.application.project_application_service import ProjectApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.unit_of_work import SqlModelUnitOfWork, UnitOfWork


class BuildOnlyService:
    called: bool = False

    @classmethod
    def build_service(cls) -> BuildOnlyService:
        cls.called = True
        return cls()


class BuildWithFactoryService:
    received_factory: type[UnitOfWork] | None = None

    @classmethod
    def build_service(cls, factory: type[UnitOfWork]) -> BuildWithFactoryService:
        cls.received_factory = factory
        return cls()


class BuildServiceRaises:
    def __init__(self, factory: type[UnitOfWork]) -> None:
        self.received_factory = factory

    @classmethod
    def build_service(cls, factory: type[UnitOfWork]) -> BuildServiceRaises:
        msg = "build failure"
        raise RuntimeError(msg)


class CtorWithFactoryService:
    def __init__(self, factory: type[UnitOfWork]) -> None:
        self.received_factory = factory


class CtorNoArgService:
    initialized: bool = False

    def __init__(self) -> None:
        self.initialized = True


class StubOneLinerApplicationService(OneLinerApplicationService):
    def __init__(self) -> None:
        # LLM初期化を避けるために最低限の属性のみを設定
        self._unit_of_work_factory = SqlModelUnitOfWork


class InjectingLock:
    def __init__(self, apps: ApplicationServices, service_type: type[BuildOnlyService]) -> None:
        self._apps = apps
        self._service_type = service_type
        self.entered = False

    def __enter__(self) -> Self:
        self.entered = True
        self._apps._services[self._service_type] = object()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        self._apps._services.pop(self._service_type, None)
        return False


class ValidInjectingLock:
    def __init__(
        self,
        apps: ApplicationServices,
        service_type: type[BuildOnlyService],
        instance: BuildOnlyService,
    ) -> None:
        self._apps = apps
        self._service_type = service_type
        self._instance = instance
        self.entered = False

    def __enter__(self) -> Self:
        self.entered = True
        self._apps._services[self._service_type] = self._instance
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        return False


def test_get_service_returns_cached_instance() -> None:
    memo = MemoApplicationService()
    apps = ApplicationServices.create(memo=memo)

    assert apps.memo is memo


def test_get_service_via_build_service_without_factory() -> None:
    BuildOnlyService.called = False
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    service = apps.get_service(BuildOnlyService)

    assert isinstance(service, BuildOnlyService)
    assert BuildOnlyService.called is True


def test_get_service_via_build_service_with_factory() -> None:
    BuildWithFactoryService.received_factory = None
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    service = apps.get_service(BuildWithFactoryService)

    assert isinstance(service, BuildWithFactoryService)
    assert BuildWithFactoryService.received_factory is SqlModelUnitOfWork


def test_get_service_via_constructor_with_factory() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    service = apps.get_service(CtorWithFactoryService)

    assert isinstance(service, CtorWithFactoryService)
    assert service.received_factory is SqlModelUnitOfWork


def test_get_service_via_constructor_without_factory() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    service = apps.get_service(CtorNoArgService)

    assert isinstance(service, CtorNoArgService)
    assert service.initialized is True


def test_reset_clears_cache() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)
    apps.get_service(CtorNoArgService)

    assert CtorNoArgService in apps._services
    apps.reset()
    assert apps._services == {}


def test_configure_updates_unit_of_work_factory() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    class AnotherUnitOfWork(SqlModelUnitOfWork):
        pass

    apps.configure(unit_of_work_factory=AnotherUnitOfWork)
    service = apps.get_service(CtorWithFactoryService)

    assert service.received_factory is AnotherUnitOfWork


def test_configure_without_arguments_preserves_factory_and_cache() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)
    cached = apps.get_service(CtorNoArgService)

    apps.configure()

    assert apps._unit_of_work_factory is SqlModelUnitOfWork
    assert apps._services[CtorNoArgService] is cached


def test_get_service_raises_on_cached_type_mismatch() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)
    apps._services[BuildOnlyService] = Mock()

    with pytest.raises(ApplicationServicesError):
        apps.get_service(BuildOnlyService)


def test_get_service_detects_type_change_during_lock() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)
    apps._lock = InjectingLock(apps, BuildOnlyService)  # type: ignore[assignment]

    with pytest.raises(ApplicationServicesError):
        apps.get_service(BuildOnlyService)

    assert apps._lock.entered is True  # type: ignore[attr-defined]


def test_get_service_returns_instance_inserted_during_lock() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)
    cached_instance = BuildOnlyService()
    apps._lock = ValidInjectingLock(apps, BuildOnlyService, cached_instance)  # type: ignore[assignment]

    result = apps.get_service(BuildOnlyService)

    assert result is cached_instance
    assert apps._lock.entered is True  # type: ignore[attr-defined]


def test_get_service_raises_when_constructor_returns_wrong_type() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    class BrokenService:
        def __new__(cls, *args: object, **kwargs: object) -> object:
            if args or kwargs:
                return super().__new__(cls)
            return object()

        def __init__(self, *args: object, **kwargs: object) -> None:
            if args:
                msg = "ctor failure"
                raise RuntimeError(msg)

    with pytest.raises(ApplicationServicesError) as exc:
        apps.get_service(BrokenService)

    assert "生成されたサービスの型が不正" in str(exc.value)


def test_build_service_failure_falls_back_to_constructor() -> None:
    apps = ApplicationServices.create(unit_of_work_factory=SqlModelUnitOfWork)

    service = apps.get_service(BuildServiceRaises)

    assert isinstance(service, BuildServiceRaises)
    assert service.received_factory is SqlModelUnitOfWork


def test_convenience_properties_return_preconfigured_services() -> None:
    memo_service = MemoApplicationService()
    project_service = ProjectApplicationService()
    tag_service = TagApplicationService()
    task_service = TaskApplicationService()
    one_liner_service = StubOneLinerApplicationService()

    apps = ApplicationServices.create(
        memo=memo_service,
        project=project_service,
        tag=tag_service,
        task=task_service,
        one_liner=one_liner_service,
        unit_of_work_factory=SqlModelUnitOfWork,
    )

    assert apps.memo is memo_service
    assert apps.project is project_service
    assert apps.tag is tag_service
    assert apps.task is task_service
    assert apps.one_liner is one_liner_service
