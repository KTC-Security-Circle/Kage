"""タグ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.tag_service import TagService
from logic.unit_of_work import SqlModelUnitOfWork
from models import TagCreate, TagRead, TagUpdate

if TYPE_CHECKING:
    import uuid


class TagApplicationError(ApplicationError):
    """タグ管理のApplication Serviceで発生するエラー"""


class TagValidationError(ValidationError, TagApplicationError):
    """タグのバリデーションエラー"""


class TagApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """タグ管理のApplication Service"""

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> TagApplicationService: ...

    def create(self, name: str, description: str | None = None, color: str | None = None) -> TagRead:
        """タグ作成"""
        if not name.strip():
            msg = "タグ名を入力してください"
            raise TagValidationError(msg)

        create_data = TagCreate(name=name, description=description, color=color)
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            created = tag_service.create(create_data)
        logger.info(f"タグ作成完了 - (ID={created.id})")
        return created

    def update(self, tag_id: uuid.UUID, update_data: TagUpdate) -> TagRead:
        """タグ更新"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            updated = tag_service.update(tag_id, update_data)
        logger.info(f"タグ更新完了 - (ID={updated.id})")
        return updated

    def delete(self, tag_id: uuid.UUID) -> bool:
        """タグ削除"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            success = tag_service.delete(tag_id)
            logger.info(f"タグ削除完了: ID {tag_id}, 結果: {success}")
            return success

    def get_by_id(self, tag_id: uuid.UUID) -> TagRead:
        """IDでタグ取得"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.get_by_id(tag_id)

    def get_by_name(self, name: str) -> TagRead:
        """名前でタグ取得"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.get_by_name(name)

    def get_all_tags(self) -> list[TagRead]:
        """全タグ取得"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.get_all()

    def search_by_name(self, query: str) -> list[TagRead]:
        """名前で部分一致検索"""
        with self._unit_of_work_factory() as uow:
            tag_service = uow.service_factory.get_service(TagService)
            return tag_service.search_by_name(query)

    def search(self, query: str) -> list[TagRead]:
        """タグ検索（エイリアス）

        Args:
            query: 検索クエリ

        Returns:
            list[TagRead]: 検索結果
        """
        return self.search_by_name(query)
