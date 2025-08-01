"""[AI GENERATED] リポジトリの基底クラス"""

import uuid
from typing import Generic, TypeVar

from loguru import logger
from sqlmodel import Session, SQLModel, select

from config import engine

T = TypeVar("T", bound=SQLModel)
CreateT = TypeVar("CreateT", bound=SQLModel)
UpdateT = TypeVar("UpdateT", bound=SQLModel)


class BaseRepository(Generic[T, CreateT, UpdateT]):
    """[AI GENERATED] リポジトリの基底クラス"""

    def __init__(self, model_class: type[T]) -> None:
        """[AI GENERATED] リポジトリを初期化する

        Args:
            model_class: このリポジトリが扱うモデルクラス
        """
        self.engine = engine
        self.model_class = model_class

    def create(self, entity_data: CreateT) -> T:
        """[AI GENERATED] エンティティを作成する

        Args:
            entity_data: 作成するエンティティのデータ

        Returns:
            T: 作成されたエンティティ

        Raises:
            Exception: データベース操作エラー
        """
        try:
            with Session(self.engine) as session:
                entity = self.model_class(**entity_data.model_dump())
                session.add(entity)
                session.commit()
                session.refresh(entity)
                entity_id = getattr(entity, "id", "N/A")
                logger.info(f"{self.model_class.__name__} を作成しました: {entity_id}")
                return entity
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の作成に失敗しました: {e}")
            raise

    def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """[AI GENERATED] IDでエンティティを取得する

        Args:
            entity_id: 取得するエンティティのID

        Returns:
            T | None: 取得されたエンティティ、見つからない場合はNone
        """
        try:
            with Session(self.engine) as session:
                # SQLModel の場合、通常 id フィールドはあるのでsession.getを使用
                result = session.get(self.model_class, entity_id)
                if result:
                    logger.debug(f"{self.model_class.__name__} を取得しました: {entity_id}")
                return result
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の取得に失敗しました: {e}")
            raise

    def get_all(self) -> list[T]:
        """[AI GENERATED] 全エンティティを取得する

        Returns:
            list[T]: 全エンティティのリスト
        """
        try:
            with Session(self.engine) as session:
                statement = select(self.model_class)
                results = session.exec(statement).all()
                logger.debug(f"{self.model_class.__name__} を {len(results)} 件取得しました")
                return list(results)
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の全取得に失敗しました: {e}")
            raise

    def update(self, entity_id: uuid.UUID, entity_data: UpdateT) -> T | None:
        """[AI GENERATED] エンティティを更新する

        Args:
            entity_id: 更新するエンティティのID
            entity_data: 更新するデータ

        Returns:
            T | None: 更新されたエンティティ、見つからない場合はNone
        """
        try:
            with Session(self.engine) as session:
                entity = session.get(self.model_class, entity_id)
                if entity is None:
                    logger.warning(f"{self.model_class.__name__} が見つかりません: {entity_id}")
                    return None

                # None でない値のみ更新
                entity_data_dict = entity_data.model_dump(exclude_unset=True)
                for key, value in entity_data_dict.items():
                    if value is not None:
                        setattr(entity, key, value)

                session.add(entity)
                session.commit()
                session.refresh(entity)
                logger.info(f"{self.model_class.__name__} を更新しました: {entity_id}")
                return entity
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の更新に失敗しました: {e}")
            raise

    def delete(self, entity_id: uuid.UUID) -> bool:
        """[AI GENERATED] エンティティを削除する

        Args:
            entity_id: 削除するエンティティのID

        Returns:
            bool: 削除が成功した場合True、見つからない場合False
        """
        try:
            with Session(self.engine) as session:
                entity = session.get(self.model_class, entity_id)
                if entity is None:
                    logger.warning(f"{self.model_class.__name__} が見つかりません: {entity_id}")
                    return False

                session.delete(entity)
                session.commit()
                logger.info(f"{self.model_class.__name__} を削除しました: {entity_id}")
                return True
        except Exception as e:
            logger.exception(f"{self.model_class.__name__} の削除に失敗しました: {e}")
            raise
