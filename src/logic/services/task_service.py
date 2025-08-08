"""タスクサービスの実装

このモジュールは、タスクに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なタスク操作を実装します。
"""

import datetime
import uuid

from loguru import logger

from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.base import MyBaseError, ServiceBase
from models import TagRead, TaskCreate, TaskRead, TaskStatus, TaskTag, TaskTagCreate, TaskUpdate


# Custom exceptions for task service errors
class TaskServiceCreateError(MyBaseError):
    """タスク作成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスク作成エラー: {self.arg}"


class TaskServiceCheckError(MyBaseError):
    """タスク存在確認時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスク存在確認エラー: {self.arg}"


class TaskServiceUpdateError(MyBaseError):
    """タスク更新時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスク更新エラー: {self.arg}"


class TaskServiceDeleteError(MyBaseError):
    """タスク削除時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスク削除エラー: {self.arg}"


class TaskServiceGetError(MyBaseError):
    """タスク取得時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タスク取得エラー: {self.arg}"


type TaskServiceError = (
    TaskServiceGetError
    | TaskServiceCreateError
    | TaskServiceCheckError
    | TaskServiceUpdateError
    | TaskServiceDeleteError
)


class TaskService(ServiceBase[TaskServiceError]):
    """タスクサービス

    タスクに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なタスク操作を実装します。
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        tag_repo: TagRepository,
        task_tag_repo: TaskTagRepository,
    ) -> None:
        """TaskServiceを初期化する

        Args:
            task_repo: タスクリポジトリ
            project_repo: プロジェクトリポジトリ
            tag_repo: タグリポジトリ
            task_tag_repo: タスクタグリポジトリ
        """
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.tag_repo = tag_repo
        self.task_tag_repo = task_tag_repo

    # タスクの存在を確認するメソッド
    def _check_task_exists(self, task_id: uuid.UUID) -> TaskRead:
        """タスクの存在を確認する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 存在するタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task = self.task_repo.get_by_id(task_id)
        if not task:
            self._log_error_and_raise(f"タスクID {task_id} が見つかりません", TaskServiceCheckError)
        return TaskRead.model_validate(task)

    def create_task(self, task_data: TaskCreate) -> TaskRead:
        """新しいタスクを作成する

        Args:
            task_data: 作成するタスクのデータ

        Returns:
            TaskRead: 作成されたタスク

        Raises:
            TaskServiceCreateError: プロジェクトIDが指定されているが存在しない場合、またはタスク作成に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        # プロジェクトIDが指定されている場合、存在を確認
        if task_data.project_id is not None:
            project = self.project_repo.get_by_id(task_data.project_id)
            if not project:
                self._log_error_and_raise(
                    f"プロジェクトID {task_data.project_id} が見つかりません", TaskServiceCreateError
                )

        task = self.task_repo.create(task_data)
        if not task:
            self._log_error_and_raise("タスクの作成に失敗しました", TaskServiceCreateError)

        logger.info(f"タスク '{task.title}' を作成しました (ID: {task.id})")
        return TaskRead.model_validate(task)

    def update_task(self, task_id: uuid.UUID, task_data: TaskUpdate) -> TaskRead:
        """タスクを更新する

        Args:
            task_id: 更新するタスクのID
            task_data: 更新するタスクのデータ

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: プロジェクトIDが無効な場合、またはタスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        # タスクの存在を確認
        self._check_task_exists(task_id)

        # プロジェクトIDが指定されている場合、存在を確認
        if task_data.project_id is not None:
            project = self.project_repo.get_by_id(task_data.project_id)
            if not project:
                self._log_error_and_raise(
                    f"プロジェクトID {task_data.project_id} が見つかりません", TaskServiceUpdateError
                )

        updated_task = self.task_repo.update(task_id, task_data)
        if not updated_task:
            self._log_error_and_raise(f"タスクの更新に失敗しました (ID: {task_id})", TaskServiceUpdateError)

        logger.info(f"タスク '{updated_task.title}' を更新しました (ID: {task_id})")
        return TaskRead.model_validate(updated_task)

    def delete_task(self, task_id: uuid.UUID) -> bool:
        """タスクを削除する

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除が成功した場合True

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceDeleteError: タスク削除に失敗した場合
        """
        # タスクの存在を確認
        existing_task = self._check_task_exists(task_id)

        # 関連するタスクタグを削除
        task_tags = self.task_tag_repo.get_by_task_id(task_id)
        for task_tag in task_tags:
            self.task_tag_repo.delete_by_task_and_tag(task_tag.task_id, task_tag.tag_id)

        success = self.task_repo.delete(task_id)
        if not success:
            self._log_error_and_raise(f"タスクの削除に失敗しました (ID: {task_id})", TaskServiceDeleteError)

        logger.info(f"タスク '{existing_task.title}' を削除しました (ID: {task_id})")
        return success

    def get_task_by_id(self, task_id: uuid.UUID) -> TaskRead | None:
        """IDでタスクを取得する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead | None: 見つかったタスク、存在しない場合はNone

        Raises:
            TaskServiceGetError: タスク取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            if not task:
                self._log_error_and_raise(f"タスクID {task_id} が見つかりません", TaskServiceGetError)
            return TaskRead.model_validate(task)
        except Exception:
            self._log_error_and_raise(f"タスクの取得に失敗しました (ID: {task_id})", TaskServiceGetError)

    def get_all_tasks(self) -> list[TaskRead]:
        """全てのタスクを取得する

        Returns:
            list[TaskRead]: 全てのタスクのリスト

        Raises:
            TaskServiceGetError: タスク一覧の取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        try:
            tasks = self.task_repo.get_all()
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception:
            self._log_error_and_raise("タスク一覧の取得に失敗しました", TaskServiceGetError)

    def get_tasks_by_status(self, status: TaskStatus) -> list[TaskRead]:
        """指定されたステータスのタスクを取得する

        Args:
            status: タスクステータス

        Returns:
            list[TaskRead]: 指定されたステータスのタスクのリスト

        Raises:
            TaskServiceGetError: ステータス別タスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        try:
            tasks = self.task_repo.get_by_status(status)
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception:
            self._log_error_and_raise(f"ステータス '{status}' のタスク取得に失敗しました", TaskServiceGetError)

    def get_tasks_by_project_id(self, project_id: uuid.UUID) -> list[TaskRead]:
        """プロジェクトIDでタスクを取得する

        Args:
            project_id: プロジェクトのID

        Returns:
            list[TaskRead]: 指定されたプロジェクトのタスクのリスト

        Raises:
            TaskServiceGetError: プロジェクト別タスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        try:
            tasks = self.task_repo.get_by_project_id(project_id)
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception:
            self._log_error_and_raise("プロジェクト別タスクの取得に失敗しました", TaskServiceGetError)

    def search_tasks(self, query: str) -> list[TaskRead]:
        """タスクをタイトルで検索する

        Args:
            query: 検索クエリ

        Returns:
            list[TaskRead]: 検索条件に一致するタスクのリスト

        Raises:
            TaskServiceGetError: タスクの検索に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        try:
            tasks = self.task_repo.search_by_title(query)
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception:
            self._log_error_and_raise("タスクの検索に失敗しました", TaskServiceGetError)

    def add_tag_to_task(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> TaskTag:
        """タスクにタグを追加する

        Args:
            task_id: タスクのID
            tag_id: タグのID

        Returns:
            TaskTag: 作成されたタスクタグの関連

        Raises:
            TaskServiceCheckError: タスクまたはタグが存在しない場合
            TaskServiceCreateError: タスクタグの作成に失敗した場合
        """
        # タスクとタグの存在を確認
        self._check_task_exists(task_id)
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            self._log_error_and_raise(f"タグID {tag_id} が見つかりません", TaskServiceCheckError)

        task_tag_data = TaskTagCreate(task_id=task_id, tag_id=tag_id)
        task_tag = self.task_tag_repo.create(task_tag_data)
        if not task_tag:
            self._log_error_and_raise("タスクタグの作成に失敗しました", TaskServiceCreateError)

        logger.info(f"タスク '{task_id}' にタグ '{tag.name}' を追加しました")
        return task_tag

    def remove_tag_from_task(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """タスクからタグを削除する

        Args:
            task_id: タスクのID
            tag_id: タグのID

        Returns:
            bool: 削除が成功した場合True

        Raises:
            TaskServiceCheckError: タスクまたはタグが存在しない場合
            TaskServiceDeleteError: タスクタグの削除に失敗した場合
        """
        # タスクとタグの存在を確認
        self._check_task_exists(task_id)
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            self._log_error_and_raise(f"タグID {tag_id} が見つかりません", TaskServiceCheckError)

        # タスクタグの関連が存在するか確認
        task_tag = self.task_tag_repo.get_by_task_and_tag(task_id, tag_id)
        if not task_tag:
            self._log_error_and_raise("タスクタグの関連が見つかりません", TaskServiceCheckError)

        success = self.task_tag_repo.delete_by_task_and_tag(task_id, tag_id)
        if not success:
            self._log_error_and_raise("タスクタグの削除に失敗しました", TaskServiceDeleteError)

        logger.info(f"タスク '{task_id}' からタグ '{tag.name}' を削除しました")
        return success

    def get_task_tags(self, task_id: uuid.UUID) -> list[TagRead]:
        """タスクに関連するタグを取得する

        Args:
            task_id: タスクのID

        Returns:
            list[TagRead]: タスクに関連するタグのリスト

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceGetError: タグ取得に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        # タスクの存在を確認
        self._check_task_exists(task_id)

        try:
            task_tags = self.task_tag_repo.get_by_task_id(task_id)
            tags = []
            for task_tag in task_tags:
                tag = self.tag_repo.get_by_id(task_tag.tag_id)
                if tag:
                    tags.append(TagRead.model_validate(tag))
        except Exception:
            self._log_error_and_raise("タグ取得に失敗しました", TaskServiceGetError)
        return tags

    def complete_task(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを完了する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.COMPLETED)
        return self.update_task(task_id, task_data)

    def start_task(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを次のアクション状態にする

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.NEXT_ACTION)
        return self.update_task(task_id, task_data)

    def pause_task(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを待機状態にする

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.WAITING_FOR)
        return self.update_task(task_id, task_data)

    def cancel_task(self, task_id: uuid.UUID) -> TaskRead:
        """タスクをキャンセルする

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.CANCELLED)
        return self.update_task(task_id, task_data)

    def get_inbox_tasks(self) -> list[TaskRead]:
        """インボックス状態のタスクを取得する

        Returns:
            list[TaskRead]: インボックス状態のタスクのリスト

        Raises:
            TaskServiceGetError: インボックスタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.INBOX)

    def get_next_action_tasks(self) -> list[TaskRead]:
        """次のアクション状態のタスクを取得する

        Returns:
            list[TaskRead]: 次のアクション状態のタスクのリスト

        Raises:
            TaskServiceGetError: 次のアクションタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.NEXT_ACTION)

    def get_waiting_for_tasks(self) -> list[TaskRead]:
        """待機中のタスクを取得する

        Returns:
            list[TaskRead]: 待機中のタスクのリスト

        Raises:
            TaskServiceGetError: 待機中タスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.WAITING_FOR)

    def get_someday_maybe_tasks(self) -> list[TaskRead]:
        """いつかやるタスクを取得する

        Returns:
            list[TaskRead]: いつかやるタスクのリスト

        Raises:
            TaskServiceGetError: いつかやるタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.SOMEDAY_MAYBE)

    # 今日のタスクを取得するメソッド
    def get_today_tasks(self) -> list[TaskRead]:
        """今日のタスクを取得する

        Returns:
            list[TaskRead]: 今日のタスクのリスト

        Raises:
            TaskServiceGetError: 今日のタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        today_tasks = self.task_repo.get_by_due_date(datetime.datetime.now(tz=datetime.UTC).date())
        return [TaskRead.model_validate(task) for task in today_tasks]

    def get_today_tasks_count(self) -> int:
        """今日のタスク件数を取得する

        Returns:
            int: 今日のタスク件数

        Raises:
            TaskServiceGetError: 今日のタスク件数の取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        today_tasks = self.get_today_tasks()
        return len(today_tasks)

    def get_delegated_tasks(self) -> list[TaskRead]:
        """委任済みタスクを取得する

        Returns:
            list[TaskRead]: 委任済みタスクのリスト

        Raises:
            TaskServiceGetError: 委任済みタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.DELEGATED)

    def get_completed_tasks(self) -> list[TaskRead]:
        """完了済みタスクを取得する

        Returns:
            list[TaskRead]: 完了済みタスクのリスト

        Raises:
            TaskServiceGetError: 完了済みタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.COMPLETED)

    def get_cancelled_tasks(self) -> list[TaskRead]:
        """キャンセル済みタスクを取得する

        Returns:
            list[TaskRead]: キャンセル済みタスクのリスト

        Raises:
            TaskServiceGetError: キャンセル済みタスクの取得に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        return self.get_tasks_by_status(TaskStatus.CANCELLED)

    def move_to_inbox(self, task_id: uuid.UUID) -> TaskRead:
        """タスクをインボックスに移動する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.INBOX)
        return self.update_task(task_id, task_data)

    def move_to_next_action(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを次のアクションに移動する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.NEXT_ACTION)
        return self.update_task(task_id, task_data)

    def move_to_waiting_for(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを待機中に移動する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.WAITING_FOR)
        return self.update_task(task_id, task_data)

    def move_to_someday_maybe(self, task_id: uuid.UUID) -> TaskRead:
        """タスクをいつかやるに移動する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.SOMEDAY_MAYBE)
        return self.update_task(task_id, task_data)

    def delegate_task(self, task_id: uuid.UUID) -> TaskRead:
        """タスクを委任する

        Args:
            task_id: タスクのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            TaskServiceCheckError: タスクが存在しない場合
            TaskServiceUpdateError: タスク更新に失敗した場合
            ValidationError: タスクデータの検証に失敗した場合
        """
        task_data = TaskUpdate(status=TaskStatus.DELEGATED)
        return self.update_task(task_id, task_data)
