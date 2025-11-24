"""プロジェクトリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, select

from errors import NotFoundError
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
        self.model_class = Project
        super().__init__(session, load_options=[Project.tasks])

    def _check_exists_task(self, task_id: uuid.UUID) -> Task:
        """タスクが存在するか確認する

        Args:
            task_id: 確認するタスクのID

        Returns:
            Task: 存在するタスク

        Raises:
            NotFoundError: タスクが存在しない場合
        """
        task = self.session.get(Task, task_id)
        if task is None:
            msg = f"タスクが見つかりません: {task_id}"
            logger.warning(msg)
            raise NotFoundError(msg)
        return task

    def add_task(self, project_id: uuid.UUID, task_id: uuid.UUID) -> Project:
        """プロジェクトにタスクを追加する

        Args:
            project_id: プロジェクトのID
            task_id: 追加するタスクのID

        Returns:
            Project: 更新されたプロジェクト

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        project = self.get_by_id(project_id, with_details=True)
        task = self._check_exists_task(task_id)

        # 既に追加済みでないか確認
        if task not in project.tasks:
            project.tasks.append(task)
            self._commit_and_refresh(project)
            logger.debug(f"プロジェクト({project_id})にタスク({task_id})を追加しました。")
        else:
            logger.warning(f"プロジェクト({project_id})にタスク({task_id})は既に追加されています。")

        return project

    def remove_task(self, project_id: uuid.UUID, task_id: uuid.UUID) -> Project:
        """プロジェクトからタスクを削除する

        Args:
            project_id: プロジェクトのID
            task_id: 削除するタスクのID

        Returns:
            Project: 更新されたプロジェクト

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        project = self.get_by_id(project_id, with_details=True)
        task = self._check_exists_task(task_id)

        if task in project.tasks:
            project.tasks.remove(task)
            self._commit_and_refresh(project)
            logger.debug(f"プロジェクト({project_id})からタスク({task_id})を削除しました。")
        else:
            logger.warning(f"プロジェクト({project_id})にタスク({task_id})は存在しません。")

        return project

    def remove_all_tasks(self, project_id: uuid.UUID) -> Project:
        """プロジェクトから全てのタスクを削除する

        もしタスクが存在しない場合は何もしない

        Args:
            project_id: プロジェクトのID

        Returns:
            Project: 更新されたプロジェクト

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        project = self.get_by_id(project_id, with_details=True)

        if project.tasks:
            num_tasks = len(project.tasks)
            project.tasks.clear()
            self._commit_and_refresh(project)
            logger.debug(f"プロジェクト({project_id})から {num_tasks} 個のタスクを削除しました。")
        else:
            logger.debug(f"プロジェクト({project_id})にはタスクが存在しません。")

        return project

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def list_by_status(self, status: ProjectStatus) -> list[Project]:
        """指定されたステータスのプロジェクト一覧を取得する

        Args:
            status: プロジェクトステータス

        Returns:
            list[Project]: 指定された条件に一致するプロジェクト一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Project).where(Project.status == status)
        return self._gets_by_statement(stmt)

    def search_by_title(self, title_query: str) -> list[Project]:
        """タイトルでプロジェクトを検索する

        Args:
            title_query: 検索クエリ（部分一致）

        Returns:
            list[Project]: 検索条件に一致するプロジェクト一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Project).where(func.lower(Project.title).like(f"%{title_query.lower()}%"))
        return self._gets_by_statement(stmt)
