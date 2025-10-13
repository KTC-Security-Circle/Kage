"""タスク管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.task_service import TaskService
from logic.unit_of_work import SqlModelUnitOfWork
from models import TaskCreate, TaskRead, TaskStatus, TaskUpdate

if TYPE_CHECKING:
    import uuid


class TaskApplicationError(ApplicationError):
    """タスク管理のApplication Serviceで発生するエラー"""


class TaskContentValidationError(ValidationError, TaskApplicationError):
    """タスク内容のバリデーションエラー"""


class TaskApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """タスク管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        """TaskApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> TaskApplicationService: ...

    def create(self, title: str, description: str | None = None, *, status: TaskStatus | None = None) -> TaskRead:
        """タスクを作成する

        Args:
            title: タスクタイトル
            description: 詳細説明
            status: 初期ステータス（未指定時はモデル既定）

        Returns:
            TaskRead: 作成されたタスク

        Raises:
            TaskContentValidationError: タイトルが空の場合
        """
        if not title.strip():
            msg = "タスクタイトルを入力してください"
            raise TaskContentValidationError(msg)

        create_model = TaskCreate(title=title, description=description, status=status or TaskStatus.TODO)

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            created = task_service.create(create_model)

        logger.info(f"タスク作成完了 - (ID={created.id})")
        return created

    def update(self, task_id: uuid.UUID, update_data: TaskUpdate) -> TaskRead:
        """タスクを更新する

        Args:
            task_id: 更新対象タスクのID
            update_data: タスク更新データ

        Returns:
            TaskRead: 更新後タスク
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            updated = task_service.update(task_id, update_data)

        logger.info(f"タスク更新完了 - (ID={updated.id})")
        return updated

    def delete(self, task_id: uuid.UUID) -> bool:
        """タスク削除

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除成功フラグ
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            success = task_service.delete(task_id)
            logger.info(f"タスク削除完了: ID {task_id}, 結果: {success}")
            return success

    # 取得系
    def get_by_id(self, task_id: uuid.UUID, *, with_details: bool = False) -> TaskRead | None:
        """IDでタスク取得

        Args:
            task_id: タスクのID
            with_details: 関連エンティティも取得するか

        Returns:
            TaskRead | None: 見つかったタスク（存在しない場合None想定の呼び出し元もある）
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.get_by_id(task_id, with_details=with_details)

    def get_all_tasks(self) -> list[TaskRead]:
        """全タスク取得"""
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.get_all()

    def list_by_status(self, status: TaskStatus, *, with_details: bool = False) -> list[TaskRead]:
        """ステータスでタスク取得"""
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.list_by_status(status, with_details=with_details)
