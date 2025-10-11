"""タスクリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, select

from logic.repositories.base import BaseRepository
from models import Tag, Task, TaskCreate, TaskStatus, TaskUpdate


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
        super().__init__(session, Task, load_options=[Task.tags, Task.project, Task.memo])

    def add_tag_to_task(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task | None:
        """タスクにタグを追加する"""
        task = self.get_by_id(task_id, with_details=True)
        if not task:
            logger.warning("タスクが見つかりません。")
            return None

        tag = self.session.get(Tag, tag_id)
        if not tag:
            logger.warning("タグが見つかりません。")
            return None

        # 既に追加済みでないか確認
        if tag not in task.tags:
            task.tags.append(tag)
            self._commit_and_refresh(task)
            logger.info(f"タスク({task_id})にタグ({tag_id})を追加しました。")

        return task

    def remove_tag_from_task(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task | None:
        """タスクからタグを削除する"""
        task = self.get_by_id(task_id, with_details=True)
        if not task:
            logger.warning("タスクが見つかりません。")
            return None

        tag = self.session.get(Tag, tag_id)
        if not tag:
            logger.warning("タグが見つかりません。")
            return None

        # タグが存在するか確認
        if tag in task.tags:
            task.tags.remove(tag)
            self._commit_and_refresh(task)
            logger.info(f"タスク({task_id})からタグ({tag_id})を削除しました。")

        return task

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def gets_by_status(self, status: TaskStatus, *, with_details: bool = False) -> list[Task]:
        """指定されたステータスのタスク一覧を取得する

        Args:
            status: タスクステータス
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧
        """
        stmt = select(Task).where(Task.status == status)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)
