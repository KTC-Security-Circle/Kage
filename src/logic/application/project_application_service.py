"""プロジェクト管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.project_service import ProjectService
from logic.unit_of_work import SqlModelUnitOfWork
from models import ProjectCreate, ProjectRead, ProjectStatus, ProjectUpdate

if TYPE_CHECKING:
    import uuid


class ProjectApplicationError(ApplicationError):
    """プロジェクト管理のApplication Serviceで発生するエラー"""


class ProjectValidationError(ValidationError, ProjectApplicationError):
    """プロジェクトのバリデーションエラー"""


class ProjectApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """プロジェクト管理のApplication Service"""

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> ProjectApplicationService: ...

    def create(self, title: str, description: str | None = None, *, status: ProjectStatus | None = None) -> ProjectRead:
        """プロジェクト作成"""
        if not title.strip():
            msg = "プロジェクトタイトルを入力してください"
            raise ProjectValidationError(msg)

        create_data = ProjectCreate(title=title, description=description, status=status or ProjectStatus.ACTIVE)
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            created = proj_service.create(create_data)
        logger.info(f"プロジェクト作成完了 - (ID={created.id})")
        return created

    def update(self, project_id: uuid.UUID, update_data: ProjectUpdate) -> ProjectRead:
        """プロジェクト更新"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            updated = proj_service.update(project_id, update_data)
        logger.info(f"プロジェクト更新完了 - (ID={updated.id})")
        return updated

    def delete(self, project_id: uuid.UUID) -> bool:
        """プロジェクト削除"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            success = proj_service.delete(project_id)
            logger.info(f"プロジェクト削除完了: ID {project_id}, 結果: {success}")
            return success

    def get_by_id(self, project_id: uuid.UUID) -> ProjectRead:
        """IDでプロジェクト取得"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            return proj_service.get_by_id(project_id)

    def get_all_projects(self) -> list[ProjectRead]:
        """全プロジェクト取得"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            return proj_service.get_all()

    def list_by_status(self, status: ProjectStatus) -> list[ProjectRead]:
        """ステータスでプロジェクト取得"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            return proj_service.list_by_status(status)

    def search(
        self,
        query: str,
        *,
        status: ProjectStatus | None = None,
    ) -> list[ProjectRead]:
        """プロジェクト検索

        Args:
            query: 検索クエリ（空文字・空白のみなら空配列）
            status: 追加のステータスフィルタ

        Returns:
            list[ProjectRead]: 検索結果
        """
        if not query or not query.strip():
            return []

        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            results = proj_service.search_projects(query)
            if status is not None:
                status_items = proj_service.list_by_status(status)
                status_ids = {p.id for p in status_items}
                results = [p for p in results if p.id in status_ids]
            return results
