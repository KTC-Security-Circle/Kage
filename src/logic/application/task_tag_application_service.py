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
    )
    from logic.queries.task_tag_queries import (
        GetAllTaskTagsQuery,
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

        with self._unit_of_work_factory() as uow:
            # 基本的な実装 - 将来の拡張に備えてプレースホルダーとする
            from models import TaskTag

            task_tag = TaskTag(task_id=command.task_id, tag_id=command.tag_id)
            uow.session.add(task_tag)
            uow.commit()
            uow.session.refresh(task_tag)

            logger.info(f"タスクタグ作成完了: Task {task_tag.task_id}, Tag {task_tag.tag_id}")
            return task_tag  # type: ignore[return-value]

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
            from sqlmodel import select

            from models import TaskTag

            statement = select(TaskTag)
            return list(uow.session.exec(statement).all())  # type: ignore[return-value]

    def delete_task_tag(self, command: DeleteTaskTagCommand) -> None:
        """タスクからタグを削除

        Args:
            command: タスクタグ削除コマンド

        Raises:
            ValueError: 削除できない場合
            RuntimeError: 削除エラー
        """
        logger.info(f"タスクからタグ削除開始: Task {command.task_id}, Tag {command.tag_id}")

        with self._unit_of_work_factory() as uow:
            from sqlmodel import select

            from models import TaskTag

            statement = select(TaskTag).where(
                TaskTag.task_id == command.task_id,
                TaskTag.tag_id == command.tag_id,
            )
            task_tag = uow.session.exec(statement).first()

            if task_tag is None:
                msg = f"タスクからタグの削除に失敗しました: Task {command.task_id}, Tag {command.tag_id}"
                raise ValueError(msg)

            uow.session.delete(task_tag)
            uow.commit()
            logger.info(f"タスクからタグ削除完了: Task {command.task_id}, Tag {command.tag_id}")
