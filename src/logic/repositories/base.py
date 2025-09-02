"""リポジトリの基底クラス"""

import uuid

from loguru import logger
from sqlmodel import Session, SQLModel, select


class BaseRepository[T: SQLModel, CreateT: SQLModel, UpdateT: SQLModel]:
    """リポジトリの基底クラス

    依存性注入によりデータベースセッションを受け取り、
    CRUD操作の基本実装を提供する。
    """

    def __init__(self, model_class: type[T], session: Session) -> None:
        """リポジトリを初期化する

        Args:
            model_class: このリポジトリが扱うモデルクラス
            session: データベースセッション
        """
        self.model_class = model_class
        self.session = session

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
            entity = self.model_class(**entity_data.model_dump())
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            entity_id = getattr(entity, "id", "N/A")
            logger.info(f"{self.model_class.__name__} を作成しました: {entity_id}")
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の作成に失敗しました: {e}")
            raise
        return entity

    def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """IDでエンティティを取得する

        Args:
            entity_id: 取得するエンティティのID

        Returns:
            T | None: 取得されたエンティティ、見つからない場合はNone
        """
        try:
            # SQLModel の場合、通常 id フィールドはあるのでsession.getを使用
            result = self.session.get(self.model_class, entity_id)
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の取得に失敗しました: {e}")
            raise
        return result

    def get_all(self) -> list[T]:
        """全エンティティを取得する

        Returns:
            list[T]: 全エンティティのリスト
        """
        try:
            statement = select(self.model_class)
            results = self.session.exec(statement).all()
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の全取得に失敗しました: {e}")
            raise
        return list(results)

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
            for key, value in entity_data_dict.items():
                if value is not None:
                    setattr(entity, key, value)

            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
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
