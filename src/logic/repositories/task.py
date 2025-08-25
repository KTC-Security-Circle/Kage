"""タスクリポジトリの実装"""

import uuid
from datetime import date, datetime

from loguru import logger
from sqlmodel import Session, select, func

from logic.repositories.base import BaseRepository
from models import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    """タスクリポジトリ

    タスクの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、タスク固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """TaskRepository を初期化する

        Args:
            session: データベースセッション
        """
        super().__init__(Task, session)

    def get_by_project_id(self, project_id: uuid.UUID) -> list[Task]:
        """指定されたプロジェクトIDのタスク一覧を取得する

        Args:
            project_id: プロジェクトID

        Returns:
            list[Task]: 指定されたプロジェクトのタスク一覧
        """
        try:
            statement = select(Task).where(Task.project_id == project_id)
            results = self.session.exec(statement).all()
            return list(results)
        except Exception as e:
            logger.exception(f"プロジェクトのタスク取得に失敗しました: {e}")
            raise

    def get_by_status(self, status: TaskStatus) -> list[Task]:
        """指定されたステータスのタスク一覧を取得する

        Args:
            status: タスクステータス

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧
        """
        try:
            statement = select(Task).where(Task.status == status)
            results = self.session.exec(statement).all()
            return list(results)
        except Exception as e:
            logger.exception(f"ステータス別タスク取得に失敗しました: {e}")
            raise

    def get_by_due_date(self, due_date: date) -> list[Task]:
        """指定された期限日のタスク一覧を取得する

        Args:
            due_date: 期限日

        Returns:
            list[Task]: 指定された期限日のタスク一覧
        """
        try:
            statement = select(Task).where(Task.due_date == due_date)
            results = self.session.exec(statement).all()
            return list(results)
        except Exception as e:
            logger.exception(f"期限日別タスク取得に失敗しました: {e}")
            raise

    def get_subtasks(self, parent_id: uuid.UUID) -> list[Task]:
        """指定された親タスクのサブタスク一覧を取得する

        Args:
            parent_id: 親タスクのID

        Returns:
            list[Task]: サブタスク一覧
        """
        try:
            statement = select(Task).where(Task.parent_id == parent_id)
            results = self.session.exec(statement).all()
            return list(results)
        except Exception as e:
            logger.exception(f"サブタスク取得に失敗しました: {e}")
            raise

    def search_by_title(self, title_query: str) -> list[Task]:
        """タイトルでタスクを検索する

        Args:
            title_query: 検索クエリ（部分一致）

        Returns:
            list[Task]: 検索条件に一致するタスク一覧
        """
        try:
            # SQLModelでフィルタリングを実行（大きめの検索が来た際にPython側だと遅くなるため）
            # [AI GENERATED] 大文字小文字を区別しない検索のためfunc.lower()を使用
            statement = select(Task).where(func.lower(Task.title).contains(func.lower(title_query)))  # pyright: ignore[reportAttributeAccessIssue]
            filtered_tasks = list(self.session.exec(statement).all())

        except Exception as e:
            logger.exception(f"タイトル検索に失敗しました: {e}")
            raise
        else:
            return filtered_tasks

    def get_inbox_tasks(self) -> list[Task]:
        """INBOXステータスのタスク一覧を取得する

        Returns:
            list[Task]: INBOXステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.INBOX)

    def get_next_action_tasks(self) -> list[Task]:
        """NEXT_ACTIONステータスのタスク一覧を取得する

        Returns:
            list[Task]: NEXT_ACTIONステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.NEXT_ACTION)

    def get_completed_tasks(self) -> list[Task]:
        """COMPLETEDステータスのタスク一覧を取得する

        Returns:
            list[Task]: COMPLETEDステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.COMPLETED)

    def get_overdue_tasks(self) -> list[Task]:
        """期限切れのタスク一覧を取得する

        Returns:
            list[Task]: 期限切れのタスク一覧
        """
        try:
            today = datetime.now().date()
            # Python側でフィルタリングを実行
            statement = select(Task).where(Task.status != TaskStatus.COMPLETED)
            all_tasks = self.session.exec(statement).all()

            # 期限切れのタスクをフィルタリング
            overdue_tasks = [task for task in all_tasks if task.due_date is not None and task.due_date < today]

        except Exception as e:
            logger.exception(f"期限切れタスクの取得に失敗しました: {e}")
            raise
        else:
            return overdue_tasks
