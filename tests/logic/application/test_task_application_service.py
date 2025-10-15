"""TaskApplicationService のテスト（現行API）

Unit of Work のモックを用い、TaskApplicationService の公開APIを検証する。
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from logic.application.task_application_service import TaskApplicationService, TaskContentValidationError
from models import TaskRead, TaskStatus, TaskUpdate

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
            status=TaskStatus.TODO,
            due_date=datetime.now(tz=UTC).date() + timedelta(days=1),
        )

    def test_create_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: タスク作成成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.create.return_value = sample_task_read

        # 実行
        result = task_application_service.create(
            title="新しいタスク", description="テスト用タスク", status=TaskStatus.TODO
        )

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == sample_task_read.title
        mock_task_service.create.assert_called_once()

    def test_create_validation_error(self, task_application_service: TaskApplicationService) -> None:
        """異常系: タスク作成時のバリデーションエラー"""
        with pytest.raises(TaskContentValidationError, match="タスクタイトルを入力してください"):
            task_application_service.create(title="", description="テスト用タスク")

    def test_update_success(
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
        mock_task_service.update.return_value = updated_task

        update = TaskUpdate(title="更新されたタスク", description=sample_task_read.description)

        # 実行
        result = task_application_service.update(sample_task_read.id, update)

        # 検証
        assert isinstance(result, TaskRead)
        assert result.title == "更新されたタスク"
        mock_task_service.update.assert_called_once()

    # update のバリデーションは Application 層ではタイトル空チェックを行わないため対象外

    def test_delete_success(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: タスク削除成功"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        task_id = uuid.uuid4()
        # 実行
        task_application_service.delete(task_id)

        # 検証
        mock_task_service.delete.assert_called_once_with(task_id)

    # ステータス更新の個別APIは現行Application層に存在しないため対象外

    # ステータス更新NotFoundは対象外

    def test_list_by_status(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: ステータス別タスク取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.list_by_status.return_value = [sample_task_read]

        # 実行
        result = task_application_service.list_by_status(TaskStatus.TODO)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_task_read
        mock_task_service.list_by_status.assert_called_once_with(TaskStatus.TODO, with_details=False)

    # Today 件数APIは現行仕様に存在しないため対象外

    def test_get_by_id(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
        sample_task_read: TaskRead,
    ) -> None:
        """正常系: ID指定タスク取得"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_by_id.return_value = sample_task_read

        # 実行
        result = task_application_service.get_by_id(sample_task_read.id)

        # 検証
        assert result == sample_task_read
        mock_task_service.get_by_id.assert_called_once_with(sample_task_read.id, with_details=False)

    def test_get_by_id_not_found(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: ID指定タスク取得でタスクが見つからない場合"""
        # モックの設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_by_id.return_value = None

        task_id = uuid.uuid4()

        # 実行
        result = task_application_service.get_by_id(task_id)

        # 検証
        assert result is None
        mock_task_service.get_by_id.assert_called_once_with(task_id, with_details=False)

    # 全ステータス辞書取得APIは現行仕様に存在しないため対象外

    def test_get_all_tasks(self, task_application_service: TaskApplicationService, mock_unit_of_work: Mock) -> None:
        """正常系: 全件取得"""
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.get_all.return_value = []

        result = task_application_service.get_all_tasks()
        assert isinstance(result, list)
        mock_task_service.get_all.assert_called_once()
