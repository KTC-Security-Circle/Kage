"""リポジトリの基底クラス"""

import uuid
from typing import Any, TypeVar

from loguru import logger
from sqlalchemy.orm import selectinload
from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

from models import BaseModel

_LoadOptionType = TypeVar("_LoadOptionType", bound=Any)


class MyBaseError(Exception):
    """カスタム例外クラス"""

    def __init__(self, arg: str = "") -> None:
        self.arg = arg


class CheckExistsError(MyBaseError):
    """エンティティ存在確認エラー

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"エンティティ存在確認エラー: {self.arg}"


class BaseRepository[T: BaseModel, CreateT: SQLModel, UpdateT: SQLModel]:
    """リポジトリの基底クラス

    依存性注入によりデータベースセッションを受け取り、
    CRUD操作の基本実装を提供する。
    """

    model_class: type[T]

    def __init__(self, session: Session, *, load_options: list[_LoadOptionType] | None = None) -> None:
        """リポジトリを初期化する

        Args:
            session: データベースセッション
            load_options: 関連エンティティの事前読み込みオプション（デフォルトはNone）
        """
        self.session = session
        self._eager_loading_options = load_options or []

        if not hasattr(self, "model_class"):
            msg = "model_class must be defined in the subclass"
            logger.error(msg)
            raise NotImplementedError(msg)

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

    def _get_by_statement(self, stmt: SelectOfScalar, entity: uuid.UUID | str) -> T:
        """カスタムステートメントでエンティティを取得する

        Args:
            stmt: カスタムのSQLAlchemyステートメント（デフォルトはNone）
            entity: 取得するエンティティ

        Returns:
            T | None: 取得されたエンティティ

        Raises:
            CheckExistsError: エンティティが存在しない場合
        """
        try:
            result = self.session.exec(stmt).first()
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の取得に失敗しました: {e}")
            raise

        if not result:
            msg = f"{self.model_class.__name__} が見つかりません: {entity}"
            logger.warning(msg)
            raise CheckExistsError(msg)

        logger.debug(f"{self.model_class.__name__} が見つかりました: {entity}")
        return result

    def _gets_by_statement(self, stmt: SelectOfScalar) -> list[T]:
        """カスタムステートメントでエンティティ一覧を取得する

        Args:
            stmt: カスタムのSQLAlchemyステートメント

        Returns:
            list[T]: 取得されたエンティティ一覧

        Raises:
            CheckExistsError: エンティティが存在しない場合
        """
        try:
            results = self.session.exec(stmt).all()
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の一覧取得に失敗しました: {e}")
            raise

        if not results:
            msg = f"{self.model_class.__name__} のエンティティが見つかりません。"
            logger.warning(msg)
            raise CheckExistsError(msg)

        logger.info(f"{self.model_class.__name__} のエンティティが {len(results)} 件見つかりました。")
        return list(results)

    def check_exists(self, entity_id: uuid.UUID) -> T:
        """エンティティが存在するか確認する

        check_exists は get_by_id を呼び出し、存在しない場合は CheckExistsError を発生させる
        リレーションが必要な場合は直接 get_by_id(with_details=True) を呼び出すこと

        Args:
            entity_id: 確認するエンティティのID

        Returns:
            T: 存在するエンティティ

        Raises:
            CheckExistsError: エンティティが存在しない場合
        """
        return self.get_by_id(entity_id)

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
            logger.info(f"{self.model_class.__name__} を作成しました: {entity.id}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の作成に失敗しました: {e}")
            raise
        return entity

    def get_by_id(self, entity_id: uuid.UUID, *, with_details: bool = False) -> T:
        """IDでエンティティを取得する

        Args:
            entity_id: 取得するエンティティのID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            T | None: 取得されたエンティティ

        Raises:
            CheckExistsError: エンティティが存在しない場合
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

    def update(self, entity_id: uuid.UUID, entity_data: UpdateT) -> T:
        """エンティティを更新する

        Args:
            entity_id: 更新するエンティティのID
            entity_data: 更新するデータ

        Returns:
            T | None: 更新されたエンティティ

        Raises:
            CheckExistsError: エンティティが存在しない場合
        """
        try:
            entity = self.check_exists(entity_id)

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
            entity = self.check_exists(entity_id)

            self.session.delete(entity)
            self.session.commit()
            logger.info(f"{self.model_class.__name__} を削除しました: {entity_id}")
        except CheckExistsError:
            logger.warning(f"{self.model_class.__name__} が見つかりません: {entity_id}")
            return False
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の削除に失敗しました: {e}")
            raise
        return True
