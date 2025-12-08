"""タスクサービスの実装

このモジュールは、タスクに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なタスク操作を実装します。
"""

import uuid

from loguru import logger

from errors import NotFoundError
from logic.repositories import RepositoryFactory, TaskRepository
from logic.services.base import MyBaseError, ServiceBase, convert_read_model, handle_service_errors
from models import Task, TaskCreate, TaskRead, TaskStatus, TaskUpdate

SERVICE_NAME = "タスクサービス"


class TaskServiceError(MyBaseError):
    """タスクサービス層で発生する汎用的なエラー"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:
        super().__init__(f"タスクの{operation}処理でエラーが発生しました: {message}")
        self.operation = operation


class TaskService(ServiceBase):
    """タスクサービス

    タスクに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なタスク操作を実装します。
    """

    def __init__(self, task_repo: TaskRepository) -> None:
        """TaskServiceを初期化する

        Args:
            task_repo: タスクリポジトリ
        """
        self.task_repo = task_repo

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> "TaskService":
        """TaskServiceのインスタンスを生成するファクトリメソッド

        Returns:
            TaskService: タスクサービスのインスタンス
        """
        return cls(task_repo=repo_factory.create(TaskRepository))

    @handle_service_errors(SERVICE_NAME, "作成", TaskServiceError)
    @convert_read_model(TaskRead)
    def create(self, create_data: TaskCreate) -> Task:
        """新しいタスクを作成する

        Args:
            create_data: 作成するタスクのデータ

        Returns:
            TaskRead: 作成されたタスク

        Raises:
            NotFoundError: エンティティが存在しない場合
            TaskServiceError: タスク作成に失敗した場合
        """
        task = self.task_repo.create(create_data)
        logger.debug(f"タスク '{task.title}' を作成しました (ID: {task.id})")
        return task

    @handle_service_errors(SERVICE_NAME, "更新", TaskServiceError)
    @convert_read_model(TaskRead)
    def update(self, task_id: uuid.UUID, update_data: TaskUpdate) -> Task:
        """タスクを更新する

        Args:
            task_id: 更新するタスクのID
            update_data: 更新データ

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            NotFoundError: タスクが存在しない場合
            TaskServiceError: タスク更新に失敗した場合
        """
        task = self.task_repo.update(task_id, update_data)
        logger.debug(f"タスクを更新しました: {task.id}")

        return task

    @handle_service_errors(SERVICE_NAME, "削除", TaskServiceError)
    def delete(self, task_id: uuid.UUID, *, force: bool = False) -> bool:
        """タスクを削除する

        Args:
            task_id: 削除するタスクのID
            force: 強制削除フラグ。Trueの場合、関連するタグやプロジェクトからもタスクを削除する

        Returns:
            bool: タスクが正常に削除された場合にTrueを返す

        Raises:
            NotFoundError: タスクが存在しない場合
            TaskServiceError: タスクが関連している場合、または削除に失敗した場合
        """
        existing_task = self.task_repo.get_by_id(task_id)

        if not force:
            self.task_repo.remove_all_tags(task_id)
            self.task_repo.delete(task_id)
            success = True
        else:
            self.delete(task_id, force=True)
            success = True

        logger.debug(f"タスク '{existing_task.title}' を削除しました (ID: {task_id})")
        return success

    @handle_service_errors(SERVICE_NAME, "タグ削除", TaskServiceError)
    @convert_read_model(TaskRead)
    def remove_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task:
        """タスクからタグを削除する

        Args:
            task_id: タスクのID
            tag_id: 削除するタグのID

        Returns:
            TaskRead: 更新されたタスク

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        task = self.task_repo.get_by_id(task_id, with_details=True)

        for tag in task.tags:
            if tag.id == tag_id:
                updated_task = self.task_repo.remove_tag(task_id, tag_id)
                logger.debug(f"タスク({task_id})からタグ({tag_id})を削除しました。")
                break
        else:
            msg = f"タスク({task_id})にタグ({tag_id})は存在しません。"
            logger.debug(msg)
            raise NotFoundError(msg)

        return updated_task

    @handle_service_errors(SERVICE_NAME, "取得", TaskServiceError)
    @convert_read_model(TaskRead)
    def get_by_id(self, task_id: uuid.UUID, *, with_details: bool = False) -> Task:
        """IDでタスクを取得する

        Args:
            task_id: タスクのID
            with_details: 関連するタグやプロジェクト情報も含めるかどうか

        Returns:
            TaskRead: 見つかったタスク

        Raises:
            NotFoundError: タスクが存在しない場合
            TaskServiceError: タスクの取得に失敗した場合
        """
        task = self.task_repo.get_by_id(task_id, with_details=with_details)
        logger.debug(f"タスクを取得しました: {task.id}")
        return task

    @handle_service_errors(SERVICE_NAME, "取得", TaskServiceError)
    @convert_read_model(TaskRead, is_list=True)
    def get_all(self) -> list[Task]:
        """全てのタスクを取得する

        Returns:
            list[TaskRead]: 全てのタスクのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            TaskServiceError: 全タスクの取得に失敗した場合
        """
        tasks = self.task_repo.get_all()
        logger.debug(f"全てのタスクを取得しました: {len(tasks)} 件")
        return tasks

    @handle_service_errors(SERVICE_NAME, "ステータス取得", TaskServiceError)
    @convert_read_model(TaskRead, is_list=True)
    def list_by_status(self, status: TaskStatus, *, with_details: bool = False) -> list[Task]:
        """ステータスでタスクを取得する

        Args:
            status: 取得するタスクのステータス
            with_details: 関連するタグやプロジェクト情報も含めるかどうか

        Returns:
            list[TaskRead]: 指定されたステータスのタスクのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            TaskServiceError: タスクの取得に失敗した場合
        """
        tasks = self.task_repo.list_by_status(status, with_details=with_details)
        logger.debug(f"ステータス '{status}' のタスクを取得しました: {len(tasks)} 件")
        return tasks

    @handle_service_errors(SERVICE_NAME, "タグ取得", TaskServiceError)
    @convert_read_model(TaskRead, is_list=True)
    def list_by_tag(self, tag_id: uuid.UUID, *, with_details: bool = False) -> list[Task]:
        """タグIDでタスクを取得する。

        Args:
            tag_id: 取得対象のタグID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[TaskRead]: タグにひも付くタスク一覧
        """
        try:
            tasks = self.task_repo.list_by_tag(tag_id, with_details=with_details)
        except NotFoundError:
            tasks = []
        logger.debug(f"タグ({tag_id})に紐づくタスクを {len(tasks)} 件取得しました。")
        return tasks

    @handle_service_errors(SERVICE_NAME, "検索", TaskServiceError)
    @convert_read_model(TaskRead, is_list=True)
    def search_tasks(self, query: str, *, with_details: bool = False) -> list[Task]:
        """クエリでタスクを検索する

        タイトルと説明の双方を部分一致・大文字小文字無視で検索し、重複を除去して返す。

        Args:
            query: 検索クエリ
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[TaskRead]: 検索結果のタスク一覧
        """
        # タイトルと説明の両方を検索し、IDで重複排除
        try:
            by_title = self.task_repo.search_by_title(query, with_details=with_details)
        except NotFoundError:
            by_title = []
        try:
            by_desc = self.task_repo.search_by_description(query, with_details=with_details)
        except NotFoundError:
            by_desc = []
        merged: dict[uuid.UUID, Task] = {}
        for t in by_title + by_desc:
            if t.id is not None:
                merged[t.id] = t
        results = list(merged.values())
        logger.debug(f"クエリ '{query}' に一致するタスクを {len(results)} 件取得しました。")
        return results
