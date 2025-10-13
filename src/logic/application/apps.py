from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any, TypeVar, cast

from loguru import logger

from logic.application.memo_application_service import MemoApplicationService
from logic.application.one_liner_application_service import OneLinerApplicationService
from logic.application.project_application_service import ProjectApplicationService
from logic.application.tag_application_service import TagApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.unit_of_work import SqlModelUnitOfWork, UnitOfWork

_S = TypeVar("_S")


class ApplicationServicesError(Exception):
    """ApplicationServicesコンテナで発生するエラー。"""


@dataclass
class ApplicationServices:
    """Application ServiceのDIコンテナ（遅延生成・スレッドセーフ）。

    - Viewや呼び出し側は`get_service(ServiceType)`でサービスを取得できます。
    - 各サービスはステートレス（UoWの境界はメソッド呼び出し時）なため、
      本コンテナで遅延生成・キャッシュして再利用します。

    推奨の使い方:
        >>> apps = ApplicationServices.create()
        >>> created_task = apps.task.create(title="新しいタスク")
    または:
        >>> task_app = apps.task  # または apps.get_service(TaskApplicationService)
        >>> created_task = task_app.create(title="新しいタスク")
    """

    _unit_of_work_factory: type[UnitOfWork]
    _services: dict[type[Any], Any]
    _lock: Lock

    # ---------- Factory ----------
    @classmethod
    def create(
        cls,
        *,
        unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork,
        memo: MemoApplicationService | None = None,
        project: ProjectApplicationService | None = None,
        tag: TagApplicationService | None = None,
        task: TaskApplicationService | None = None,
        one_liner: OneLinerApplicationService | None = None,
    ) -> ApplicationServices:
        """Application Servicesコンテナのファクトリメソッド。

        Args:
            unit_of_work_factory: UoWファクトリ（既定はSqlModelUnitOfWork）
            memo: テストや差し替え用のMemoApplicationServiceインスタンス
            project: 同上（ProjectApplicationService）
            tag: 同上（TagApplicationService）
            task: 同上（TaskApplicationService）
            one_liner: 同上（OneLinerApplicationService）

        Returns:
            ApplicationServices: 構築済みコンテナ
        """
        cache: dict[type[Any], Any] = {}
        if memo is not None:
            cache[MemoApplicationService] = memo
        if project is not None:
            cache[ProjectApplicationService] = project
        if tag is not None:
            cache[TagApplicationService] = tag
        if task is not None:
            cache[TaskApplicationService] = task
        if one_liner is not None:
            cache[OneLinerApplicationService] = one_liner

        return cls(
            _unit_of_work_factory=unit_of_work_factory,
            _services=cache,
            _lock=Lock(),
        )

    # ---------- Public API ----------
    def get_service(self, service_type: type[_S]) -> _S:
        """サービスを取得（遅延生成・キャッシュ）。

        Args:
            service_type: 取得したいサービスの型

        Returns:
            指定型のサービスインスタンス

        Raises:
            ApplicationServicesError: 生成失敗や型不一致時
        """
        # Fast path: 既存キャッシュ
        built = self._services.get(service_type)
        if built is not None:
            if not isinstance(built, service_type):
                msg = (
                    f"キャッシュされたサービスの型が不正です: 期待={service_type.__name__}, 実際={type(built).__name__}"
                )
                raise ApplicationServicesError(msg)
            return cast("_S", built)

        # Slow path: 同期して生成
        with self._lock:
            # ダブルチェック
            built2 = self._services.get(service_type)
            if built2 is not None:
                if not isinstance(built2, service_type):
                    msg = (
                        "キャッシュされたサービスの型が不正です: "
                        f"期待={service_type.__name__}, 実際={type(built2).__name__}"
                    )
                    raise ApplicationServicesError(msg)
                return cast("_S", built2)

            try:
                instance = self._build_service_instance(service_type)
                self._services[service_type] = instance
                logger.debug(
                    "ApplicationServices: %s を初期化しました (uow=%s)",
                    service_type.__name__,
                    self._unit_of_work_factory.__name__,
                )
                return cast("_S", instance)
            except Exception as e:  # pragma: no cover - 型や依存が壊れている場合
                logger.exception("ApplicationServices: %s の生成に失敗しました: %s", service_type.__name__, e)
                raise ApplicationServicesError(str(e)) from e

    def _build_service_instance(self, service_type: type[_S]) -> _S:
        """サービスインスタンスを生成する。

        優先順:
        1) build_serviceがあれば、引数数を見てUoWファクトリ付き or なしで呼ぶ
        2) コンストラクタにUoWファクトリを渡す
        3) 引数なしコンストラクタを呼ぶ

        Raises:
            ApplicationServicesError: 型不一致など
        """
        # 1) build_service 経由
        build = getattr(service_type, "build_service", None)
        if callable(build):
            try:
                argc = getattr(build, "__code__", None)
                if argc is not None and getattr(argc, "co_argcount", 1) == 1:
                    # cls のみ
                    instance = build()
                else:
                    instance = build(self._unit_of_work_factory)
                if isinstance(instance, service_type):
                    return cast("_S", instance)
            except Exception as e:  # build失敗時は次の手段へフォールバック
                logger.debug("build_service 経由の生成に失敗: %s", e)

        # 2) コンストラクタにUoW ファクトリを渡す
        try:
            instance2 = service_type(self._unit_of_work_factory)  # type: ignore[misc,call-arg]
            if isinstance(instance2, service_type):
                return cast("_S", instance2)
        except Exception as e:
            logger.debug("コンストラクタ(UoW引数あり) 経由の生成に失敗: %s", e)

        # 3) 引数なしコンストラクタ
        instance3 = service_type()  # type: ignore[call-arg]
        if not isinstance(instance3, service_type):
            msg = f"生成されたサービスの型が不正です: 期待={service_type.__name__}, 実際={type(instance3).__name__}"
            raise ApplicationServicesError(msg)
        return cast("_S", instance3)

    def reset(self) -> None:
        """キャッシュをクリア（テスト用）。"""
        with self._lock:
            self._services.clear()

    def configure(self, *, unit_of_work_factory: type[UnitOfWork] | None = None) -> None:
        """設定の変更（UoW差し替えなど、テストや特殊用途で使用）。

        Args:
            unit_of_work_factory: 差し替えるUoWファクトリ
        """
        with self._lock:
            if unit_of_work_factory is not None:
                self._unit_of_work_factory = unit_of_work_factory
            # 既存キャッシュは維持（必要に応じて reset() を別途呼ぶ）

    # ---------- Convenience properties ----------
    @property
    def memo(self) -> MemoApplicationService:
        """Memoサービスを取得。"""
        return self.get_service(MemoApplicationService)

    @property
    def project(self) -> ProjectApplicationService:
        """Projectサービスを取得。"""
        return self.get_service(ProjectApplicationService)

    @property
    def tag(self) -> TagApplicationService:
        """Tagサービスを取得。"""
        return self.get_service(TagApplicationService)

    @property
    def task(self) -> TaskApplicationService:
        """Taskサービスを取得。"""
        return self.get_service(TaskApplicationService)

    @property
    def one_liner(self) -> OneLinerApplicationService:
        """OneLinerサービスを取得。"""
        return self.get_service(OneLinerApplicationService)
