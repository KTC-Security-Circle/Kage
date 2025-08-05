"""TaskServiceのテストケース

このモジュールは、TaskServiceクラスのビジネスロジックを
テストするためのテストケースを提供します。

テスト対象：
- create_task: タスク作成のビジネスロジック
- update_task: タスク更新のビジネスロジック
- delete_task: タスク削除のビジネスロジック
- get_task_by_id: タスク取得のビジネスロジック
- complete_task: タスク完了処理
- プロジェクト存在チェック等のビジネスルール
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.services.task_service import (
    TaskService,
    TaskServiceCheckError,
    TaskServiceCreateError,
    TaskServiceGetError,
)
from models import Task, TaskCreate, TaskRead, TaskStatus, TaskUpdate

# テスト用定数
EXPECTED_TASK_COUNT = 2


class TestTaskService:
    """TaskServiceのビジネスロジックをテストするクラス"""

    @pytest.fixture
    def mock_repositories(self) -> dict[str, Mock]:
        """モックのRepositoryを作成"""
        return {
            "task_repo": Mock(),
            "project_repo": Mock(),
            "tag_repo": Mock(),
            "task_tag_repo": Mock(),
        }

    @pytest.fixture
    def task_service(self, mock_repositories: dict[str, Mock]) -> TaskService:
        """TaskServiceのインスタンスを作成"""
        return TaskService(
            task_repo=mock_repositories["task_repo"],
            project_repo=mock_repositories["project_repo"],
            tag_repo=mock_repositories["tag_repo"],
            task_tag_repo=mock_repositories["task_tag_repo"],
        )

    def test_create_task_success(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: タスクの作成成功"""
        # モックの設定
        task_create = TaskCreate(title="新しいタスク", description="テストタスク")
        created_task = Task(
            id=uuid.uuid4(),
            title="新しいタスク",
            description="テストタスク",
            status=TaskStatus.INBOX,
        )
        mock_repositories["task_repo"].create.return_value = created_task

        # 実行
        result = task_service.create_task(task_create)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == "新しいタスク"
        mock_repositories["task_repo"].create.assert_called_once()

    def test_create_task_with_project_success(
        self, task_service: TaskService, mock_repositories: dict[str, Mock]
    ) -> None:
        """正常系: プロジェクト付きタスクの作成成功"""
        # モックの設定
        project_id = uuid.uuid4()
        task_create = TaskCreate(
            title="プロジェクトタスク",
            description="プロジェクト関連タスク",
            project_id=project_id,
        )

        # プロジェクトが存在することをモック
        mock_project = Mock()
        mock_repositories["project_repo"].get_by_id.return_value = mock_project

        created_task = Task(
            id=uuid.uuid4(),
            title="プロジェクトタスク",
            description="プロジェクト関連タスク",
            status=TaskStatus.INBOX,
            project_id=project_id,
        )
        mock_repositories["task_repo"].create.return_value = created_task

        # 実行
        result = task_service.create_task(task_create)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == "プロジェクトタスク"
        assert result.project_id == project_id
        mock_repositories["project_repo"].get_by_id.assert_called_once_with(project_id)
        mock_repositories["task_repo"].create.assert_called_once()

    def test_create_task_with_invalid_project(
        self, task_service: TaskService, mock_repositories: dict[str, Mock]
    ) -> None:
        """異常系: 存在しないプロジェクトIDでのタスク作成"""
        # モックの設定
        project_id = uuid.uuid4()
        task_create = TaskCreate(
            title="無効プロジェクトタスク",
            project_id=project_id,
        )

        # プロジェクトが存在しないことをモック
        mock_repositories["project_repo"].get_by_id.return_value = None

        # 実行と検証
        with pytest.raises(TaskServiceCreateError, match="プロジェクチ.*が見つかりません"):
            task_service.create_task(task_create)

        mock_repositories["project_repo"].get_by_id.assert_called_once_with(project_id)
        mock_repositories["task_repo"].create.assert_not_called()

    def test_update_task_success(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: タスクの更新成功"""
        # モックの設定
        task_id = uuid.uuid4()
        task_update = TaskUpdate(title="更新されたタスク", description="更新後の説明")

        existing_task = Task(
            id=task_id,
            title="元のタスク",
            description="元の説明",
            status=TaskStatus.INBOX,
        )
        updated_task = Task(
            id=task_id,
            title="更新されたタスク",
            description="更新後の説明",
            status=TaskStatus.INBOX,
        )

        mock_repositories["task_repo"].get_by_id.return_value = existing_task
        mock_repositories["task_repo"].update.return_value = updated_task

        # 実行
        result = task_service.update_task(task_id, task_update)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == "更新されたタスク"
        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)
        mock_repositories["task_repo"].update.assert_called_once()

    def test_update_task_not_found(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """異常系: 存在しないタスクの更新"""
        # モックの設定
        task_id = uuid.uuid4()
        task_update = TaskUpdate(title="更新されたタスク")

        mock_repositories["task_repo"].get_by_id.return_value = None

        # 実行と検証
        with pytest.raises(TaskServiceCheckError, match="タスクID .* が見つかりません"):
            task_service.update_task(task_id, task_update)

        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)
        mock_repositories["task_repo"].update.assert_not_called()

    def test_delete_task_success(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: タスクの削除成功"""
        # モックの設定
        task_id = uuid.uuid4()
        existing_task = Task(
            id=task_id,
            title="削除対象タスク",
            description="削除テスト",
            status=TaskStatus.INBOX,
        )

        mock_repositories["task_repo"].get_by_id.return_value = existing_task
        mock_repositories["task_repo"].delete.return_value = True
        # タスクタグの削除に関するモック設定
        mock_repositories["task_tag_repo"].get_by_task_id.return_value = []

        # 実行
        result = task_service.delete_task(task_id)

        # 検証
        assert result is True
        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)
        mock_repositories["task_repo"].delete.assert_called_once_with(task_id)

    def test_delete_task_not_found(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """異常系: 存在しないタスクの削除"""
        # モックの設定
        task_id = uuid.uuid4()
        mock_repositories["task_repo"].get_by_id.return_value = None

        # 実行と検証
        with pytest.raises(TaskServiceCheckError, match="タスクID .* が見つかりません"):
            task_service.delete_task(task_id)

        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)
        mock_repositories["task_repo"].delete.assert_not_called()

    def test_get_task_by_id_success(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: タスクの取得成功"""
        # モックの設定
        task_id = uuid.uuid4()
        task = Task(
            id=task_id,
            title="取得対象タスク",
            description="取得テスト",
            status=TaskStatus.NEXT_ACTION,
        )

        mock_repositories["task_repo"].get_by_id.return_value = task

        # 実行
        result = task_service.get_task_by_id(task_id)

        # 検証
        assert result is not None
        assert isinstance(result, TaskRead)
        assert result.title == "取得対象タスク"
        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)

    def test_get_task_by_id_not_found(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """異常系: 存在しないタスクの取得でエラー"""
        # モックの設定
        task_id = uuid.uuid4()
        mock_repositories["task_repo"].get_by_id.return_value = None

        # 実行と検証
        with pytest.raises(TaskServiceGetError, match="タスクの取得に失敗しました"):
            task_service.get_task_by_id(task_id)

        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)

    def test_complete_task_success(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: タスクの完了処理成功"""
        # モックの設定
        task_id = uuid.uuid4()
        existing_task = Task(
            id=task_id,
            title="完了対象タスク",
            description="完了テスト",
            status=TaskStatus.NEXT_ACTION,
        )
        completed_task = Task(
            id=task_id,
            title="完了対象タスク",
            description="完了テスト",
            status=TaskStatus.COMPLETED,
        )

        mock_repositories["task_repo"].get_by_id.return_value = existing_task
        mock_repositories["task_repo"].update.return_value = completed_task

        # 実行
        result = task_service.complete_task(task_id)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.status == TaskStatus.COMPLETED
        mock_repositories["task_repo"].get_by_id.assert_called_once_with(task_id)
        mock_repositories["task_repo"].update.assert_called_once()

    def test_get_tasks_by_status(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: ステータス別タスク取得"""
        # モックの設定
        tasks = [
            Task(
                id=uuid.uuid4(),
                title="タスク1",
                description="説明1",
                status=TaskStatus.NEXT_ACTION,
            ),
            Task(
                id=uuid.uuid4(),
                title="タスク2",
                description="説明2",
                status=TaskStatus.NEXT_ACTION,
            ),
        ]

        mock_repositories["task_repo"].get_by_status.return_value = tasks

        # 実行
        result = task_service.get_tasks_by_status(TaskStatus.NEXT_ACTION)

        # 検証
        assert len(result) == EXPECTED_TASK_COUNT
        assert all(isinstance(task, TaskRead) for task in result)
        assert all(task.status == TaskStatus.NEXT_ACTION for task in result)
        mock_repositories["task_repo"].get_by_status.assert_called_once_with(TaskStatus.NEXT_ACTION)

    def test_get_inbox_tasks(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: INBOXタスクの取得"""
        # モックの設定
        inbox_tasks = [
            Task(
                id=uuid.uuid4(),
                title="INBOX タスク1",
                description="INBOX 説明1",
                status=TaskStatus.INBOX,
            ),
            Task(
                id=uuid.uuid4(),
                title="INBOX タスク2",
                description="INBOX 説明2",
                status=TaskStatus.INBOX,
            ),
        ]

        # get_inbox_tasksの内部でget_by_statusが呼ばれるのでそちらをモック
        mock_repositories["task_repo"].get_by_status.return_value = inbox_tasks

        # 実行
        result = task_service.get_inbox_tasks()

        # 検証
        assert len(result) == EXPECTED_TASK_COUNT
        assert all(isinstance(task, TaskRead) for task in result)
        assert all(task.status == TaskStatus.INBOX for task in result)
        mock_repositories["task_repo"].get_by_status.assert_called_once_with(TaskStatus.INBOX)

    def test_get_next_action_tasks(self, task_service: TaskService, mock_repositories: dict[str, Mock]) -> None:
        """正常系: 次のアクションタスクの取得"""
        # モックの設定
        next_action_tasks = [
            Task(
                id=uuid.uuid4(),
                title="次のアクション1",
                description="説明1",
                status=TaskStatus.NEXT_ACTION,
            ),
            Task(
                id=uuid.uuid4(),
                title="次のアクション2",
                description="説明2",
                status=TaskStatus.NEXT_ACTION,
            ),
        ]

        # get_next_action_tasksの内部でget_by_statusが呼ばれるのでそちらをモック
        mock_repositories["task_repo"].get_by_status.return_value = next_action_tasks

        # 実行
        result = task_service.get_next_action_tasks()

        # 検証
        assert len(result) == EXPECTED_TASK_COUNT
        assert all(isinstance(task, TaskRead) for task in result)
        assert all(task.status == TaskStatus.NEXT_ACTION for task in result)
        mock_repositories["task_repo"].get_by_status.assert_called_once_with(TaskStatus.NEXT_ACTION)
