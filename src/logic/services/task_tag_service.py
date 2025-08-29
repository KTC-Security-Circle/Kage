"""タスクタグサービスの実装

このモジュールは、タスクタグに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なタスクタグ操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories.task_tag import TaskTagRepository
from logic.services.base import MyBaseError, ServiceBase
from models import TaskTagCreate, TaskTagRead


# Custom exceptions for task tag service errors
class TaskTagServiceCreateError(MyBaseError):
    """タスクタグ作成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスクタグ作成エラー: {self.arg}"


class TaskTagServiceCheckError(MyBaseError):
    """タスクタグ存在確認時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスクタグ存在確認エラー: {self.arg}"


class TaskTagServiceDeleteError(MyBaseError):
    """タスクタグ削除時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスクタグ削除エラー: {self.arg}"


class TaskTagServiceGetError(MyBaseError):
    """タスクタグ取得時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスクタグ取得エラー: {self.arg}"


type TaskTagServiceError = (
    TaskTagServiceGetError | TaskTagServiceCreateError | TaskTagServiceCheckError | TaskTagServiceDeleteError
)


class TaskTagService(ServiceBase[TaskTagServiceError]):
    """タスクタグサービス

    タスクタグに関するビジネスロジックを提供するサービスクラス。
    リポジトリ層を使用してデータアクセスを行い、複雑なタスクタグ操作を実装します。
    """

    def __init__(self, task_tag_repo: TaskTagRepository) -> None:
        """TaskTagServiceを初期化する

        Args:
            task_tag_repo: タスクタグリポジトリ
        """
        self.task_tag_repo = task_tag_repo

    def create_task_tag(self, task_tag_data: TaskTagCreate) -> TaskTagRead:
        """新しいタスクタグを作成する

        Args:
            task_tag_data: 作成するタスクタグのデータ

        Returns:
            TaskTagRead: 作成されたタスクタグ

        Raises:
            TaskTagServiceCreateError: タスクタグ作成に失敗した場合
        """
        try:
            # 既存のタスクタグが存在しないかチェック
            existing_task_tag = self.task_tag_repo.get_by_task_and_tag(task_tag_data.task_id, task_tag_data.tag_id)
            if existing_task_tag:
                self._log_error_and_raise(
                    f"タスクタグが既に存在します: Task {task_tag_data.task_id}, Tag {task_tag_data.tag_id}",
                    TaskTagServiceCreateError,
                )

            # タスクタグを作成
            created_task_tag = self.task_tag_repo.create(task_tag_data)
            logger.info(f"タスクタグ作成成功: Task {created_task_tag.task_id}, Tag {created_task_tag.tag_id}")
            return TaskTagRead.model_validate(created_task_tag)

        except Exception as e:
            self._log_error_and_raise(f"タスクタグ作成に失敗しました: {e}", TaskTagServiceCreateError)

    def get_all_task_tags(self) -> list[TaskTagRead]:
        """全てのタスクタグを取得する

        Returns:
            list[TaskTagRead]: タスクタグのリスト

        Raises:
            TaskTagServiceGetError: タスクタグ取得に失敗した場合
        """
        try:
            task_tags = self.task_tag_repo.get_all()
            return [TaskTagRead.model_validate(task_tag) for task_tag in task_tags]

        except Exception as e:
            self._log_error_and_raise(f"タスクタグ取得に失敗しました: {e}", TaskTagServiceGetError)

    def get_task_tags_by_task_id(self, task_id: uuid.UUID) -> list[TaskTagRead]:
        """指定されたタスクIDのタスクタグを取得する

        Args:
            task_id: タスクID

        Returns:
            list[TaskTagRead]: 指定されたタスクのタスクタグのリスト

        Raises:
            TaskTagServiceGetError: タスクタグ取得に失敗した場合
        """
        try:
            task_tags = self.task_tag_repo.get_by_task_id(task_id)
            return [TaskTagRead.model_validate(task_tag) for task_tag in task_tags]

        except Exception as e:
            self._log_error_and_raise(f"タスクのタスクタグ取得に失敗しました: {e}", TaskTagServiceGetError)

    def get_task_tags_by_tag_id(self, tag_id: uuid.UUID) -> list[TaskTagRead]:
        """指定されたタグIDのタスクタグを取得する

        Args:
            tag_id: タグID

        Returns:
            list[TaskTagRead]: 指定されたタグのタスクタグのリスト

        Raises:
            TaskTagServiceGetError: タスクタグ取得に失敗した場合
        """
        try:
            task_tags = self.task_tag_repo.get_by_tag_id(tag_id)
            return [TaskTagRead.model_validate(task_tag) for task_tag in task_tags]

        except Exception as e:
            self._log_error_and_raise(f"タグのタスクタグ取得に失敗しました: {e}", TaskTagServiceGetError)

    def get_task_tag_by_task_and_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> TaskTagRead | None:
        """指定されたタスクIDとタグIDのタスクタグを取得する

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            TaskTagRead | None: タスクタグ（存在しない場合はNone）

        Raises:
            TaskTagServiceGetError: タスクタグ取得に失敗した場合
        """
        try:
            task_tag = self.task_tag_repo.get_by_task_and_tag(task_id, tag_id)
        except Exception as e:
            self._log_error_and_raise(f"タスクタグ取得に失敗しました: {e}", TaskTagServiceGetError)
        else:
            if task_tag:
                return TaskTagRead.model_validate(task_tag)
            return None

    def delete_task_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        """タスクタグを削除する

        Args:
            task_id: タスクID
            tag_id: タグID

        Raises:
            TaskTagServiceDeleteError: タスクタグ削除に失敗した場合
            TaskTagServiceCheckError: タスクタグが存在しない場合
        """
        try:
            # タスクタグの存在確認
            existing_task_tag = self.task_tag_repo.get_by_task_and_tag(task_id, tag_id)
            if not existing_task_tag:
                self._log_error_and_raise(
                    f"削除対象のタスクタグが見つかりません: Task {task_id}, Tag {tag_id}",
                    TaskTagServiceCheckError,
                )

            # タスクタグを削除
            self.task_tag_repo.delete_by_task_and_tag(task_id, tag_id)
            logger.info(f"タスクタグ削除成功: Task {task_id}, Tag {tag_id}")

        except TaskTagServiceCheckError:
            raise
        except Exception as e:
            self._log_error_and_raise(f"タスクタグ削除に失敗しました: {e}", TaskTagServiceDeleteError)

    def delete_task_tags_by_task_id(self, task_id: uuid.UUID) -> None:
        """指定されたタスクIDの全てのタスクタグを削除する

        Args:
            task_id: タスクID

        Raises:
            TaskTagServiceDeleteError: タスクタグ削除に失敗した場合
        """
        try:
            deleted_count = self.task_tag_repo.delete_by_task_id(task_id)
            logger.info(f"タスクの全タスクタグ削除成功: Task {task_id}, 削除件数: {deleted_count}")

        except Exception as e:
            self._log_error_and_raise(f"タスクの全タスクタグ削除に失敗しました: {e}", TaskTagServiceDeleteError)

    def delete_task_tags_by_tag_id(self, tag_id: uuid.UUID) -> None:
        """指定されたタグIDの全てのタスクタグを削除する

        Args:
            tag_id: タグID

        Raises:
            TaskTagServiceDeleteError: タスクタグ削除に失敗した場合
        """
        try:
            deleted_count = self.task_tag_repo.delete_by_tag_id(tag_id)
            logger.info(f"タグの全タスクタグ削除成功: Tag {tag_id}, 削除件数: {deleted_count}")

        except Exception as e:
            self._log_error_and_raise(f"タグの全タスクタグ削除に失敗しました: {e}", TaskTagServiceDeleteError)

    def check_task_tag_exists(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """タスクタグが存在するかチェックする

        Args:
            task_id: タスクID
            tag_id: タグID

        Returns:
            bool: タスクタグが存在する場合True

        Raises:
            TaskTagServiceCheckError: タスクタグ存在確認に失敗した場合
        """
        try:
            task_tag = self.task_tag_repo.get_by_task_and_tag(task_id, tag_id)
        except Exception as e:
            self._log_error_and_raise(f"タスクタグ存在確認に失敗しました: {e}", TaskTagServiceCheckError)
        else:
            return task_tag is not None
