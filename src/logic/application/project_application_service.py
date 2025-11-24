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
    from collections.abc import Sequence


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

    def create(
        self,
        title: str,
        description: str | None = None,
        *,
        status: ProjectStatus | None = None,
        task_ids: Sequence[uuid.UUID] | None = None,
    ) -> ProjectRead:
        """プロジェクト作成"""
        if not title.strip():
            msg = "プロジェクトタイトルを入力してください"
            raise ProjectValidationError(msg)

        create_data = ProjectCreate(title=title, description=description, status=status or ProjectStatus.ACTIVE)
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            created = proj_service.create(create_data)
            if task_ids is not None and created.id is not None:
                self._sync_project_tasks(uow, proj_service, created.id, task_ids)
        logger.info(f"プロジェクト作成完了 - (ID={created.id})")
        return created

    def update(
        self,
        project_id: uuid.UUID,
        update_data: ProjectUpdate,
        *,
        task_ids: Sequence[uuid.UUID] | None = None,
    ) -> ProjectRead:
        """プロジェクト更新"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            updated = proj_service.update(project_id, update_data)
            if task_ids is not None:
                self._sync_project_tasks(uow, proj_service, project_id, task_ids)
        logger.info(f"プロジェクト更新完了 - (ID={updated.id})")
        return updated

    def delete(self, project_id: uuid.UUID) -> bool:
        """プロジェクト削除"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            success = proj_service.delete(project_id)
            logger.info(f"プロジェクト削除完了: ID {project_id}, 結果: {success}")
            return success

    def get_by_id(self, project_id: uuid.UUID, *, with_details: bool = False) -> ProjectRead:
        """IDでプロジェクト取得"""
        with self._unit_of_work_factory() as uow:
            proj_service = uow.service_factory.get_service(ProjectService)
            return proj_service.get_by_id(project_id, with_details=with_details)

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

    def _sync_project_tasks(
        self,
        uow: SqlModelUnitOfWork,
        proj_service: ProjectService,
        project_id: uuid.UUID,
        task_ids: Sequence[uuid.UUID],
    ) -> None:
        """プロジェクトとタスクの関連付けを同期する。"""
        from logic.repositories import ProjectRepository as _ProjectRepository

        project_repo = uow.repository_factory.create(_ProjectRepository)
        project = project_repo.get_by_id(project_id, with_details=True)
        if not hasattr(project, "tasks"):
            msg = f"プロジェクトID {project_id} のタスク情報が取得できません。"
            raise ProjectApplicationError(msg)

        current_ids = {task.id for task in getattr(project, "tasks", []) if getattr(task, "id", None) is not None}

        desired_ids_ordered: list[uuid.UUID] = []
        desired_ids_set: set[uuid.UUID] = set()
        for task_id in task_ids:
            if task_id is None or task_id in desired_ids_set:
                continue
            desired_ids_set.add(task_id)
            desired_ids_ordered.append(task_id)

        for task_id in desired_ids_ordered:
            if task_id not in current_ids:
                proj_service.add_task(project_id, task_id)

        for task_id in current_ids - desired_ids_set:
            proj_service.remove_task(project_id, task_id)
