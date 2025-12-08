"""タスク管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from loguru import logger

from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.task_service import TaskService
from logic.unit_of_work import SqlModelUnitOfWork
from models import TaskCreate, TaskRead, TaskStatus, TaskUpdate

if TYPE_CHECKING:
    import uuid
    from datetime import date, datetime


class TaskApplicationError(ApplicationError):
    """タスク管理のApplication Serviceで発生するエラー"""


class TaskContentValidationError(ValidationError, TaskApplicationError):
    """タスク内容のバリデーションエラー"""


class TaskApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """タスク管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        """TaskApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> TaskApplicationService:
        instance = super().get_instance(*args, **kwargs)
        return cast("TaskApplicationService", instance)

    def create(  # noqa: PLR0913
        self,
        title: str,
        description: str | None = None,
        *,
        status: TaskStatus | None = None,
        project_id: uuid.UUID | None = None,
        memo_id: uuid.UUID | None = None,
        due_date: date | None = None,
        completed_at: datetime | None = None,
        is_recurring: bool | None = None,
        recurrence_rule: str | None = None,
    ) -> TaskRead:
        """タスクを作成する

        Args:
            title: タスクタイトル
            description: 詳細説明
            status: 初期ステータス（未指定時はモデル既定）
            project_id: 紐づけるプロジェクトID
            memo_id: 生成元メモのID
            due_date: 期限日
            completed_at: 完了日時
            is_recurring: 繰り返しタスクかどうか
            recurrence_rule: 繰り返しルール

        Returns:
            TaskRead: 作成されたタスク

        Raises:
            TaskContentValidationError: タイトルが空の場合
        """
        if not title.strip():
            msg = "タスクタイトルを入力してください"
            raise TaskContentValidationError(msg)

        create_model = TaskCreate(
            title=title,
            description=description,
            status=status or TaskStatus.TODO,
            project_id=project_id,
            memo_id=memo_id,
            due_date=due_date,
            completed_at=completed_at,
            is_recurring=is_recurring if is_recurring is not None else False,
            recurrence_rule=recurrence_rule,
        )

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            created = task_service.create(create_model)

        logger.info(f"タスク作成完了 - (ID={created.id})")
        return created

    def update(self, task_id: uuid.UUID, update_data: TaskUpdate) -> TaskRead:
        """タスクを更新する

        Args:
            task_id: 更新対象タスクのID
            update_data: タスク更新データ

        Returns:
            TaskRead: 更新後タスク
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            updated = task_service.update(task_id, update_data)

        logger.info(f"タスク更新完了 - (ID={updated.id})")
        return updated

    def delete(self, task_id: uuid.UUID) -> bool:
        """タスク削除

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除成功フラグ
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            success = task_service.delete(task_id)
            logger.info(f"タスク削除完了: ID {task_id}, 結果: {success}")
            return success

    # 取得系
    def get_by_id(self, task_id: uuid.UUID, *, with_details: bool = False) -> TaskRead | None:
        """IDでタスク取得

        Args:
            task_id: タスクのID
            with_details: 関連エンティティも取得するか

        Returns:
            TaskRead | None: 見つかったタスク（存在しない場合None想定の呼び出し元もある）
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.get_by_id(task_id, with_details=with_details)

    def get_all_tasks(self) -> list[TaskRead]:
        """全タスク取得"""
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.get_all()

    def list_by_status(self, status: TaskStatus, *, with_details: bool = False) -> list[TaskRead]:
        """ステータスでタスク取得"""
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.list_by_status(status, with_details=with_details)

    def list_by_tag(self, tag_id: uuid.UUID, *, with_details: bool = False) -> list[TaskRead]:
        """タグIDでタスク一覧を取得する。"""
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)
            return task_service.list_by_tag(tag_id, with_details=with_details)

    def search(
        self,
        query: str,
        *,
        with_details: bool = False,
        status: TaskStatus | None = None,
        tags: list[uuid.UUID] | None = None,
    ) -> list[TaskRead]:
        """タスク検索

        タイトル・説明を横断検索し、必要に応じてステータスやタグで絞り込む。

        Args:
            query: 検索クエリ（空文字・空白のみなら全件取得してフィルタ適用）
            with_details: 関連情報を含めるかどうか
            status: ステータスでの追加フィルタ
            tags: タグIDのリスト（いずれかを含むOR条件）

        Returns:
            list[TaskRead]: 検索結果
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.get_service(TaskService)

            # 空クエリの場合は全件取得、それ以外は検索
            if not query or not query.strip():
                results = task_service.get_all()
            else:
                results = task_service.search_tasks(query, with_details=with_details)

            # ステータスフィルタ
            if status is not None:
                status_items = task_service.list_by_status(status, with_details=with_details)
                status_ids = {t.id for t in status_items}
                results = [t for t in results if t.id in status_ids]

            # タグフィルタ（OR条件）
            if tags:
                # RepositoryのJOINを活用（直接TaskRepositoryを生成）
                from logic.repositories import TaskRepository as _TaskRepo

                task_repo = uow.repository_factory.create(_TaskRepo)
                matched_ids: set[uuid.UUID] = set()
                for tag_id in tags:
                    try:
                        for t in task_repo.list_by_tag(tag_id, with_details=with_details):
                            if t.id is not None:
                                matched_ids.add(t.id)
                    except Exception as exc:
                        # タグが存在しない場合などは単にスキップ
                        logger.debug(f"タグフィルタ処理中に例外: {exc}")
                        continue
                results = [t for t in results if t.id in matched_ids]

            return results
