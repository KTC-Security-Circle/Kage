"""TaskApplicationServiceのテストケース

このモジュールは、TaskApplicationServiceクラスの
Application Service層の機能をテストするためのテストケースを提供します。

テスト対象：
- create_task: タスク作成のApplication Service層ロジック
- update_task: タスク更新のApplication Service層ロジック
- delete_task: タスク削除のApplication Service層ロジック
- update_task_status: タスクステータス更新の処理
- get_tasks_by_status: ステータス別タスク取得
- get_today_tasks_count: 今日のタスク件数取得
- get_task_by_id: ID指定タスク取得
- get_all_tasks_by_status_dict: 全ステータス別タスク取得
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from logic.application.task_application_service import TaskApplicationService
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
from models import TaskRead, TaskStatus

# テスト用定数
EXPECTED_TODAY_TASKS_COUNT = 5


class TestTaskApplicationService:
    """TaskApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_task_service = Mock()

        # [AI GENERATED] モックの階層構造を設定
        mock_uow.service_factory = mock_service_factory
        mock_service_factory.get_service.return_value = mock_task_service

        # [AI GENERATED] コンテキストマネージャとして機能させる
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def task_application_service(self, mock_unit_of_work_factory: Mock) -> TaskApplicationService:
        """TaskApplicationServiceのインスタンスを作成"""
        return TaskApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_task_read(self) -> TaskRead:
        """テスト用のTaskReadデータを作成"""
        return TaskRead(
            id=uuid.uuid4(),
            title="サンプルタスク",
            description="テスト用のタスク",
            status=TaskStatus.INBOX,
            due_date=datetime.now(tz=UTC).date() + timedelta(days=1),
        )

    def test_create_task_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: タスク作成成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.create_task.return_value = sample_task_read

        # コマンド作成
        command = CreateTaskCommand(
            title="新しいタスク",
            description="テスト用タスク",
            status=TaskStatus.INBOX,
        )

        # 実行
        result = task_application_service.create_task(command)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == sample_task_read.title
        mock_task_service.create_task.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_create_task_validation_error(self, task_application_service: TaskApplicationService) -> None:
        """異常系: タスク作成時のバリデーションエラー"""
        # 空のタイトルでコマンド作成
        command = CreateTaskCommand(title="", description="テスト用タスク")

        # 実行と検証
        with pytest.raises(ValueError, match="タスクタイトルを入力してください"):
            task_application_service.create_task(command)

    def test_update_task_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: タスク更新成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        updated_task = TaskRead(
            id=sample_task_read.id,
            title="更新されたタスク",
            description=sample_task_read.description,
            status=sample_task_read.status,
            due_date=sample_task_read.due_date,
        )
        mock_task_service.update_task.return_value = updated_task

        # コマンド作成
        command = UpdateTaskCommand(
            task_id=sample_task_read.id,
            title="更新されたタスク",
            description=sample_task_read.description,
            status=sample_task_read.status,
        )

        # 実行
        result = task_application_service.update_task(command)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == "更新されたタスク"
        mock_task_service.update_task.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_update_task_validation_error(self, task_application_service: TaskApplicationService) -> None:
        """異常系: タスク更新時のバリデーションエラー"""
        # 空のタイトルでコマンド作成
        command = UpdateTaskCommand(
            task_id=uuid.uuid4(),
            title="",  # 空のタイトル
            description="テスト用タスク",
        )

        # 実行と検証
        with pytest.raises(ValueError, match="タスクタイトルを入力してください"):
            task_application_service.update_task(command)

    def test_delete_task_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: タスク削除成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        task_id = uuid.uuid4()

        # コマンド作成
        command = DeleteTaskCommand(task_id=task_id)

        # 実行
        task_application_service.delete_task(command)

        # 検証
        mock_task_service.delete_task.assert_called_once_with(task_id)
        mock_unit_of_work.commit.assert_called_once()

    def test_update_task_status_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: タスクステータス更新成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_task_by_id.return_value = sample_task_read

        updated_task = TaskRead(
            id=sample_task_read.id,
            title=sample_task_read.title,
            description=sample_task_read.description,
            status=TaskStatus.NEXT_ACTION,  # ステータス変更
            due_date=sample_task_read.due_date,
        )
        mock_task_service.update_task.return_value = updated_task

        # コマンド作成
        command = UpdateTaskStatusCommand(
            task_id=sample_task_read.id,
            new_status=TaskStatus.NEXT_ACTION,
        )

        # 実行
        result = task_application_service.update_task_status(command)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.status == TaskStatus.NEXT_ACTION
        mock_task_service.get_task_by_id.assert_called_once_with(sample_task_read.id)
        mock_task_service.update_task.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_update_task_status_task_not_found(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: タスクステータス更新時にタスクが見つからない"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_task_by_id.return_value = None  # タスクが見つからない

        task_id = uuid.uuid4()
        command = UpdateTaskStatusCommand(
            task_id=task_id,
            new_status=TaskStatus.NEXT_ACTION,
        )

        # 実行と検証
        with pytest.raises(RuntimeError, match=f"タスクが見つかりません: {task_id}"):
            task_application_service.update_task_status(command)

    def test_get_tasks_by_status(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: ステータス別タスク取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_tasks_by_status.return_value = [sample_task_read]

        # クエリ作成
        query = GetTasksByStatusQuery(status=TaskStatus.INBOX)

        # 実行
        result = task_application_service.get_tasks_by_status(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_task_read
        mock_task_service.get_tasks_by_status.assert_called_once_with(TaskStatus.INBOX)

    def test_get_today_tasks_count(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: 今日のタスク件数取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_today_tasks_count.return_value = EXPECTED_TODAY_TASKS_COUNT

        # クエリ作成
        query = GetTodayTasksCountQuery()

        # 実行
        result = task_application_service.get_today_tasks_count(query)

        # 検証
        assert result == EXPECTED_TODAY_TASKS_COUNT
        mock_task_service.get_today_tasks_count.assert_called_once()

    def test_get_task_by_id(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: ID指定タスク取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_task_by_id.return_value = sample_task_read

        # クエリ作成
        query = GetTaskByIdQuery(task_id=sample_task_read.id)

        # 実行
        result = task_application_service.get_task_by_id(query)

        # 検証
        assert result == sample_task_read
        mock_task_service.get_task_by_id.assert_called_once_with(sample_task_read.id)

    def test_get_task_by_id_not_found(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: ID指定タスク取得でタスクが見つからない場合"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_task_by_id.return_value = None

        task_id = uuid.uuid4()
        query = GetTaskByIdQuery(task_id=task_id)

        # 実行
        result = task_application_service.get_task_by_id(query)

        # 検証
        assert result is None
        mock_task_service.get_task_by_id.assert_called_once_with(task_id)

    def test_get_all_tasks_by_status_dict(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: 全ステータス別タスク取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value

        # [AI GENERATED] 各ステータスでの戻り値設定
        def mock_get_tasks_by_status(status: TaskStatus) -> list[TaskRead]:
            if status == TaskStatus.INBOX:
                return [sample_task_read]
            return []

        mock_task_service.get_tasks_by_status.side_effect = mock_get_tasks_by_status

        # クエリ作成
        query = GetAllTasksByStatusDictQuery()

        # 実行
        result = task_application_service.get_all_tasks_by_status_dict(query)

        # 検証
        assert isinstance(result, dict)
        assert TaskStatus.INBOX in result
        assert TaskStatus.NEXT_ACTION in result
        assert TaskStatus.COMPLETED in result
        assert len(result[TaskStatus.INBOX]) == 1
        assert result[TaskStatus.INBOX][0] == sample_task_read
        assert len(result[TaskStatus.NEXT_ACTION]) == 0
        assert len(result[TaskStatus.COMPLETED]) == 0

        # [AI GENERATED] 全ステータスでget_tasks_by_statusが呼ばれることを確認
        expected_calls = len(TaskStatus)
        assert mock_task_service.get_tasks_by_status.call_count == expected_calls
