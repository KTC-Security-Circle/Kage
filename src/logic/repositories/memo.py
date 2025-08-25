"""メモリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, select, func

from logic.repositories.base import BaseRepository
from models import Memo, MemoCreate, MemoUpdate


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
        super().__init__(Memo, session)

    def get_by_task_id(self, task_id: uuid.UUID) -> list[Memo]:
        """指定されたタスクIDのメモ一覧を取得する

        Args:
            task_id: タスクID

        Returns:
            list[Memo]: 指定されたタスクのメモ一覧

        Raises:
            Exception: データベース操作エラー
        """
        try:
            statement = select(Memo).where(Memo.task_id == task_id)
            results = self.session.exec(statement).all()
            return list(results)
        except Exception as e:
            logger.exception(f"タスクのメモ取得に失敗しました: {e}")
            raise

    def search_by_content(self, content_query: str) -> list[Memo]:
        """メモ内容でメモを検索する

        Args:
            content_query: 検索クエリ（部分一致）

        Returns:
            list[Memo]: 検索条件に一致するメモ一覧

        Raises:
            Exception: データベース操作エラー
        """
        try:
            # SQLModelでフィルタリングを実行（大きめの検索が来た際にPython側だと遅くなるため）
            # [AI GENERATED] 大文字小文字を区別しない検索のためfunc.lower()を使用
            statement = select(Memo).where(func.lower(Memo.content).contains(func.lower(content_query)))  # pyright: ignore[reportAttributeAccessIssue]
            filtered_memos = list(self.session.exec(statement).all())

        except Exception as e:
            logger.exception(f"メモ内容検索に失敗しました: {e}")
            raise
        else:
            return filtered_memos
