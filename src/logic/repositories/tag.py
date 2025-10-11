"""タグリポジトリの実装"""

from sqlmodel import Session, func, select

from logic.repositories.base import BaseRepository
from models import Tag, TagCreate, TagUpdate


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
            CheckExistsError: エンティティが存在しない場合
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
            CheckExistsError: エンティティが存在しない場合
        """
        stmt = select(Tag).where(func.lower(Tag.name).like(f"%{name_query.lower()}%"))

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)
