"""[AI GENERATED] タスクリポジトリの実装"""

import uuid
from datetime import date, datetime

from loguru import logger
from sqlmodel import Session, select

from logic.repositories.base import BaseRepository
from models import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    """[AI GENERATED] タスクリポジトリ

    タスクの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、タスク固有の操作を追加実装。
    """

    def __init__(self) -> None:
        """[AI GENERATED] TaskRepository を初期化する"""
        super().__init__(Task)

    def get_by_project_id(self, project_id: uuid.UUID) -> list[Task]:
        """[AI GENERATED] 指定されたプロジェクトIDのタスク一覧を取得する

        Args:
            project_id: プロジェクトID

        Returns:
            list[Task]: 指定されたプロジェクトのタスク一覧
        """
        try:
            with Session(self.engine) as session:
                statement = select(Task).where(Task.project_id == project_id)
                results = session.exec(statement).all()
                logger.debug(f"プロジェクト {project_id} のタスクを {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"プロジェクトのタスク取得に失敗しました: {e}")
            raise

    def get_by_status(self, status: TaskStatus) -> list[Task]:
        """[AI GENERATED] 指定されたステータスのタスク一覧を取得する

        Args:
            status: タスクステータス

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧
        """
        try:
            with Session(self.engine) as session:
                statement = select(Task).where(Task.status == status)
                results = session.exec(statement).all()
                logger.debug(f"ステータス {status} のタスクを {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"ステータス別タスク取得に失敗しました: {e}")
            raise

    def get_by_due_date(self, due_date: date) -> list[Task]:
        """[AI GENERATED] 指定された期限日のタスク一覧を取得する

        Args:
            due_date: 期限日

        Returns:
            list[Task]: 指定された期限日のタスク一覧
        """
        try:
            with Session(self.engine) as session:
                statement = select(Task).where(Task.due_date == due_date)
                results = session.exec(statement).all()
                logger.debug(f"期限日 {due_date} のタスクを {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"期限日別タスク取得に失敗しました: {e}")
            raise

    def get_subtasks(self, parent_id: uuid.UUID) -> list[Task]:
        """[AI GENERATED] 指定された親タスクのサブタスク一覧を取得する

        Args:
            parent_id: 親タスクのID

        Returns:
            list[Task]: サブタスク一覧
        """
        try:
            with Session(self.engine) as session:
                statement = select(Task).where(Task.parent_id == parent_id)
                results = session.exec(statement).all()
                logger.debug(f"親タスク {parent_id} のサブタスクを {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"サブタスク取得に失敗しました: {e}")
            raise

    def search_by_title(self, title_query: str) -> list[Task]:
        """[AI GENERATED] タイトルでタスクを検索する

        Args:
            title_query: 検索クエリ（部分一致）

        Returns:
            list[Task]: 検索条件に一致するタスク一覧
        """
        try:
            with Session(self.engine) as session:
                # Python側でフィルタリングを実行（SQLiteの制限を回避）
                statement = select(Task)
                all_tasks = session.exec(statement).all()

                # タイトルに検索クエリが含まれるタスクをフィルタリング
                filtered_tasks = [task for task in all_tasks if title_query.lower() in task.title.lower()]

                logger.debug(f"タイトル検索 '{title_query}' で {len(filtered_tasks)} 件取得しました")
                return filtered_tasks
        except Exception as e:
            logger.exception(f"タイトル検索に失敗しました: {e}")
            raise

    def get_inbox_tasks(self) -> list[Task]:
        """[AI GENERATED] INBOXステータスのタスク一覧を取得する

        Returns:
            list[Task]: INBOXステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.INBOX)

    def get_next_action_tasks(self) -> list[Task]:
        """[AI GENERATED] NEXT_ACTIONステータスのタスク一覧を取得する

        Returns:
            list[Task]: NEXT_ACTIONステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.NEXT_ACTION)

    def get_completed_tasks(self) -> list[Task]:
        """[AI GENERATED] COMPLETEDステータスのタスク一覧を取得する

        Returns:
            list[Task]: COMPLETEDステータスのタスク一覧
        """
        return self.get_by_status(TaskStatus.COMPLETED)

    def get_overdue_tasks(self) -> list[Task]:
        """[AI GENERATED] 期限切れのタスク一覧を取得する

        Returns:
            list[Task]: 期限切れのタスク一覧
        """
        try:
            today = datetime.now().date()
            with Session(self.engine) as session:
                # Python側でフィルタリングを実行
                statement = select(Task).where(Task.status != TaskStatus.COMPLETED)
                all_tasks = session.exec(statement).all()

                # 期限切れのタスクをフィルタリング
                overdue_tasks = [task for task in all_tasks if task.due_date is not None and task.due_date < today]

                logger.debug(f"期限切れのタスクを {len(overdue_tasks)} 件取得しました")
                return overdue_tasks
        except Exception as e:
            logger.exception(f"期限切れタスクの取得に失敗しました: {e}")
            raise
