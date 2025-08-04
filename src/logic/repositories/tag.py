"""[AI GENERATED] タグリポジトリの実装"""

from loguru import logger
from sqlmodel import Session, select

from logic.repositories.base import BaseRepository
from models import Tag, TagCreate, TagUpdate


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    """[AI GENERATED] タグリポジトリ

    タグの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、タグ固有の操作を追加実装。
    """

    def __init__(self) -> None:
        """[AI GENERATED] TagRepository を初期化する"""
        super().__init__(Tag)

    def get_all(self) -> list[Tag]:
        """[AI GENERATED] 全てのタグ一覧を取得する

        Returns:
            list[Tag]: 全てのタグ一覧
        """
        try:
            with Session(self.engine) as session:
                statement = select(Tag)
                results = session.exec(statement).all()
                logger.debug(f"タグを {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"タグ取得に失敗しました: {e}")
            raise

    def get_by_name(self, name: str) -> Tag | None:
        """[AI GENERATED] 指定されたタグ名でタグを取得する

        Args:
            name: タグ名

        Returns:
            Tag | None: 指定された条件に一致するタグ、見つからない場合はNone
        """
        try:
            with Session(self.engine) as session:
                statement = select(Tag).where(Tag.name == name)
                result = session.exec(statement).first()
                if result:
                    logger.debug(f"タグ '{name}' を取得しました")
                return result
        except Exception as e:
            logger.exception(f"タグ名での取得に失敗しました: {e}")
            raise

    def search_by_name(self, name_query: str) -> list[Tag]:
        """[AI GENERATED] タグ名でタグを検索する

        Args:
            name_query: 検索クエリ（部分一致）

        Returns:
            list[Tag]: 検索条件に一致するタグ一覧
        """
        try:
            with Session(self.engine) as session:
                # Python側でフィルタリングを実行
                statement = select(Tag)
                all_tags = session.exec(statement).all()

                # タグ名に検索クエリが含まれるタグをフィルタリング
                filtered_tags = [tag for tag in all_tags if name_query.lower() in tag.name.lower()]

                logger.debug(f"タグ名検索 '{name_query}' で {len(filtered_tags)} 件取得しました")
                return filtered_tags
        except Exception as e:
            logger.exception(f"タグ名検索に失敗しました: {e}")
            raise

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
