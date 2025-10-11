"""メモリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, select

from logic.repositories.base import BaseRepository
from models import Memo, MemoCreate, MemoStatus, MemoTagLink, MemoUpdate, Tag


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
        super().__init__(session, Memo, load_options=[Memo.tags, Memo.tasks])

    def add_tag_to_memo(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo | None:
        """メモにタグを追加する"""
        memo = self.get_by_id(memo_id, with_details=True)
        tag = self.session.get(Tag, tag_id)

        if not memo or not tag:
            logger.warning("メモまたはタグが見つかりません。")
            return None

        # 既に追加済みでないか確認
        if tag not in memo.tags:
            memo.tags.append(tag)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})にタグ({tag_id})を追加しました。")

        return memo

    def remove_tag_from_memo(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo | None:
        """メモからタグを削除する"""
        memo = self.get_by_id(memo_id, with_details=True)
        tag = self.session.get(Tag, tag_id)

        if not memo or not tag:
            logger.warning("メモまたはタグが見つかりません。")
            return None

        # タグがメモに存在するか確認
        if tag in memo.tags:
            memo.tags.remove(tag)
            self._commit_and_refresh(memo)
            logger.info(f"メモ({memo_id})からタグ({tag_id})を削除しました。")

        return memo

    # ==============================================================================
    # ==============================================================================
    # get functions
    # ==============================================================================
    # ==============================================================================

    def get_by_status(self, status: MemoStatus, *, with_details: bool = False) -> list[Memo] | None:
        """指定されたステータスのメモ一覧を取得する

        Args:
            status: メモステータス
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 指定された条件に一致するメモ一覧
        """
        stmt = select(Memo).where(Memo.status == status)
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)

    def get_by_tag(self, tag_id: uuid.UUID, *, with_details: bool = False) -> list[Memo] | None:
        """指定されたタグが付与されたメモ一覧を取得する

        Args:
            tag_id: タグID
            with_details: 詳細情報を含めるかどうか

        Returns:
            list[Memo]: 指定された条件に一致するメモ一覧
        """
        # 特定のタグが付与されたメモを取得
        stmt = select(Memo).join(MemoTagLink).join(Tag).where(Tag.id == tag_id)
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
        """
        stmt = select(Memo).where(func.lower(Memo.content).contains(func.lower(content_query)))
        if with_details:
            stmt = self._apply_eager_loading(stmt)
        return self._gets_by_statement(stmt)
