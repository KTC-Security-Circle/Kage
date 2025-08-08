"""タスク管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.services.quick_action_mapping_service import QuickActionMappingService
from logic.services.task_status_display_service import (
    TaskStatusDisplay,
    TaskStatusDisplayService,
)
from logic.unit_of_work import SqlModelUnitOfWork

if TYPE_CHECKING:
    from datetime import date

    from logic.commands.task_commands import (
        CreateTaskCommand,
        DeleteTaskCommand,
        UpdateTaskCommand,
        UpdateTaskStatusCommand,
    )
    from logic.queries.task_queries import (
        GetAllTasksByStatusDictQuery,
        GetTaskByIdQuery,
        GetTasksByStatusQuery,
        GetTodayTasksCountQuery,
    )
    from logic.unit_of_work import UnitOfWork
    from models import QuickActionCommand, TaskRead, TaskStatus


class TaskApplicationService(BaseApplicationService):
    """タスク管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork) -> None:
        """TaskApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    def create_task(self, command: CreateTaskCommand) -> TaskRead:
        """タスク作成

        Args:
            command: タスク作成コマンド

        Returns:
            作成されたタスク

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"タスク作成開始: {command.title}")

        # バリデーション
        if not command.title.strip():
            msg = "タスクタイトルを入力してください"
            raise ValueError(msg)

        # Unit of Workでトランザクション管理
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            created_task = task_service.create_task(command.to_task_create())
            uow.commit()

            logger.info(f"タスク作成完了: {created_task.title} (ID: {created_task.id})")
            return created_task

    def update_task(self, command: UpdateTaskCommand) -> TaskRead:
        """タスク更新

        Args:
            command: タスク更新コマンド

        Returns:
            更新されたタスク

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 更新エラー
        """
        logger.info(f"タスク更新開始: {command.task_id}")

        # バリデーション
        if not command.title.strip():
            msg = "タスクタイトルを入力してください"
            raise ValueError(msg)

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            updated_task = task_service.update_task(command.task_id, command.to_task_update())
            uow.commit()

            logger.info(f"タスク更新完了: {updated_task.title} (ID: {updated_task.id})")
            return updated_task

    def delete_task(self, command: DeleteTaskCommand) -> None:
        """タスク削除

        Args:
            command: タスク削除コマンド

        Raises:
            RuntimeError: 削除エラー
        """
        logger.info(f"タスク削除開始: {command.task_id}")

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            task_service.delete_task(command.task_id)
            uow.commit()

            logger.info(f"タスク削除完了: {command.task_id}")

    def update_task_status(self, command: UpdateTaskStatusCommand) -> TaskRead:
        """タスクステータス更新

        Args:
            command: タスクステータス更新コマンド

        Returns:
            更新されたタスク

        Raises:
            RuntimeError: 更新エラー
        """
        logger.info(f"タスクステータス更新開始: {command.task_id} -> {command.new_status.value}")

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()

            # 現在のタスクを取得
            task = task_service.get_task_by_id(command.task_id)
            if not task:
                msg = f"タスクが見つかりません: {command.task_id}"
                raise RuntimeError(msg)

            # ステータス更新用のUpdateTaskCommandを作成
            from logic.commands.task_commands import UpdateTaskCommand

            update_command = UpdateTaskCommand(
                task_id=command.task_id,
                title=task.title,
                description=task.description,
                status=command.new_status,
                due_date=task.due_date,
            )

            updated_task = task_service.update_task(command.task_id, update_command.to_task_update())
            uow.commit()

            logger.info(f"タスクステータス更新完了: {updated_task.title} (ID: {updated_task.id})")
            return updated_task

    def get_tasks_by_status(self, query: GetTasksByStatusQuery) -> list[TaskRead]:
        """ステータス別タスク取得

        Args:
            query: ステータス別タスク取得クエリ

        Returns:
            タスクリスト
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_tasks_by_status(query.status)

    def get_today_tasks_count(self, query: GetTodayTasksCountQuery) -> int:
        """今日のタスク件数取得

        Args:
            query: 今日のタスク件数取得クエリ

        Returns:
            今日のタスク件数
        """
        _ = query  # 将来の拡張用パラメータ
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_today_tasks_count()

    def get_task_by_id(self, query: GetTaskByIdQuery) -> TaskRead | None:
        """ID指定タスク取得

        Args:
            query: ID指定タスク取得クエリ

        Returns:
            タスク（見つからない場合はNone）
        """
        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()
            return task_service.get_task_by_id(query.task_id)

    def get_all_tasks_by_status_dict(self, query: GetAllTasksByStatusDictQuery) -> dict[TaskStatus, list[TaskRead]]:
        """全ステータスのタスクを辞書形式で取得

        Args:
            query: 全ステータス別タスク取得クエリ

        Returns:
            ステータス別タスク辞書
        """
        _ = query  # 将来の拡張用パラメータ
        from models import TaskStatus

        result = {}

        with self._unit_of_work_factory() as uow:
            task_service = uow.service_factory.create_task_service()

            for status in TaskStatus:
                result[status] = task_service.get_tasks_by_status(status)

            return result

    # [AI GENERATED] QuickAction関連のメソッド

    def get_task_status_for_quick_action(self, action: QuickActionCommand) -> TaskStatus:
        """QuickActionCommandに対応するTaskStatusを取得

        Args:
            action: クイックアクションコマンド

        Returns:
            対応するTaskStatus

        Raises:
            ValueError: 未対応のアクションが指定された場合
        """
        logger.info(f"クイックアクション→ステータス変換: {action}")
        return QuickActionMappingService.map_quick_action_to_task_status(action)

    def get_available_quick_actions(self) -> list[QuickActionCommand]:
        """利用可能なクイックアクションのリストを取得

        Returns:
            利用可能なQuickActionCommandのリスト
        """
        return QuickActionMappingService.get_available_quick_actions()

    def get_quick_action_description(self, action: QuickActionCommand) -> str:
        """クイックアクションの説明を取得

        Args:
            action: クイックアクションコマンド

        Returns:
            アクションの説明文

        Raises:
            ValueError: 未対応のアクションが指定された場合
        """
        return QuickActionMappingService.get_quick_action_description(action)

    # [AI GENERATED] タスクステータス表示関連のメソッド

    def get_task_status_display(self, status: TaskStatus) -> TaskStatusDisplay:
        """タスクステータスの表示情報を取得

        Args:
            status: タスクステータス

        Returns:
            TaskStatusDisplay: 表示情報

        Raises:
            ValueError: 未対応のステータスが指定された場合
        """
        return TaskStatusDisplayService.get_task_status_display(status)

    def get_board_column_mapping(self) -> dict[str, list[TaskStatus]]:
        """タスクボードのカラムマッピングを取得

        Returns:
            カラム名とタスクステータスリストのマッピング
        """
        return TaskStatusDisplayService.get_board_column_mapping()

    def get_board_section_display(self, section_name: str, status: TaskStatus) -> str:
        """ボードセクションの表示ラベルを取得

        Args:
            section_name: セクション名（"CLOSED" または "INBOX"）
            status: タスクステータス

        Returns:
            表示ラベル

        Raises:
            ValueError: 未対応の組み合わせが指定された場合
        """
        return TaskStatusDisplayService.get_board_section_display(section_name, status)

    def get_all_status_displays(self) -> list[TaskStatusDisplay]:
        """全てのタスクステータスの表示情報を取得

        Returns:
            全タスクステータスの表示情報リスト
        """
        return TaskStatusDisplayService.get_all_status_displays()

    # [AI GENERATED] QuickAction経由でのタスク作成便利メソッド

    def create_task_from_quick_action(
        self,
        action: QuickActionCommand,
        title: str,
        description: str = "",
        due_date: date | None = None,
    ) -> TaskRead:
        """QuickActionからタスクを作成

        QuickActionCommandを基にTaskStatusを決定してタスクを作成する便利メソッド。
        View層からの呼び出しを簡素化します。

        Args:
            action: クイックアクションコマンド
            title: タスクタイトル
            description: タスク説明（オプション）
            due_date: 締切日（オプション）

        Returns:
            作成されたタスク

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: 作成エラー
        """
        logger.info(f"QuickAction経由でタスク作成: {action} - {title}")

        # [AI GENERATED] QuickActionに対応するステータスを取得
        task_status = self.get_task_status_for_quick_action(action)

        # [AI GENERATED] 既存のCreateTaskCommandを使用してタスク作成
        from logic.commands.task_commands import CreateTaskCommand

        command = CreateTaskCommand(
            title=title,
            description=description,
            status=task_status,
            due_date=due_date,
        )

        return self.create_task(command)
