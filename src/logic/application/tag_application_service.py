"""タグ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    import uuid

    from logic.commands.tag_commands import CreateTagCommand, DeleteTagCommand, UpdateTagCommand
    from logic.unit_of_work import UnitOfWork
    from models import TagRead


class TagApplicationService(BaseApplicationService):
    """タグ管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork) -> None:
        """TagApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_tag(self, command: CreateTagCommand) -> TagRead:
        """[AI GENERATED] タグ作成

        Args:
            command: タグ作成コマンド

        Returns:
            作成されたタグ

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"タグ作成開始: {command.name}")

        # バリデーション
        if not command.name.strip():
            msg = "タグ名を入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            created_tag = tag_service.create_tag(command.to_tag_create())
            uow.commit()

            logger.info(f"タグ作成完了: {created_tag.name} (ID: {created_tag.id})")
            return created_tag

    def get_tag_by_id(self, tag_id: uuid.UUID) -> TagRead:
        """[AI GENERATED] IDでタグを取得

        Args:
            tag_id: タグID

        Returns:
            取得されたタグ

        Raises:
            ValueError: タグが見つからない場合
        """
        logger.debug(f"タグ取得: {tag_id}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            tag = tag_service.get_tag_by_id(tag_id)

            if tag is None:
                msg = f"タグが見つかりません: {tag_id}"
                raise ValueError(msg)

            return tag

    def get_all_tags(self) -> list[TagRead]:
        """[AI GENERATED] 全タグ取得

        Returns:
            タグ一覧
        """
        logger.debug("全タグ取得")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            return tag_service.get_all_tags()

    def get_tag_by_name(self, name: str) -> TagRead | None:
        """[AI GENERATED] 名前でタグを取得

        Args:
            name: タグ名

        Returns:
            取得されたタグ、見つからない場合はNone
        """
        logger.debug(f"タグ名検索: {name}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            return tag_service.get_tag_by_name(name)

    def update_tag(self, command: UpdateTagCommand) -> TagRead:
        """[AI GENERATED] タグ更新

        Args:
            command: タグ更新コマンド

        Returns:
            更新されたタグ

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 更新エラー
        """
        logger.info(f"タグ更新開始: {command.tag_id}")

        # 名前が更新される場合のバリデーション
        if command.name is not None and not command.name.strip():
            msg = "タグ名を入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            updated_tag = tag_service.update_tag(command.tag_id, command.to_tag_update())
            uow.commit()

            logger.info(f"タグ更新完了: {updated_tag.name} (ID: {updated_tag.id})")
            return updated_tag

    def delete_tag(self, command: DeleteTagCommand) -> bool:
        """[AI GENERATED] タグ削除

        Args:
            command: タグ削除コマンド

        Returns:
            削除成功時True

        Raises:
            ValueError: 削除できない場合
            RuntimeError: 削除エラー
        """
        logger.info(f"タグ削除開始: {command.tag_id}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            success = tag_service.delete_tag(command.tag_id)

            if success:
                uow.commit()
                logger.info(f"タグ削除完了: {command.tag_id}")

            return success

    def search_tags_by_name(self, name_query: str) -> list[TagRead]:
        """[AI GENERATED] 名前でタグを検索

        Args:
            name_query: 検索クエリ（部分一致）

        Returns:
            検索条件に一致するタグ一覧
        """
        logger.debug(f"タグ検索: {name_query}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.create_tag_service()
            return tag_service.search_tags(name_query)
