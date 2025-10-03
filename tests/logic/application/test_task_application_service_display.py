"""TaskApplicationServiceの新機能（QuickAction、表示関連）のテストコード"""

import uuid
from datetime import date
from unittest.mock import Mock

import pytest

from logic.application.task_application_service import TaskApplicationService
from logic.services.task_status_display_service import TaskStatusDisplay
from models import QuickActionCommand, TaskRead, TaskStatus

EXPECTED_QUICK_ACTIONS_COUNT = 4


class TestTaskApplicationServiceDisplayFeatures:
    """TaskApplicationServiceの表示機能関連のテストクラス"""

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

    def test_get_task_status_for_quick_action_do_now(self, task_application_service: TaskApplicationService) -> None:
        """DO_NOWアクションのステータス取得テスト"""
        # Arrange & Act
        result = task_application_service.get_task_status_for_quick_action(QuickActionCommand.DO_NOW)

        # Assert
        assert result == TaskStatus.NEXT_ACTION

    def test_get_task_status_for_quick_action_do_someday(
        self, task_application_service: TaskApplicationService
    ) -> None:
        """DO_SOMEDAYアクションのステータス取得テスト"""
        # Arrange & Act
        result = task_application_service.get_task_status_for_quick_action(QuickActionCommand.DO_SOMEDAY)

        # Assert
        assert result == TaskStatus.SOMEDAY_MAYBE

    def test_get_task_status_for_quick_action_reference(self, task_application_service: TaskApplicationService) -> None:
        """REFERENCEアクションのステータス取得テスト"""
        # Arrange & Act
        result = task_application_service.get_task_status_for_quick_action(QuickActionCommand.REFERENCE)

        # Assert
        assert result == TaskStatus.INBOX

    def test_get_available_quick_actions(self, task_application_service: TaskApplicationService) -> None:
        """利用可能なクイックアクション取得テスト"""
        # Arrange & Act
        result = task_application_service.get_available_quick_actions()

        # Assert
        assert len(result) == EXPECTED_QUICK_ACTIONS_COUNT
        assert QuickActionCommand.DO_NOW in result
        assert QuickActionCommand.DO_NEXT in result
        assert QuickActionCommand.DO_SOMEDAY in result
        assert QuickActionCommand.REFERENCE in result

    def test_get_quick_action_description(self, task_application_service: TaskApplicationService) -> None:
        """クイックアクション説明取得テスト"""
        # Arrange & Act
        result = task_application_service.get_quick_action_description(QuickActionCommand.DO_NOW)

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "今すぐ実行すべきタスク"

    def test_get_task_status_display(self, task_application_service: TaskApplicationService) -> None:
        """タスクステータス表示情報取得テスト"""
        # Arrange & Act
        result = task_application_service.get_task_status_display(TaskStatus.INBOX)

        # Assert
        assert isinstance(result, TaskStatusDisplay)
        assert result.status == TaskStatus.INBOX
        assert result.label == "📥 整理用"
        assert result.icon == "📥"

    def test_get_board_column_mapping(self, task_application_service: TaskApplicationService) -> None:
        """ボードカラムマッピング取得テスト"""
        # Arrange & Act
        result = task_application_service.get_board_column_mapping()

        # Assert
        assert "CLOSED" in result
        assert "INBOX" in result
        assert TaskStatus.NEXT_ACTION in result["CLOSED"]
        assert TaskStatus.INBOX in result["INBOX"]

    def test_get_board_section_display(self, task_application_service: TaskApplicationService) -> None:
        """ボードセクション表示ラベル取得テスト"""
        # Arrange & Act & Assert
        result = task_application_service.get_board_section_display("CLOSED", TaskStatus.NEXT_ACTION)
        assert result == "📋 作業リスト"

        result = task_application_service.get_board_section_display("INBOX", TaskStatus.INBOX)
        assert result == "📥 整理用"

    def test_get_all_status_displays(self, task_application_service: TaskApplicationService) -> None:
        """全ステータス表示情報取得テスト"""
        # Arrange & Act
        result = task_application_service.get_all_status_displays()

        # Assert
        assert len(result) == len(TaskStatus)

        # [AI GENERATED] 全てのタスクステータスが含まれているかチェック
        status_in_result = {display.status for display in result}
        assert status_in_result == set(TaskStatus)

        # [AI GENERATED] 各表示情報が正しい形式か確認
        for display in result:
            assert isinstance(display, TaskStatusDisplay)
            assert isinstance(display.label, str)
            assert isinstance(display.icon, str)
            assert len(display.label) > 0
            assert len(display.icon) > 0

    def test_create_task_from_quick_action(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """QuickAction経由でのタスク作成テスト"""
        # Arrange
        test_title = "テストタスク"
        test_description = "テスト用の説明"
        test_due_date = date(2025, 12, 31)

        expected_task = TaskRead(
            id=uuid.uuid4(),
            title=test_title,
            description=test_description,
            status=TaskStatus.NEXT_ACTION,
            due_date=test_due_date,
        )

        # [AI GENERATED] モックのタスクサービスの戻り値を設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.create_task.return_value = expected_task

        # Act
        result = task_application_service.create_task_from_quick_action(
            action=QuickActionCommand.DO_NOW,
            title=test_title,
            description=test_description,
            due_date=test_due_date,
        )

        # Assert
        assert result.title == test_title
        assert result.description == test_description
        assert result.status == TaskStatus.NEXT_ACTION
        assert result.due_date == test_due_date

        # [AI GENERATED] サービスが適切に呼ばれたことを確認
        mock_task_service.create_task.assert_called_once()

    def test_create_task_from_quick_action_reference(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """REFERENCEアクション経由でのタスク作成テスト"""
        # Arrange
        test_title = "参考資料"
        test_description = "整理が必要な資料"

        expected_task = TaskRead(
            id=uuid.uuid4(),
            title=test_title,
            description=test_description,
            status=TaskStatus.INBOX,
            due_date=None,
        )

        # [AI GENERATED] モックのタスクサービスの戻り値を設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.create_task.return_value = expected_task

        # Act
        result = task_application_service.create_task_from_quick_action(
            action=QuickActionCommand.REFERENCE,
            title=test_title,
            description=test_description,
        )

        # Assert
        assert result.title == test_title
        assert result.status == TaskStatus.INBOX
        assert result.due_date is None

    def test_create_task_from_quick_action_someday(
        self,
        task_application_service: TaskApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """DO_SOMEDAYアクション経由でのタスク作成テスト"""
        # Arrange
        test_title = "いつかやりたいこと"

        expected_task = TaskRead(
            id=uuid.uuid4(),
            title=test_title,
            description="",
            status=TaskStatus.SOMEDAY_MAYBE,
            due_date=None,
        )

        # [AI GENERATED] モックのタスクサービスの戻り値を設定
        mock_task_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_task_service.create_task.return_value = expected_task

        # Act
        result = task_application_service.create_task_from_quick_action(
            action=QuickActionCommand.DO_SOMEDAY,
            title=test_title,
        )

        # Assert
        assert result.title == test_title
        assert result.status == TaskStatus.SOMEDAY_MAYBE
        assert result.description == ""
