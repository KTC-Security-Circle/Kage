"""メモ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.memo_service import MemoService
from logic.unit_of_work import SqlModelUnitOfWork
from models import MemoCreate, MemoRead, MemoUpdate

if TYPE_CHECKING:
    import uuid

logger_msg = "{msg} - (ID={memo_id})"


class MemoApplicationError(ApplicationError):
    """メモ管理のApplication Serviceで発生するエラー"""


class ContentValidationError(ValidationError, MemoApplicationError):
    """メモ内容のバリデーションエラー"""


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

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> MemoApplicationService: ...

    def create(self, title: str, content: str) -> MemoRead:
        """メモを作成する

        Args:
            title: メモタイトル
            content: メモ内容

        Returns:
            MemoRead: 作成されたメモ

        Raises:
            ContentValidationError: タイトルまたは内容が空の場合
        """
        if not title.strip():
            msg = "メモタイトルを入力してください"
            raise ContentValidationError(msg)

        if not content.strip():
            msg = "メモ内容を入力してください"
            raise ContentValidationError(msg)

        memo = MemoCreate(title=title, content=content)

        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            created_memo = memo_service.create(memo)

        logger.info(logger_msg.format(msg="メモ作成完了", memo_id=created_memo.id))
        return created_memo

    def update(self, memo_id: uuid.UUID, update_data: MemoUpdate) -> MemoRead:
        """メモを更新する

        Args:
            memo_id: 更新するメモのID
            update_data: メモ更新データ

        Returns:
            MemoRead: 更新されたメモ
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            updated_memo = memo_service.update(memo_id, update_data)

        logger.info(logger_msg.format(msg="メモ更新完了", memo_id=updated_memo.id))
        return updated_memo

    def delete(self, memo_id: uuid.UUID) -> bool:
        """メモ削除

        Args:
            memo_id: 削除するメモのID

        Returns:
            bool: 削除成功フラグ

        Raises:
            RuntimeError: 削除エラー
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            success = memo_service.delete(memo_id)

            logger.info(f"メモ削除完了: ID {memo_id}, 結果: {success}")
            return success

    def get_by_id(self, memo_id: uuid.UUID, *, with_details: bool = False) -> MemoRead:
        """IDでメモ取得

        Args:
            memo_id: メモのID
            with_details: 関連エンティティも取得するかどうか

        Returns:
            MemoRead: 指定されたIDのメモ
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            return memo_service.get_by_id(memo_id, with_details=with_details)

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        """全メモ取得

        Args:
            with_details: 関連エンティティも取得するかどうか

        Returns:
            list[MemoRead]: 全メモのリスト
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.get_all(with_details=with_details)
