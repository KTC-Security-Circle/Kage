"""タグリポジトリの実装"""

from loguru import logger
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
        super().__init__(Tag, session)

    def get_all(self) -> list[Tag]:
        """全てのタグ一覧を取得する

        Returns:
            list[Tag]: 全てのタグ一覧
        """
        try:
            statement = select(Tag)
            results = self.session.exec(statement).all()
            logger.debug(f"タグを {len(results)} 件取得しました")
            return list(results)
        except Exception as e:
            logger.exception(f"タグ取得に失敗しました: {e}")
            raise

    def get_by_name(self, name: str) -> Tag | None:
        """指定されたタグ名でタグを取得する

        Args:
            name: タグ名

        Returns:
            Tag | None: 指定された条件に一致するタグ、見つからない場合はNone
        """
        try:
            statement = select(Tag).where(Tag.name == name)
            result = self.session.exec(statement).first()
            if result:
                logger.debug(f"タグ '{name}' を取得しました")
        except Exception as e:
            logger.exception(f"タグ名での取得に失敗しました: {e}")
            raise
        else:
            return result

    def search_by_name(self, name_query: str) -> list[Tag]:
        """タグ名でタグを検索する

        Args:
            name_query: 検索クエリ（部分一致）

        Returns:
            list[Tag]: 検索条件に一致するタグ一覧
        """
        try:
            # SQLModelでフィルタリングを実行（大きめの検索が来た際にPython側だと遅くなるため）
            # [AI GENERATED] 大文字小文字を区別しない検索のためfunc.lower()を使用
            statement = select(Tag).where(func.lower(Tag.name).contains(func.lower(name_query)))  # pyright: ignore[reportAttributeAccessIssue]
            filtered_tags = list(self.session.exec(statement).all())

            logger.debug(f"タグ名検索 '{name_query}' で {len(filtered_tags)} 件取得しました")
        except Exception as e:
            logger.exception(f"タグ名検索に失敗しました: {e}")
            raise
        else:
            return filtered_tags

    def exists_by_name(self, name: str) -> bool:
        """[AI GENERATED] 指定されたタグ名でタグが存在するかチェックする

        Args:
            name: タグ名

        Returns:
            bool: タグが存在する場合True、存在しない場合False
        """
        try:
            return self.get_by_name(name) is not None
        except Exception as e:
            logger.exception(f"タグ存在チェックに失敗しました: {e}")
            raise
