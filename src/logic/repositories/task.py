"""タスクリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, select

from errors import NotFoundError
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
        self.model_class = Task
        super().__init__(session, load_options=[Task.tags, Task.project, Task.memo])

    def _check_exists_tag(self, tag_id: uuid.UUID) -> Tag:
        """タグが存在するか確認する

        Args:
            tag_id: 確認するタグのID

        Returns:
            Tag: 存在するタグ

        Raises:
            NotFoundError: タグが存在しない場合
        """
        tag = self.session.get(Tag, tag_id)
        if tag is None:
            msg = f"タグが見つかりません: {tag_id}"
            logger.warning(msg)
            raise NotFoundError(msg)
        return tag

    def add_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task:
        """タスクにタグを追加する

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            Task: 更新されたタスク

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        task = self.get_by_id(task_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        # 既に追加済みでないか確認
        if tag not in task.tags:
            task.tags.append(tag)
            self._commit_and_refresh(task)
            logger.info(f"タスク({task_id})にタグ({tag_id})を追加しました。")
        else:
            logger.info(f"タスク({task_id})にタグ({tag_id})は既に追加されています。")

        return task

    def remove_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task:
        """タスクからタグを削除する

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            Task: 更新されたタスク

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        task = self.get_by_id(task_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        # タグが存在するか確認
        if tag in task.tags:
            task.tags.remove(tag)
            self._commit_and_refresh(task)
            logger.info(f"タスク({task_id})からタグ({tag_id})を削除しました。")
        else:
            logger.info(f"タスク({task_id})にはタグ({tag_id})は存在しません。")

        return task

    def remove_all_tags(self, task_id: uuid.UUID) -> Task:
        """タスクから全てのタグを削除する

        Args:
            task_id: タスクID

        Returns:
            Task: 更新されたタスク

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        task = self.get_by_id(task_id, with_details=True)

        if task.tags:
            num_tags = len(task.tags)
            task.tags.clear()
            self._commit_and_refresh(task)
            logger.info(f"タスク({task_id})から {num_tags} 件のタグを削除しました。")
        else:
            logger.info(f"タスク({task_id})にはタグは存在しません。")

        return task

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def list_by_status(self, status: TaskStatus, *, with_details: bool = False) -> list[Task]:
        """指定されたステータスのタスク一覧を取得する

        Args:
            status: タスクステータス
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Task).where(Task.status == status)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)

    def list_by_project(self, project_id: uuid.UUID, *, with_details: bool = False) -> list[Task]:
        """指定されたプロジェクトに関連するタスク一覧を取得する

        Args:
            project_id: プロジェクトID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Task).where(Task.project_id == project_id)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)

    def search_by_title(self, title_query: str, *, with_details: bool = False) -> list[Task]:
        """タイトルでタスクを検索する

        Args:
            title_query: タイトルの検索クエリ
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Task]: 指定された条件に一致するタスク一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Task).where(func.lower(Task.title).like(f"%{title_query.lower()}%"))

        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)
