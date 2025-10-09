"""メモ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.services.memo_service import MemoService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from logic.commands.memo_commands import CreateMemoCommand, DeleteMemoCommand, UpdateMemoCommand
    from logic.queries.memo_queries import (
        GetAllMemosQuery,
        GetMemoByIdQuery,
        GetMemosByTaskIdQuery,
        SearchMemosQuery,
    )
    from models import MemoRead


class MemoApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """メモ管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        """MemoApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_memo(self, command: CreateMemoCommand) -> MemoRead:
        """メモ作成

        Args:
            command: メモ作成コマンド

        Returns:
            MemoRead: 作成されたメモ

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"メモ作成開始: タスクID {command.task_id}")

        # [AI GENERATED] バリデーション
        if not command.content.strip():
            msg = "メモ内容を入力してください"
            raise ValueError(msg)

        # [AI GENERATED] Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            created_memo = memo_service.create_memo(command.to_memo_create())
            uow.commit()

            logger.info(f"メモ作成完了: ID {created_memo.id}, タスクID {created_memo.task_id}")
            return created_memo

    def update_memo(self, command: UpdateMemoCommand) -> MemoRead:
        """メモ更新

        Args:
            command: メモ更新コマンド

        Returns:
            MemoRead: 更新されたメモ

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 更新エラー
        """
        logger.info(f"メモ更新開始: ID {command.memo_id}")

        # [AI GENERATED] バリデーション
        if not command.content.strip():
            msg = "メモ内容を入力してください"
            raise ValueError(msg)

        # [AI GENERATED] Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            updated_memo = memo_service.update_memo(command.memo_id, command.to_memo_update())
            uow.commit()

            logger.info(f"メモ更新完了: ID {updated_memo.id}")
            return updated_memo

    def delete_memo(self, command: DeleteMemoCommand) -> bool:
        """メモ削除

        Args:
            command: メモ削除コマンド

        Returns:
            bool: 削除成功フラグ

        Raises:
            RuntimeError: 削除エラー
        """
        logger.info(f"メモ削除開始: ID {command.memo_id}")

        # [AI GENERATED] Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            success = memo_service.delete_memo(command.memo_id)
            uow.commit()

            logger.info(f"メモ削除完了: ID {command.memo_id}, 結果: {success}")
            return success

    def get_memo_by_id(self, query: GetMemoByIdQuery) -> MemoRead | None:
        """IDでメモ取得

        Args:
            query: メモ取得クエリ

        Returns:
            MemoRead | None: 取得されたメモ、存在しない場合はNone
        """
        logger.debug(f"メモ取得: ID {query.memo_id}")

        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.get_memo_by_id(query.memo_id)

    def get_all_memos(self, query: GetAllMemosQuery) -> list[MemoRead]:  # noqa: ARG002
        """全メモ取得

        Args:
            query: 全メモ取得クエリ

        Returns:
            list[MemoRead]: 全メモのリスト
        """
        logger.debug("全メモ取得")

        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.get_all_memos()

    def get_memos_by_task_id(self, query: GetMemosByTaskIdQuery) -> list[MemoRead]:
        """タスクIDでメモ取得

        Args:
            query: タスクID指定メモ取得クエリ

        Returns:
            list[MemoRead]: 指定されたタスクのメモリスト
        """
        logger.debug(f"タスクメモ取得: タスクID {query.task_id}")

        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.get_memos_by_task_id(query.task_id)

    def search_memos(self, query: SearchMemosQuery) -> list[MemoRead]:
        """メモ検索

        Args:
            query: メモ検索クエリ

        Returns:
            list[MemoRead]: 検索条件に一致するメモのリスト
        """
        logger.debug(f"メモ検索: クエリ '{query.query}'")

        # [AI GENERATED] 空の検索クエリは全件返却しない
        if not query.query.strip():
            return []

        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.search_memos(query.query)
