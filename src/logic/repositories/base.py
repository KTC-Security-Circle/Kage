"""リポジトリの基底クラス"""

import uuid
from typing import Any, TypeVar

from loguru import logger
from sqlalchemy.orm import selectinload
from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

from models import BaseModel

_LoadOptionType = TypeVar("_LoadOptionType", bound=Any)


class BaseRepository[T: BaseModel, CreateT: SQLModel, UpdateT: SQLModel]:
    """リポジトリの基底クラス

    依存性注入によりデータベースセッションを受け取り、
    CRUD操作の基本実装を提供する。
    """

    def __init__(
        self, session: Session, model_class: type[T], load_options: list[_LoadOptionType] | None = None
    ) -> None:
        """リポジトリを初期化する

        Args:
            session: データベースセッション
            model_class: このリポジトリが扱うモデルクラス
            load_options: 関連エンティティの事前読み込みオプション（デフォルトはNone）
        """
        self.session = session
        self.model_class = model_class
        self._eager_loading_options = load_options or []

    def _commit_and_refresh(self, entity: T) -> None:
        """エンティティをコミットしてリフレッシュする"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

    # _eager_loading_options があるかチェックして、あれば selectinload を使用して関連エンティティを事前読み込み
    def _apply_eager_loading(self, stmt: SelectOfScalar) -> SelectOfScalar:
        if self._eager_loading_options:
            stmt = stmt.options(*[selectinload(opt) for opt in self._eager_loading_options])
        return stmt

    def _get_by_statement(self, stmt: SelectOfScalar, entity: uuid.UUID | str) -> T | None:
        """カスタムステートメントでエンティティを取得する

        Args:
            stmt: カスタムのSQLAlchemyステートメント（デフォルトはNone）
            entity: 取得するエンティティ

        Returns:
            T | None: 取得されたエンティティ、見つからない場合はNone
        """
        try:
            result = self.session.exec(stmt).first()
            if result:
                logger.info(f"{self.model_class.__name__} リポジトリ: エンティティが見つかりました {entity}")
            else:
                logger.warning(f"{self.model_class.__name__} リポジトリ: エンティティが見つかりませんでした {entity}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の取得に失敗しました: {e}")
            raise
        return result

    def _gets_by_statement(self, stmt: SelectOfScalar) -> list[T]:
        """カスタムステートメントでエンティティ一覧を取得する

        Args:
            stmt: カスタムのSQLAlchemyステートメント

        Returns:
            list[T]: 取得されたエンティティ一覧
        """
        try:
            results = self.session.exec(stmt).all()
            if results:
                logger.info(
                    f"{self.model_class.__name__} リポジトリ: エンティティ一覧が見つかりました。件数: {len(results)}"
                )
            else:
                logger.warning(f"{self.model_class.__name__} リポジトリ: エンティティ一覧が見つかりませんでした。")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の一覧取得に失敗しました: {e}")
            raise
        return list(results)

    def create(self, entity_data: CreateT) -> T:
        """エンティティを作成する

        Args:
            entity_data: 作成するエンティティのデータ

        Returns:
            T: 作成されたエンティティ

        Raises:
            Exception: データベース操作エラー
        """
        try:
            data = entity_data.model_dump(exclude_unset=True, exclude_none=True)
            entity = self.model_class.model_validate(data)
            self._commit_and_refresh(entity)
            entity_id = getattr(entity, "id", "N/A")
            logger.info(f"{self.model_class.__name__} を作成しました: {entity_id}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の作成に失敗しました: {e}")
            raise
        return entity

    def get_by_id(self, entity_id: uuid.UUID, *, with_details: bool = False) -> T | None:
        """IDでエンティティを取得する

        Args:
            entity_id: 取得するエンティティのID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            T | None: 取得されたエンティティ、見つからない場合はNone
        """
        stmt = select(self.model_class).where(self.model_class.id == entity_id)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._get_by_statement(stmt, entity_id)

    def get_all(self, *, with_details: bool = False) -> list[T]:
        """全エンティティを取得する

        Returns:
            list[T]: 全エンティティのリスト
        """
        stmt = select(self.model_class)

        if with_details:
            stmt = self._apply_eager_loading(stmt)

        return self._gets_by_statement(stmt)

    def update(self, entity_id: uuid.UUID, entity_data: UpdateT) -> T | None:
        """エンティティを更新する

        Args:
            entity_id: 更新するエンティティのID
            entity_data: 更新するデータ

        Returns:
            T | None: 更新されたエンティティ、見つからない場合はNone
        """
        try:
            entity = self.session.get(self.model_class, entity_id)
            if entity is None:
                logger.warning(f"{self.model_class.__name__} が見つかりません: {entity_id}")
                return None

            # None でない値のみ更新
            entity_data_dict = entity_data.model_dump(exclude_unset=True)
            entity.sqlmodel_update(entity_data_dict)

            self._commit_and_refresh(entity)
            logger.info(f"{self.model_class.__name__} を更新しました: {entity_id}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の更新に失敗しました: {e}")
            raise
        return entity

    def delete(self, entity_id: uuid.UUID) -> bool:
        """エンティティを削除する

        Args:
            entity_id: 削除するエンティティのID

        Returns:
            bool: 削除が成功した場合True、見つからない場合False
        """
        try:
            entity = self.session.get(self.model_class, entity_id)
            if entity is None:
                logger.warning(f"{self.model_class.__name__} が見つかりません: {entity_id}")
                return False

            self.session.delete(entity)
            self.session.commit()
            logger.info(f"{self.model_class.__name__} を削除しました: {entity_id}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の削除に失敗しました: {e}")
            raise
        return True
