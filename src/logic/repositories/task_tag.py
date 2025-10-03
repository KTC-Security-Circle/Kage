"""タスクタグリポジトリの実装"""

import uuid

from loguru import logger
from sqlmodel import Session, select

from logic.repositories.base import BaseRepository
from models import TaskTag, TaskTagCreate


class TaskTagRepository(BaseRepository[TaskTag, TaskTagCreate, TaskTagCreate]):
    """タスクタグリポジトリ

    タスクとタグの関連の CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、タスクタグ固有の操作を追加実装。

    Note: TaskTagは更新操作がないため、UpdateTにもTaskTagCreateを使用
    TaskTagは複合主キーのため、一部のBaseRepositoryメソッドはオーバーライドが必要
    """

    def __init__(self, session: Session) -> None:
        """TaskTagRepository を初期化する

        Args:
            session: データベースセッション
        """
        self.model_class = TaskTag
        super().__init__(session)

    def get_by_id(self, entity_id: uuid.UUID) -> TaskTag | None:  # noqa: ARG002
        """TaskTagは複合主キーのため、このメソッドは使用しない

        Args:
            entity_id: 使用されない

        Returns:
            None: 常にNone

        Note:
            TaskTagは複合主キー(task_id, tag_id)のため、代わりにget_by_task_and_tag()を使用
        """
        logger.warning("TaskTagはget_by_id()をサポートしていません。get_by_task_and_tag()を使用してください。")
        return None

    def update(self, entity_id: uuid.UUID, entity_data: TaskTagCreate) -> TaskTag | None:  # noqa: ARG002
        """TaskTagは更新操作をサポートしない

        Args:
            entity_id: 使用されない
            entity_data: 使用されない

        Returns:
            None: 常にNone

        Note:
            TaskTagは関連テーブルのため更新操作はサポートしない。
            代わりに削除後に再作成を行う。
        """
        logger.warning("TaskTagは更新操作をサポートしていません。削除後に再作成してください。")
        return None

    def delete(self, entity_id: uuid.UUID) -> bool:  # noqa: ARG002
        """TaskTagは複合主キーのため、このメソッドは使用しない

        Args:
            entity_id: 使用されない

        Returns:
            False: 常にFalse

        Note:
            TaskTagは複合主キー(task_id, tag_id)のため、代わりにdelete_by_task_and_tag()を使用
        """
        logger.warning("TaskTagはdelete()をサポートしていません。delete_by_task_and_tag()を使用してください。")
        return False

    def get_by_task_id(self, task_id: uuid.UUID) -> list[TaskTag]:
        """指定されたタスクIDの関連一覧を取得する

        Args:
            task_id: タスクID

        Returns:
            list[TaskTag]: 指定されたタスクの関連一覧
        """
        try:
            statement = select(TaskTag).where(TaskTag.task_id == task_id)
            results = self.session.exec(statement).all()
            logger.debug(f"タスク {task_id} の関連を {len(results)} 件取得しました")
            return list(results)
        except Exception as e:
            logger.exception(f"タスクの関連取得に失敗しました: {e}")
            raise

    def get_by_tag_id(self, tag_id: uuid.UUID) -> list[TaskTag]:
        """指定されたタグIDの関連一覧を取得する

        Args:
            tag_id: タグID

        Returns:
            list[TaskTag]: 指定されたタグの関連一覧
        """
        try:
            statement = select(TaskTag).where(TaskTag.tag_id == tag_id)
            results = self.session.exec(statement).all()
            logger.debug(f"タグ {tag_id} の関連を {len(results)} 件取得しました")
            return list(results)
        except Exception as e:
            logger.exception(f"タグの関連取得に失敗しました: {e}")
            raise

    def get_by_task_and_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> TaskTag | None:
        """指定されたタスクIDとタグIDの関連を取得する

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            TaskTag | None: 指定された条件に一致する関連、見つからない場合はNone
        """
        try:
            statement = select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id)
            result = self.session.exec(statement).first()
            if result:
                logger.debug(f"タスク {task_id} とタグ {tag_id} の関連を取得しました")
        except Exception as e:
            logger.exception(f"タスクタグ関連の取得に失敗しました: {e}")
            raise
        else:
            return result

    def exists(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """指定されたタスクIDとタグIDの関連が存在するかチェックする

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            bool: 関連が存在する場合True、存在しない場合False
        """
        try:
            return self.get_by_task_and_tag(task_id, tag_id) is not None
        except Exception as e:
            logger.exception(f"タスクタグ関連の存在チェックに失敗しました: {e}")
            raise

    def delete_by_task_and_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """指定されたタスクIDとタグIDの関連を削除する

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            bool: 削除が成功した場合True、見つからない場合False
        """
        try:
            statement = select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id)
            task_tag = self.session.exec(statement).first()

            if task_tag is None:
                logger.warning(f"タスクタグ関連が見つかりません: task_id={task_id}, tag_id={tag_id}")
                return False

            self.session.delete(task_tag)
            self.session.commit()
            logger.info(f"タスクタグ関連を削除しました: task_id={task_id}, tag_id={tag_id}")
        except Exception as e:
            logger.exception(f"タスクタグ関連の削除に失敗しました: {e}")
            raise
        else:
            return True

    def delete_by_task_id(self, task_id: uuid.UUID) -> int:
        """指定されたタスクIDの全ての関連を削除する

        Args:
            task_id: タスクID

        Returns:
            int: 削除された関連の数
        """
        try:
            statement = select(TaskTag).where(TaskTag.task_id == task_id)
            task_tags = self.session.exec(statement).all()

            count = len(task_tags)
            for task_tag in task_tags:
                self.session.delete(task_tag)

            self.session.commit()
            logger.info(f"タスク {task_id} の関連を {count} 件削除しました")
        except Exception as e:
            logger.exception(f"タスクの全関連削除に失敗しました: {e}")
            raise
        else:
            return count

    def delete_by_tag_id(self, tag_id: uuid.UUID) -> int:
        """指定されたタグIDの全ての関連を削除する

        Args:
            tag_id: タグID

        Returns:
            int: 削除された関連の数
        """
        try:
            statement = select(TaskTag).where(TaskTag.tag_id == tag_id)
            task_tags = self.session.exec(statement).all()

            count = len(task_tags)
            for task_tag in task_tags:
                self.session.delete(task_tag)

            self.session.commit()
            logger.info(f"タグ {tag_id} の関連を {count} 件削除しました")
        except Exception as e:
            logger.exception(f"タグの全関連削除に失敗しました: {e}")
            raise
        else:
            return count
