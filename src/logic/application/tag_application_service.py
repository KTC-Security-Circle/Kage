"""タグ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.services.tag_service import TagService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from logic.commands.tag_commands import CreateTagCommand, DeleteTagCommand, UpdateTagCommand
    from logic.queries.tag_queries import GetAllTagsQuery, GetTagByIdQuery, SearchTagsByNameQuery
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
        """タグ作成

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
            tag_service = uow.service_factory.get_service(TagService)
            created_tag = tag_service.create_tag(command.to_tag_create())
            uow.commit()

            logger.info(f"タグ作成完了: {created_tag.name} (ID: {created_tag.id})")
            return created_tag

    def get_tag_by_id(self, query: GetTagByIdQuery) -> TagRead:
        """IDでタグを取得

        Args:
            query: タグ取得クエリ

        Returns:
            取得されたタグ

        Raises:
            ValueError: タグが見つからない場合
        """
        logger.debug(f"タグ取得: {query.tag_id}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            tag = tag_service.get_tag_by_id(query.tag_id)

            if tag is None:
                msg = f"タグが見つかりません: {query.tag_id}"
                raise ValueError(msg)

            return tag

    def get_all_tags(self, query: GetAllTagsQuery) -> list[TagRead]:
        """全タグ取得

        Args:
            query: 全タグ取得クエリ

        Returns:
            タグ一覧
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("全タグ取得")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.get_all_tags()

    def search_tags_by_name(self, query: SearchTagsByNameQuery) -> list[TagRead]:
        """名前でタグを検索

        Args:
            query: タグ検索クエリ

        Returns:
            検索結果のタグ一覧
        """
        logger.debug(f"タグ名検索: {query.name_query}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.search_tags(query.name_query)

    def update_tag(self, command: UpdateTagCommand) -> TagRead:
        """タグ更新

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
            tag_service = uow.service_factory.get_service(TagService)
            updated_tag = tag_service.update_tag(command.tag_id, command.to_tag_update())
            uow.commit()

            logger.info(f"タグ更新完了: {updated_tag.name} (ID: {updated_tag.id})")
            return updated_tag

    def delete_tag(self, command: DeleteTagCommand) -> None:
        """タグ削除

        Args:
            command: タグ削除コマンド

        Raises:
            ValueError: 削除できない場合
            RuntimeError: 削除エラー
        """
        logger.info(f"タグ削除開始: {command.tag_id}")

        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            success = tag_service.delete_tag(command.tag_id)

            if not success:
                msg = f"タグの削除に失敗しました: {command.tag_id}"
                raise ValueError(msg)

            uow.commit()
            logger.info(f"タグ削除完了: {command.tag_id}")
