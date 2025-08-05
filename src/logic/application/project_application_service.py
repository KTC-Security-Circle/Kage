"""プロジェクト管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from logic.commands.project_commands import (
        CreateProjectCommand,
        DeleteProjectCommand,
        UpdateProjectCommand,
    )
    from logic.queries.project_queries import (
        GetAllProjectsQuery,
        GetProjectByIdQuery,
        SearchProjectsByTitleQuery,
    )
    from logic.unit_of_work import UnitOfWork
    from models import ProjectRead


class ProjectApplicationService(BaseApplicationService):
    """プロジェクト管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork) -> None:
        """ProjectApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_project(self, command: CreateProjectCommand) -> ProjectRead:
        """プロジェクト作成

        Args:
            command: プロジェクト作成コマンド

        Returns:
            作成されたプロジェクト

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"プロジェクト作成開始: {command.title}")

        # バリデーション
        if not command.title.strip():
            msg = "プロジェクトタイトルを入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            created_project = project_service.create_project(command.to_project_create())
            uow.commit()

            logger.info(f"プロジェクト作成完了: {created_project.title} (ID: {created_project.id})")
            return created_project

    def get_project_by_id(self, query: GetProjectByIdQuery) -> ProjectRead:
        """プロジェクトをIDで取得

        Args:
            query: プロジェクト取得クエリ

        Returns:
            取得されたプロジェクト

        Raises:
            ValueError: プロジェクトが見つからない場合
        """
        logger.debug(f"プロジェクト取得: {query.project_id}")

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            project = project_service.get_project_by_id(query.project_id)

            if project is None:
                msg = f"プロジェクトが見つかりません: {query.project_id}"
                raise ValueError(msg)

            return project

    def get_all_projects(self, query: GetAllProjectsQuery) -> list[ProjectRead]:
        """全プロジェクト取得

        Args:
            query: 全プロジェクト取得クエリ

        Returns:
            プロジェクト一覧
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("全プロジェクト取得")

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            return project_service.get_all_projects()

    def search_projects_by_title(self, query: SearchProjectsByTitleQuery) -> list[ProjectRead]:
        """タイトルでプロジェクトを検索

        Args:
            query: プロジェクト検索クエリ

        Returns:
            検索結果のプロジェクト一覧
        """
        logger.debug(f"プロジェクト検索: {query.title_query}")

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            return project_service.search_projects(query.title_query)

    def update_project(self, command: UpdateProjectCommand) -> ProjectRead:
        """プロジェクト更新

        Args:
            command: プロジェクト更新コマンド

        Returns:
            更新されたプロジェクト

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 更新エラー
        """
        logger.info(f"プロジェクト更新開始: {command.project_id}")

        # タイトルが更新される場合のバリデーション
        if command.title is not None and not command.title.strip():
            msg = "プロジェクトタイトルを入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            updated_project = project_service.update_project(command.project_id, command.to_project_update())
            uow.commit()

            logger.info(f"プロジェクト更新完了: {updated_project.title} (ID: {updated_project.id})")
            return updated_project

    def delete_project(self, command: DeleteProjectCommand) -> None:
        """プロジェクト削除

        Args:
            command: プロジェクト削除コマンド

        Raises:
            ValueError: 削除できない場合
            RuntimeError: 削除エラー
        """
        logger.info(f"プロジェクト削除開始: {command.project_id}")

        with self._unit_of_work_factory() as uow:
            project_service = uow.service_factory.create_project_service()
            success = project_service.delete_project(command.project_id)

            if not success:
                msg = f"プロジェクトの削除に失敗しました: {command.project_id}"
                raise ValueError(msg)

            uow.commit()
            logger.info(f"プロジェクト削除完了: {command.project_id}")
