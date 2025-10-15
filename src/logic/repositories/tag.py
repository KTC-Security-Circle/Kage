"""タグリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, select

from errors import NotFoundError
from logic.repositories.base import BaseRepository
from models import Memo, Tag, TagCreate, TagUpdate, Task


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    """タグリポジトリ

    タグの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、タグ固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """TagRepository を初期化する

        Args:
            session: データベースセッション
        """
        self.model_class = Tag
        super().__init__(session, load_options=[Tag.tasks, Tag.memos])

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
            raise NotFoundError(msg)
        return task

    def _check_exists_memo(self, memo_id: uuid.UUID) -> Memo:
        """メモが存在するか確認する

        Args:
            memo_id: 確認するメモのID

        Returns:
            Memo: 存在するメモ

        Raises:
            NotFoundError: メモが存在しない場合
        """
        memo = self.session.get(Memo, memo_id)
        if memo is None:
            msg = f"メモが見つかりません: {memo_id}"
            raise NotFoundError(msg)
        return memo

    def add_task(self, tag_id: uuid.UUID, task_id: uuid.UUID) -> Tag:
        """タグにタスクを追加する

        Args:
            tag_id: タグのID
            task_id: 追加するタスクのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)
        task = self._check_exists_task(task_id)

        if task not in tag.tasks:
            tag.tasks.append(task)
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})にタスク({task_id})を追加しました。")
        else:
            logger.warning(f"タグ({tag_id})にタスク({task_id})は既に追加されています。")

        return tag

    def remove_task(self, tag_id: uuid.UUID, task_id: uuid.UUID) -> Tag:
        """タグからタスクを削除する

        Args:
            tag_id: タグのID
            task_id: 削除するタスクのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)
        task = self._check_exists_task(task_id)

        if task in tag.tasks:
            tag.tasks.remove(task)
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})からタスク({task_id})を削除しました。")
        else:
            logger.warning(f"タグ({tag_id})にタスク({task_id})は存在しません。")

        return tag

    def remove_all_tasks(self, tag_id: uuid.UUID) -> Tag:
        """タグから全てのタスクを削除する

        Args:
            tag_id: タグのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)

        if tag.tasks:
            num_tasks = len(tag.tasks)
            tag.tasks.clear()
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})から {num_tasks} 件のタスクを削除しました。")
        else:
            logger.warning(f"タグ({tag_id})にはタスクが存在しません。")

        return tag

    def add_memo(self, tag_id: uuid.UUID, memo_id: uuid.UUID) -> Tag:
        """タグにメモを追加する

        Args:
            tag_id: タグのID
            memo_id: 追加するメモのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)
        memo = self._check_exists_memo(memo_id)

        if memo not in tag.memos:
            tag.memos.append(memo)
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})にメモ({memo_id})を追加しました。")
        else:
            logger.warning(f"タグ({tag_id})にメモ({memo_id})は既に追加されています。")

        return tag

    def remove_memo(self, tag_id: uuid.UUID, memo_id: uuid.UUID) -> Tag:
        """タグからメモを削除する

        Args:
            tag_id: タグのID
            memo_id: 削除するメモのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)
        memo = self._check_exists_memo(memo_id)

        if memo in tag.memos:
            tag.memos.remove(memo)
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})からメモ({memo_id})を削除しました。")
        else:
            logger.warning(f"タグ({tag_id})にメモ({memo_id})は存在しません。")

        return tag

    def remove_all_memos(self, tag_id: uuid.UUID) -> Tag:
        """タグから全てのメモを削除する

        Args:
            tag_id: タグのID

        Returns:
            Tag: 更新されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        tag = self.get_by_id(tag_id, with_details=True)

        if tag.memos:
            num_memos = len(tag.memos)
            tag.memos.clear()
            self._commit_and_refresh(tag)
            logger.debug(f"タグ({tag_id})から {num_memos} 件のメモを削除しました。")
        else:
            logger.warning(f"タグ({tag_id})にはメモが存在しません。")

        return tag

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def get_by_name(self, name: str, *, with_details: bool = False) -> Tag:
        """指定されたタグ名でタグを取得する

        Args:
            name: タグ名
            with_details: 関連エンティティを含めるかどうか

        Returns:
            Tag | None: 取得されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Tag).where(Tag.name == name)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._get_by_statement(stmt, name)

    def search_by_name(self, name_query: str, *, with_details: bool = False) -> list[Tag]:
        """タグ名でタグを検索する

        Args:
            name_query: タグ名
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Tag]: 検索条件に一致するタグ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Tag).where(func.lower(Tag.name).like(f"%{name_query.lower()}%"))

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)
