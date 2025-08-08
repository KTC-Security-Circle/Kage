"""TaskApplicationServiceの新機能（QuickAction、表示関連）のテストコード"""

from datetime import date

from logic.application.task_application_service import TaskApplicationService
from logic.services.task_status_display_service import TaskStatusDisplay
from models import QuickActionCommand, TaskStatus

EXPECTED_QUICK_ACTIONS_COUNT = 4


class TestTaskApplicationServiceDisplayFeatures:
    """TaskApplicationServiceの表示機能関連のテストクラス"""

    def setup_method(self) -> None:
        """各テストメソッド実行前の準備"""
        self.service = TaskApplicationService()

    def test_get_task_status_for_quick_action_do_now(self) -> None:
        """DO_NOWアクションのステータス取得テスト"""
        result = self.service.get_task_status_for_quick_action(QuickActionCommand.DO_NOW)
        assert result == TaskStatus.NEXT_ACTION

    def test_get_task_status_for_quick_action_do_someday(self) -> None:
        """DO_SOMEDAYアクションのステータス取得テスト"""
        result = self.service.get_task_status_for_quick_action(QuickActionCommand.DO_SOMEDAY)
        assert result == TaskStatus.SOMEDAY_MAYBE

    def test_get_task_status_for_quick_action_reference(self) -> None:
        """REFERENCEアクションのステータス取得テスト"""
        result = self.service.get_task_status_for_quick_action(QuickActionCommand.REFERENCE)
        assert result == TaskStatus.INBOX

    def test_get_available_quick_actions(self) -> None:
        """利用可能なクイックアクション取得テスト"""
        result = self.service.get_available_quick_actions()
        assert len(result) == EXPECTED_QUICK_ACTIONS_COUNT
        assert QuickActionCommand.DO_NOW in result
        assert QuickActionCommand.DO_NEXT in result
        assert QuickActionCommand.DO_SOMEDAY in result
        assert QuickActionCommand.REFERENCE in result

    def test_get_quick_action_description(self) -> None:
        """クイックアクション説明取得テスト"""
        result = self.service.get_quick_action_description(QuickActionCommand.DO_NOW)
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "今すぐ実行すべきタスク"

    def test_get_task_status_display(self) -> None:
        """タスクステータス表示情報取得テスト"""
        result = self.service.get_task_status_display(TaskStatus.INBOX)
        assert isinstance(result, TaskStatusDisplay)
        assert result.status == TaskStatus.INBOX
        assert result.label == "📥 整理用"
        assert result.icon == "📥"

    def test_get_board_column_mapping(self) -> None:
        """ボードカラムマッピング取得テスト"""
        result = self.service.get_board_column_mapping()
        assert "CLOSED" in result
        assert "INBOX" in result
        assert TaskStatus.NEXT_ACTION in result["CLOSED"]
        assert TaskStatus.INBOX in result["INBOX"]

    def test_get_board_section_display(self) -> None:
        """ボードセクション表示ラベル取得テスト"""
        result = self.service.get_board_section_display("CLOSED", TaskStatus.NEXT_ACTION)
        assert result == "📋 作業リスト"

        result = self.service.get_board_section_display("INBOX", TaskStatus.INBOX)
        assert result == "📥 整理用"

    def test_get_all_status_displays(self) -> None:
        """全ステータス表示情報取得テスト"""
        result = self.service.get_all_status_displays()
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

    def test_create_task_from_quick_action(self) -> None:
        """QuickAction経由でのタスク作成テスト"""
        # [AI GENERATED] テスト用のタスクデータ
        test_title = "テストタスク"
        test_description = "テスト用の説明"
        test_due_date = date(2025, 12, 31)

        # [AI GENERATED] DO_NOWアクションでタスク作成
        result = self.service.create_task_from_quick_action(
            action=QuickActionCommand.DO_NOW,
            title=test_title,
            description=test_description,
            due_date=test_due_date,
        )

        # [AI GENERATED] 作成されたタスクの検証
        assert result.title == test_title
        assert result.description == test_description
        assert result.status == TaskStatus.NEXT_ACTION
        assert result.due_date == test_due_date

    def test_create_task_from_quick_action_reference(self) -> None:
        """REFERENCEアクション経由でのタスク作成テスト"""
        result = self.service.create_task_from_quick_action(
            action=QuickActionCommand.REFERENCE,
            title="参考資料",
            description="整理が必要な資料",
        )

        assert result.title == "参考資料"
        assert result.status == TaskStatus.INBOX
        assert result.due_date is None

    def test_create_task_from_quick_action_someday(self) -> None:
        """DO_SOMEDAYアクション経由でのタスク作成テスト"""
        result = self.service.create_task_from_quick_action(
            action=QuickActionCommand.DO_SOMEDAY,
            title="いつかやりたいこと",
        )

        assert result.title == "いつかやりたいこと"
        assert result.status == TaskStatus.SOMEDAY_MAYBE
        assert result.description == ""
