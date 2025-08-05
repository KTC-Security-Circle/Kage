"""タスク管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from logic.commands.task_commands import (
        CreateTaskCommand,
        DeleteTaskCommand,
        UpdateTaskCommand,
        UpdateTaskStatusCommand,
    )
    from logic.queries.task_queries import (
        GetTaskByIdQuery,
        GetTasksByStatusQuery,
    )
    from logic.unit_of_work import UnitOfWork
    from models import TaskRead, TaskStatus


class TaskApplicationService(BaseApplicationService):
    """タスク管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork) -> None:
        """TaskApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_task(self, command: CreateTaskCommand) -> TaskRead:
        """タスク作成

        Args:
            command: タスク作成コマンド

        Returns:
            作成されたタスク

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"タスク作成開始: {command.title}")

        # バリデーション
        if not command.title.strip():
            msg = "タスクタイトルを入力してください"
            raise ValueError(msg)

        # Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            created_task = task_service.create_task(command.to_task_create())
            uow.commit()

            logger.info(f"タスク作成完了: {created_task.title} (ID: {created_task.id})")
            return created_task

    def update_task(self, command: UpdateTaskCommand) -> TaskRead:
        """タスク更新

        Args:
            command: タスク更新コマンド

        Returns:
            更新されたタスク

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 更新エラー
        """
        logger.info(f"タスク更新開始: {command.task_id}")

        # バリデーション
        if not command.title.strip():
            msg = "タスクタイトルを入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            updated_task = task_service.update_task(command.task_id, command.to_task_update())
            uow.commit()

            logger.info(f"タスク更新完了: {updated_task.title} (ID: {updated_task.id})")
            return updated_task

    def delete_task(self, command: DeleteTaskCommand) -> None:
        """タスク削除

        Args:
            command: タスク削除コマンド

        Raises:
            RuntimeError: 削除エラー
        """
        logger.info(f"タスク削除開始: {command.task_id}")

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            task_service.delete_task(command.task_id)
            uow.commit()

            logger.info(f"タスク削除完了: {command.task_id}")

    def update_task_status(self, command: UpdateTaskStatusCommand) -> TaskRead:
        """タスクステータス更新

        Args:
            command: タスクステータス更新コマンド

        Returns:
            更新されたタスク

        Raises:
            RuntimeError: 更新エラー
        """
        logger.info(f"タスクステータス更新開始: {command.task_id} -> {command.new_status.value}")

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()

            # 現在のタスクを取得
            task = task_service.get_task_by_id(command.task_id)
            if not task:
                msg = f"タスクが見つかりません: {command.task_id}"
                raise RuntimeError(msg)

            # ステータス更新用のUpdateTaskCommandを作成
            from logic.commands.task_commands import UpdateTaskCommand

            update_command = UpdateTaskCommand(
                task_id=command.task_id,
                title=task.title,
                description=task.description,
                status=command.new_status,
                due_date=task.due_date,
            )

            updated_task = task_service.update_task(command.task_id, update_command.to_task_update())
            uow.commit()

            logger.info(f"タスクステータス更新完了: {updated_task.title} (ID: {updated_task.id})")
            return updated_task

    def get_tasks_by_status(self, query: GetTasksByStatusQuery) -> list[TaskRead]:
        """ステータス別タスク取得

        Args:
            query: ステータス別タスク取得クエリ

        Returns:
            タスクリスト
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_tasks_by_status(query.status)

    def get_today_tasks_count(self) -> int:
        """今日のタスク件数取得

        Returns:
            今日のタスク件数
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_today_tasks_count()

    def get_task_by_id(self, query: GetTaskByIdQuery) -> TaskRead | None:
        """ID指定タスク取得

        Args:
            query: ID指定タスク取得クエリ

        Returns:
            タスク（見つからない場合はNone）
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_task_by_id(query.task_id)

    def get_all_tasks_by_status_dict(self) -> dict[TaskStatus, list[TaskRead]]:
        """全ステータスのタスクを辞書形式で取得

        Returns:
            ステータス別タスク辞書
        """
        from models import TaskStatus

        result = {}

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()

            for status in TaskStatus:
                result[status] = task_service.get_tasks_by_status(status)

            return result
