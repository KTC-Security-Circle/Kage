"""メモリポジトリの実装"""

import uuid
from collections.abc import Iterable
from datetime import datetime
from typing import Any, cast

from loguru import logger
from sqlmodel import Session, func, select

from errors import NotFoundError
from logic.repositories.base import BaseRepository
from models import Memo, MemoCreate, MemoStatus, MemoTagLink, MemoUpdate, Tag, Task


class MemoRepository(BaseRepository[Memo, MemoCreate, MemoUpdate]):
    """メモリポジトリ

    メモのCRUD操作を提供するリポジトリクラス。
    BaseRepositoryを継承して基本操作を提供し、メモ固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """MemoRepositoryを初期化する

        Args:
            session: データベースセッション
        """
        self.model_class = Memo
        super().__init__(session, load_options=[Memo.tags, Memo.tasks])

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

    def add_tag(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo:
        """メモにタグを追加する

        Args:
            memo_id: メモID
            tag_id: タグID

        Returns:
            Memo: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタグが存在しない場合
        """
        memo = self.get_by_id(memo_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        # 既に追加済みでないか確認
        if tag not in memo.tags:
            memo.tags.append(tag)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})にタグ({tag_id})を追加しました。")
        else:
            logger.warning(f"メモ({memo_id})には既にタグ({tag_id})が追加されています。")

        return memo

    def remove_tag(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo:
        """メモからタグを削除する

        Args:
            memo_id: メモID
            tag_id: タグID

        Returns:
            Memo: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタグが存在しない場合
        """
        memo = self.get_by_id(memo_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        # タグがメモに存在するか確認
        if tag in memo.tags:
            memo.tags.remove(tag)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})からタグ({tag_id})を削除しました。")
        else:
            logger.warning(f"メモ({memo_id})にはタグ({tag_id})が存在しません。")

        return memo

    def add_task(self, memo_id: uuid.UUID, task_id: uuid.UUID) -> Memo:
        """メモにタスクを追加する

        Args:
            memo_id: メモID
            task_id: タスクID

        Returns:
            Memo: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタスクが存在しない場合
        """
        memo = self.get_by_id(memo_id, with_details=True)
        task = self._check_exists_task(task_id)

        # 既に追加済みでないか確認
        if task not in memo.tasks:
            memo.tasks.append(task)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})にタスク({task_id})を追加しました。")
        else:
            logger.warning(f"メモ({memo_id})には既にタスク({task_id})が追加されています。")

        return memo

    def remove_task(self, memo_id: uuid.UUID, task_id: uuid.UUID) -> Memo:
        """メモからタスクを削除する

        Args:
            memo_id: メモID
            task_id: タスクID

        Returns:
            Memo: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタスクが存在しない場合
        """
        memo = self.get_by_id(memo_id, with_details=True)
        task = self._check_exists_task(task_id)

        # 既に追加済みでないか確認
        if task in memo.tasks:
            memo.tasks.remove(task)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})からタスク({task_id})を削除しました。")
        else:
            logger.warning(f"メモ({memo_id})にはタスク({task_id})が存在しません。")

        return memo

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def list_by_status(self, status: MemoStatus, *, with_details: bool = False) -> list[Memo]:
        """指定されたステータスのメモ一覧を取得する

        Args:
            status: メモステータス
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 指定された条件に一致するメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Memo).where(Memo.status == status)
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)

    def list_by_tag(self, tag_id: uuid.UUID, *, with_details: bool = False) -> list[Memo]:
        """指定されたタグが付与されたメモ一覧を取得する

        Args:
            tag_id: タグID
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 指定された条件に一致するメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        # 特定のタグが付与されたメモを取得
        stmt = select(Memo).join(MemoTagLink).join(Tag).where(Tag.id == tag_id)
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)

    def search_by_title(self, title_query: str, *, with_details: bool = False) -> list[Memo]:
        """メモタイトルでメモを検索する

        Args:
            title_query: 検索クエリ（部分一致）
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 検索条件に一致するメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Memo).where(func.lower(Memo.title).like(f"%{title_query.lower()}%"))
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)

    def search_by_content(self, content_query: str, *, with_details: bool = False) -> list[Memo]:
        """メモ内容でメモを検索する

        Args:
            content_query: 検索クエリ（部分一致）
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 検索条件に一致するメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Memo).where(func.lower(Memo.content).contains(func.lower(content_query)))
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)

    def list_unprocessed_memos(
        self,
        created_after: datetime | None,
        *,
        statuses: Iterable[MemoStatus] | None = None,
        limit: int | None = 20,
        with_details: bool = True,
    ) -> list[Memo]:
        """タスク化されていない未処理メモを抽出する。"""
        status_values = list(statuses or (MemoStatus.INBOX, MemoStatus.IDEA))
        created_col = cast("Any", Memo.created_at)
        status_col = cast("Any", Memo.status)
        tasks_rel = cast("Any", Memo.tasks)

        stmt = select(Memo)
        if created_after is not None:
            stmt = stmt.where(created_col >= created_after)

        stmt = stmt.where(status_col.in_(status_values)).where(~tasks_rel.any()).order_by(created_col.desc())

        if limit is not None and limit > 0:
            stmt = stmt.limit(limit)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)
