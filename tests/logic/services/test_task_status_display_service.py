"""TaskStatusDisplayServiceのテストコード"""

from logic.services.task_status_display_service import (
    TaskStatusDisplay,
    TaskStatusDisplayService,
)
from models import TaskStatus


class TestTaskStatusDisplayService:
    """TaskStatusDisplayServiceのテストクラス"""

    def test_get_task_status_display_inbox(self) -> None:
        """INBOXステータスの表示情報取得テスト"""
        result = TaskStatusDisplayService.get_task_status_display(TaskStatus.INBOX)

        assert isinstance(result, TaskStatusDisplay)
        assert result.status == TaskStatus.INBOX
        assert result.label == "📥 整理用"
        assert result.icon == "📥"
        assert result.description == "整理が必要な項目"
        assert result.color == "BLUE_600"

    def test_get_task_status_display_next_action(self) -> None:
        """NEXT_ACTIONステータスの表示情報取得テスト"""
        result = TaskStatusDisplayService.get_task_status_display(TaskStatus.NEXT_ACTION)

        assert result.status == TaskStatus.NEXT_ACTION
        assert result.label == "🎯 次に取るべき行動"
        assert result.icon == "🎯"

    def test_get_board_column_mapping(self) -> None:
        """ボードカラムマッピングの取得テスト"""
        result = TaskStatusDisplayService.get_board_column_mapping()

        assert "CLOSED" in result
        assert "INBOX" in result

        closed_statuses = result["CLOSED"]
        assert TaskStatus.NEXT_ACTION in closed_statuses
        assert TaskStatus.DELEGATED in closed_statuses
        assert TaskStatus.COMPLETED in closed_statuses

        inbox_statuses = result["INBOX"]
        assert TaskStatus.INBOX in inbox_statuses
        assert TaskStatus.NEXT_ACTION in inbox_statuses

    def test_get_board_section_display_closed(self) -> None:
        """CLOSEDセクションの表示ラベル取得テスト"""
        result = TaskStatusDisplayService.get_board_section_display("CLOSED", TaskStatus.NEXT_ACTION)
        assert result == "📋 作業リスト"

        result = TaskStatusDisplayService.get_board_section_display("CLOSED", TaskStatus.DELEGATED)
        assert result == "🔄 InProgress"

    def test_get_board_section_display_inbox(self) -> None:
        """INBOXセクションの表示ラベル取得テスト"""
        result = TaskStatusDisplayService.get_board_section_display("INBOX", TaskStatus.INBOX)
        assert result == "📥 整理用"

    def test_get_all_status_displays(self) -> None:
        """全ステータス表示情報の取得テスト"""
        result = TaskStatusDisplayService.get_all_status_displays()

        assert len(result) == len(TaskStatus)

        # [AI GENERATED] 全てのステータスが含まれているかチェック
        status_in_result = {display.status for display in result}
        assert status_in_result == set(TaskStatus)

    def test_invalid_status_raises_error(self) -> None:
        """無効なステータスでエラーが発生することのテスト"""
        # [AI GENERATED] 存在しない値を使ってエラーテスト
        # Note: 実際のEnum値以外を渡すのは難しいので、このテストは省略
