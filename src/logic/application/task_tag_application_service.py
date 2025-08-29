"""タスクタグ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from logic.commands.task_tag_commands import (
        CreateTaskTagCommand,
        DeleteTaskTagCommand,
        DeleteTaskTagsByTagCommand,
        DeleteTaskTagsByTaskCommand,
    )
    from logic.queries.task_tag_queries import (
        CheckTaskTagExistsQuery,
        GetAllTaskTagsQuery,
        GetTaskTagByTaskAndTagQuery,
        GetTaskTagsByTagIdQuery,
        GetTaskTagsByTaskIdQuery,
    )
    from logic.unit_of_work import UnitOfWork
    from models import TaskTagRead


class TaskTagApplicationService(BaseApplicationService):
    """タスクタグ管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork) -> None:
        """TaskTagApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_task_tag(self, command: CreateTaskTagCommand) -> TaskTagRead:
        """タスクタグ作成

        Args:
            command: タスクタグ作成コマンド

        Returns:
            作成されたタスクタグ

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"タスクタグ作成開始: Task {command.task_id}, Tag {command.tag_id}")

        # バリデーション
        if command.task_id is None:
            msg = "タスクIDが指定されていません"
            raise ValueError(msg)
        if command.tag_id is None:
            msg = "タグIDが指定されていません"
            raise ValueError(msg)

        # Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            created_task_tag = task_tag_service.create_task_tag(command.to_task_tag_create())
            uow.commit()

            logger.info(f"タスクタグ作成完了: Task {created_task_tag.task_id}, Tag {created_task_tag.tag_id}")
            return created_task_tag

    def get_all_task_tags(self, query: GetAllTaskTagsQuery) -> list[TaskTagRead]:
        """全タスクタグ取得

        Args:
            query: 全タスクタグ取得クエリ

        Returns:
            タスクタグ一覧
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("全タスクタグ取得")

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            return task_tag_service.get_all_task_tags()

    def delete_task_tag(self, command: DeleteTaskTagCommand) -> None:
        """タスクからタグを削除

        Args:
            command: タスクタグ削除コマンド

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 削除エラー
        """
        logger.info(f"タスクからタグ削除開始: Task {command.task_id}, Tag {command.tag_id}")

        # バリデーション
        if command.task_id is None:
            msg = "タスクIDが指定されていません"
            raise ValueError(msg)
        if command.tag_id is None:
            msg = "タグIDが指定されていません"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            task_tag_service.delete_task_tag(command.task_id, command.tag_id)
            uow.commit()

            logger.info(f"タスクからタグ削除完了: Task {command.task_id}, Tag {command.tag_id}")

    def get_task_tags_by_task_id(self, query: GetTaskTagsByTaskIdQuery) -> list[TaskTagRead]:
        """タスクID別タスクタグ取得

        Args:
            query: タスクID別タスクタグ取得クエリ

        Returns:
            タスクタグ一覧
        """
        logger.debug(f"タスクID別タスクタグ取得: {query.task_id}")

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            return task_tag_service.get_task_tags_by_task_id(query.task_id)

    def get_task_tags_by_tag_id(self, query: GetTaskTagsByTagIdQuery) -> list[TaskTagRead]:
        """タグID別タスクタグ取得

        Args:
            query: タグID別タスクタグ取得クエリ

        Returns:
            タスクタグ一覧
        """
        logger.debug(f"タグID別タスクタグ取得: {query.tag_id}")

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            return task_tag_service.get_task_tags_by_tag_id(query.tag_id)

    def get_task_tag_by_task_and_tag(self, query: GetTaskTagByTaskAndTagQuery) -> TaskTagRead | None:
        """タスクIDとタグID指定タスクタグ取得

        Args:
            query: タスクIDとタグID指定タスクタグ取得クエリ

        Returns:
            タスクタグ（存在しない場合はNone）
        """
        logger.debug(f"タスクタグ取得: Task {query.task_id}, Tag {query.tag_id}")

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            return task_tag_service.get_task_tag_by_task_and_tag(query.task_id, query.tag_id)

    def check_task_tag_exists(self, query: CheckTaskTagExistsQuery) -> bool:
        """タスクタグ存在確認

        Args:
            query: タスクタグ存在確認クエリ

        Returns:
            タスクタグが存在する場合True
        """
        logger.debug(f"タスクタグ存在確認: Task {query.task_id}, Tag {query.tag_id}")

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            return task_tag_service.check_task_tag_exists(query.task_id, query.tag_id)

    def delete_task_tags_by_task_id(self, command: DeleteTaskTagsByTaskCommand) -> None:
        """タスクの全タスクタグ削除

        Args:
            command: タスクの全タスクタグ削除コマンド

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 削除エラー
        """
        logger.info(f"タスクの全タスクタグ削除開始: Task {command.task_id}")

        # バリデーション
        if command.task_id is None:
            msg = "タスクIDが指定されていません"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            task_tag_service.delete_task_tags_by_task_id(command.task_id)
            uow.commit()

            logger.info(f"タスクの全タスクタグ削除完了: Task {command.task_id}")

    def delete_task_tags_by_tag_id(self, command: DeleteTaskTagsByTagCommand) -> None:
        """タグの全タスクタグ削除

        Args:
            command: タグの全タスクタグ削除コマンド

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 削除エラー
        """
        logger.info(f"タグの全タスクタグ削除開始: Tag {command.tag_id}")

        # バリデーション
        if command.tag_id is None:
            msg = "タグIDが指定されていません"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            task_tag_service = uow.service_factory.create_task_tag_service()
            task_tag_service.delete_task_tags_by_tag_id(command.tag_id)
            uow.commit()

            logger.info(f"タグの全タスクタグ削除完了: Tag {command.tag_id}")
