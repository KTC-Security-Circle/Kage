"""QuickActionMappingServiceのテストコード"""

from logic.services.quick_action_mapping_service import QuickActionMappingService
from models import QuickActionCommand, TaskStatus

EXPECTED_QUICK_ACTION_COUNT = 4


class TestQuickActionMappingService:
    """QuickActionMappingServiceのテストクラス"""

    def test_map_quick_action_to_task_status_do_now(self) -> None:
        """DO_NOWアクションのマッピングテスト"""
        result = QuickActionMappingService.map_quick_action_to_task_status(QuickActionCommand.DO_NOW)
        assert result == TaskStatus.NEXT_ACTION

    def test_map_quick_action_to_task_status_do_next(self) -> None:
        """DO_NEXTアクションのマッピングテスト"""
        result = QuickActionMappingService.map_quick_action_to_task_status(QuickActionCommand.DO_NEXT)
        assert result == TaskStatus.NEXT_ACTION

    def test_map_quick_action_to_task_status_do_someday(self) -> None:
        """DO_SOMEDAYアクションのマッピングテスト"""
        result = QuickActionMappingService.map_quick_action_to_task_status(QuickActionCommand.DO_SOMEDAY)
        assert result == TaskStatus.SOMEDAY_MAYBE

    def test_map_quick_action_to_task_status_reference(self) -> None:
        """REFERENCEアクションのマッピングテスト"""
        result = QuickActionMappingService.map_quick_action_to_task_status(QuickActionCommand.REFERENCE)
        assert result == TaskStatus.INBOX

    def test_get_available_quick_actions(self) -> None:
        """利用可能なクイックアクションリストの取得テスト"""
        result = QuickActionMappingService.get_available_quick_actions()
        expected = [
            QuickActionCommand.DO_NOW,
            QuickActionCommand.DO_NEXT,
            QuickActionCommand.DO_SOMEDAY,
            QuickActionCommand.REFERENCE,
        ]
        assert result == expected

        assert len(result) == EXPECTED_QUICK_ACTION_COUNT

    def test_get_quick_action_description_all_actions(self) -> None:
        """全てのクイックアクションの説明取得テスト"""
        actions = QuickActionMappingService.get_available_quick_actions()

        for action in actions:
            description = QuickActionMappingService.get_quick_action_description(action)
            assert isinstance(description, str)
            assert len(description) > 0

    def test_get_quick_action_description_specific(self) -> None:
        """特定のクイックアクション説明のテスト"""
        result = QuickActionMappingService.get_quick_action_description(QuickActionCommand.DO_NOW)
        assert result == "今すぐ実行すべきタスク"
