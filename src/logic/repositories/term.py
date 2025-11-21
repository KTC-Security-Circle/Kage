"""用語リポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, func, or_, select

from errors import AlreadyExistsError, NotFoundError
from logic.repositories.base import BaseRepository
from models import Synonym, Tag, Term, TermCreate, TermStatus, TermUpdate


class TermRepository(BaseRepository[Term, TermCreate, TermUpdate]):
    """用語リポジトリ

    用語の CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、用語固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """TermRepository を初期化する

        Args:
            session: データベースセッション
        """
        self.model_class = Term
        super().__init__(session, load_options=[Term.synonyms, Term.tags])

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
            raise NotFoundError(msg)
        return tag

    def create(self, entity_data: TermCreate) -> Term:
        """用語を作成する

        Args:
            entity_data: 作成する用語のデータ

        Returns:
            Term: 作成された用語

        Raises:
            AlreadyExistsError: 同じkeyの用語が既に存在する場合
        """
        # keyの重複チェック
        existing = self.session.exec(select(Term).where(Term.key == entity_data.key)).first()
        if existing:
            msg = f"用語キーが既に存在します: {entity_data.key}"
            raise AlreadyExistsError(msg)

        return super().create(entity_data)

    # ==============================================================================
    # Tag operations
    # ==============================================================================

    def add_tag(self, term_id: uuid.UUID, tag_id: uuid.UUID) -> Term:
        """用語にタグを追加する

        Args:
            term_id: 用語のID
            tag_id: 追加するタグのID

        Returns:
            Term: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        term = self.get_by_id(term_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        if tag not in term.tags:
            term.tags.append(tag)
            self._commit_and_refresh(term)
            logger.debug(f"用語({term_id})にタグ({tag_id})を追加しました。")
        else:
            logger.warning(f"用語({term_id})にタグ({tag_id})は既に追加されています。")

        return term

    def remove_tag(self, term_id: uuid.UUID, tag_id: uuid.UUID) -> Term:
        """用語からタグを削除する

        Args:
            term_id: 用語のID
            tag_id: 削除するタグのID

        Returns:
            Term: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        term = self.get_by_id(term_id, with_details=True)
        tag = self._check_exists_tag(tag_id)

        if tag in term.tags:
            term.tags.remove(tag)
            self._commit_and_refresh(term)
            logger.debug(f"用語({term_id})からタグ({tag_id})を削除しました。")
        else:
            logger.warning(f"用語({term_id})にタグ({tag_id})は存在しません。")

        return term

    def remove_all_tags(self, term_id: uuid.UUID) -> Term:
        """用語から全てのタグを削除する

        Args:
            term_id: 用語のID

        Returns:
            Term: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        term = self.get_by_id(term_id, with_details=True)

        if term.tags:
            num_tags = len(term.tags)
            term.tags.clear()
            self._commit_and_refresh(term)
            logger.debug(f"用語({term_id})から {num_tags} 件のタグを削除しました。")
        else:
            logger.warning(f"用語({term_id})にはタグが存在しません。")

        return term

    # ==============================================================================
    # Synonym operations
    # ==============================================================================

    def add_synonym(self, term_id: uuid.UUID, synonym_text: str) -> Term:
        """用語に同義語を追加する

        Args:
            term_id: 用語のID
            synonym_text: 同義語のテキスト

        Returns:
            Term: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        term = self.get_by_id(term_id, with_details=True)

        # 既に同じテキストの同義語が存在するかチェック
        if any(s.text == synonym_text for s in term.synonyms):
            logger.warning(f"用語({term_id})に同義語({synonym_text})は既に追加されています。")
            return term

        synonym = Synonym(text=synonym_text, term_id=term_id)
        term.synonyms.append(synonym)
        self._commit_and_refresh(term)
        logger.debug(f"用語({term_id})に同義語({synonym_text})を追加しました。")

        return term

    def remove_synonym(self, term_id: uuid.UUID, synonym_id: uuid.UUID) -> Term:
        """用語から同義語を削除する

        Args:
            term_id: 用語のID
            synonym_id: 削除する同義語のID

        Returns:
            Term: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        term = self.get_by_id(term_id, with_details=True)

        synonym = next((s for s in term.synonyms if s.id == synonym_id), None)
        if synonym:
            term.synonyms.remove(synonym)
            self._commit_and_refresh(term)
            logger.debug(f"用語({term_id})から同義語({synonym_id})を削除しました。")
        else:
            logger.warning(f"用語({term_id})に同義語({synonym_id})は存在しません。")

        return term

    # ==============================================================================
    # Search operations
    # ==============================================================================

    def get_by_key(self, key: str, *, with_details: bool = False) -> Term:
        """キーで用語を取得する

        Args:
            key: 用語のキー
            with_details: 関連エンティティを含めるかどうか

        Returns:
            Term: 取得された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        stmt = select(Term).where(Term.key == key)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._get_by_statement(stmt, key)

    def search(
        self,
        query: str | None = None,
        *,
        tags: list[uuid.UUID] | None = None,
        status: TermStatus | None = None,
        include_synonyms: bool = True,
        with_details: bool = False,
    ) -> list[Term]:
        """用語を検索する

        Args:
            query: 検索クエリ（キー、タイトル、説明を検索）
            tags: フィルタリングするタグのIDリスト
            status: フィルタリングするステータス
            include_synonyms: 同義語も検索対象に含めるか
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Term]: 検索条件に一致する用語一覧
        """
        stmt = select(Term).distinct()

        # クエリ文字列での検索
        if query:
            query_lower = query.lower()
            conditions = [
                func.lower(Term.key).like(f"%{query_lower}%"),
                func.lower(Term.title).like(f"%{query_lower}%"),
                func.lower(Term.description).like(f"%{query_lower}%"),
            ]

            # 同義語を含めた検索
            if include_synonyms:
                stmt = stmt.outerjoin(Synonym)
                conditions.append(func.lower(Synonym.text).like(f"%{query_lower}%"))

            stmt = stmt.where(or_(*conditions))

        # ステータスフィルタ
        if status:
            stmt = stmt.where(Term.status == status)

        # タグフィルタ
        if tags:
            # タグテーブルとJOINして、指定されたタグのいずれかを持つ用語を検索
            from sqlalchemy import column

            from models import TermTagLink

            stmt = stmt.join(TermTagLink).where(column("tag_id").in_(tags))

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        try:
            results = self.session.exec(stmt).all()
            logger.info(f"検索で {len(results)} 件の用語が見つかりました。")
            return list(results)
        except Exception as e:
            msg = "用語の検索に失敗しました"
            from errors import RepositoryError

            raise RepositoryError(msg) from e

    def get_by_tags(self, tag_ids: list[uuid.UUID], *, with_details: bool = False) -> list[Term]:
        """指定されたタグを持つ用語を取得する

        Args:
            tag_ids: タグのIDリスト
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Term]: 指定されたタグを持つ用語一覧
        """
        return self.search(tags=tag_ids, with_details=with_details)

    def get_by_status(self, status: TermStatus, *, with_details: bool = False) -> list[Term]:
        """指定されたステータスの用語を取得する

        Args:
            status: 用語のステータス
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[Term]: 指定されたステータスの用語一覧
        """
        return self.search(status=status, with_details=with_details)
