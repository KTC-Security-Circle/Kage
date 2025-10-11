"""プロジェクトリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, select

from logic.repositories.base import BaseRepository
from models import Project, ProjectCreate, ProjectStatus, ProjectUpdate, Task


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """プロジェクトリポジトリ

    プロジェクトの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、プロジェクト固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """ProjectRepository を初期化する

        Args:
            session: データベースセッション
        """
        super().__init__(session, Project, load_options=[Project.tasks])

    def add_task_to_project(self, project_id: uuid.UUID, task_id: str) -> Project | None:
        """プロジェクトにタスクを追加する"""
        project = self.get_by_id(project_id, with_details=True)
        task = self.session.get(Task, task_id)
        if not project or not task:
            logger.warning("プロジェクトまたはタスクが見つかりません。")
            return None

        # 既に追加済みでないか確認
        if task not in project.tasks:
            project.tasks.append(task)
            self._commit_and_refresh(project)
            logger.info(f"プロジェクト({project_id})にタスク({task_id})を追加しました。")

        return project

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def gets_by_status(self, status: ProjectStatus) -> list[Project]:
        """指定されたステータスのプロジェクト一覧を取得する

        Args:
            status: プロジェクトステータス

        Returns:
            list[Project]: 指定された条件に一致するプロジェクト一覧
        """
        stmt = select(Project).where(Project.status == status)
        return self._gets_by_statement(stmt)

    def search_by_title(self, title_query: str) -> list[Project]:
        """タイトルでプロジェクトを検索する

        Args:
            title_query: 検索クエリ（部分一致）

        Returns:
            list[Project]: 検索条件に一致するプロジェクト一覧
        """
        stmt = select(Project).where(func.lower(Project.title).like(f"%{title_query.lower()}%"))
        return self._gets_by_statement(stmt)
