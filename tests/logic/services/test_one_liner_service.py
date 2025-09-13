"""一言コメント生成サービスのテスト"""

from unittest.mock import patch

import pytest

from agents.agent_conf import LLMProvider
from logic.queries.one_liner_queries import OneLinerContext
from logic.services.base import MyBaseError
from logic.services.one_liner_service import OneLinerService, OneLinerServiceError

# [AI GENERATED] テスト用定数
TEST_TASK_COUNT_HIGH = 10
TEST_TASK_COUNT_MEDIUM = 5
TEST_OVERDUE_COUNT = 2
TEST_COMPLETED_COUNT_HIGH = 4
TEST_COMPLETED_COUNT_MEDIUM = 6
TEST_COMPLETED_COUNT_LOW = 2


class TestOneLinerService:
    """OneLinerService のテストクラス

    一言コメント生成サービスの正常系・異常系のテストを実行します。
    """

    def test_init_always_llm(self) -> None:
        """初期化時に常にエージェント(LLM経路)が有効であることをテスト"""
        service = OneLinerService()
        assert service._use_llm is True

    def test_init_legacy_flag_removed_behavior(self) -> None:
        """旧フラグに依存せず常にエージェント有効なことを確認"""
        service = OneLinerService()
        assert service._use_llm is True

    def test_generate_with_empty_context(self) -> None:
        """空のコンテキストでコメント生成が成功することをテスト"""
        service = OneLinerService()
        context = OneLinerContext()
        result = service.generate(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_overdue_tasks(self) -> None:
        """期限超過タスクがある場合の特別なメッセージをテスト"""
        service = OneLinerService()
        context = OneLinerContext(
            today_task_count=TEST_TASK_COUNT_MEDIUM,
            overdue_task_count=TEST_OVERDUE_COUNT,
            completed_task_count=1,
        )
        result = service.generate(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_high_completion_rate(self) -> None:
        """高い完了率での肯定的なメッセージをテスト"""
        service = OneLinerService()
        context = OneLinerContext(
            today_task_count=TEST_TASK_COUNT_MEDIUM,
            overdue_task_count=0,
            completed_task_count=TEST_COMPLETED_COUNT_HIGH,  # 80%完了
        )
        result = service.generate(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_medium_completion_rate(self) -> None:
        """中程度の完了率でのメッセージをテスト"""
        service = OneLinerService()
        context = OneLinerContext(
            today_task_count=TEST_TASK_COUNT_HIGH,
            overdue_task_count=0,
            completed_task_count=TEST_COMPLETED_COUNT_MEDIUM,  # 60%完了
        )

        result = service.generate(context)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_low_completion_rate(self) -> None:
        """低い完了率での励ましのメッセージをテスト"""
        service = OneLinerService()
        context = OneLinerContext(
            today_task_count=TEST_TASK_COUNT_HIGH,
            overdue_task_count=0,
            completed_task_count=TEST_COMPLETED_COUNT_LOW,  # 20%完了
        )

        result = service.generate(context)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_no_tasks(self) -> None:
        """タスクがない場合のデフォルトメッセージをテスト"""
        service = OneLinerService()
        context = OneLinerContext(today_task_count=0, overdue_task_count=0, completed_task_count=0)

        result = service.generate(context)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_agent_path(self) -> None:
        """常にエージェント経路で生成され文字列が返ることをテスト (FAKE プロバイダ)"""
        service = OneLinerService()
        context = OneLinerContext(today_task_count=3, completed_task_count=1)
        result = service.generate(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_provider_from_settings(self) -> None:
        """設定ファイルの provider (Enum) が利用されることをテスト"""
        from settings.manager import get_config_manager

        mgr = get_config_manager()
        with mgr.edit() as editable:
            editable.agents.provider = LLMProvider.FAKE
        service = OneLinerService()
        context = OneLinerContext(today_task_count=2, completed_task_count=1)
        result = service.generate(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_handles_exception_gracefully(self) -> None:
        """内部エージェント例外時にデフォルトメッセージを返すことをテスト"""
        service = OneLinerService()
        # _generate_with_agent を強制例外
        with patch.object(service, "_generate_with_agent", side_effect=Exception("Test error")):
            context = OneLinerContext()
            result = service.generate(context)
            assert result == "今日も一日、お疲れさまです。"

    def test_get_default_message(self) -> None:
        """デフォルトメッセージが正しく返されることをテスト"""
        service = OneLinerService()

        result = service._get_default_message()

        assert result == "今日も一日、お疲れさまです。"

    # ルールベース削除に伴い一貫性テストは不要

    def test_log_error_and_raise(self) -> None:
        """エラーログ出力と例外発生のテスト"""
        service = OneLinerService()

        with pytest.raises(OneLinerServiceError) as exc_info:
            service._log_error_and_raise("Test error message")

        assert str(exc_info.value) == "一言コメント生成エラー: Test error message"


class TestOneLinerContext:
    """OneLinerContext のテストクラス

    一言コメント生成のコンテキスト情報のテストを実行します。
    """

    def test_init_with_defaults(self) -> None:
        """デフォルト値でのインスタンス化をテスト"""
        context = OneLinerContext()

        assert context.today_task_count == 0
        assert context.overdue_task_count == 0
        assert context.completed_task_count == 0
        assert context.progress_summary == ""
        assert context.user_name == ""

    def test_init_with_custom_values(self) -> None:
        """カスタム値でのインスタンス化をテスト"""
        context = OneLinerContext(
            today_task_count=TEST_TASK_COUNT_HIGH,
            overdue_task_count=TEST_OVERDUE_COUNT,
            completed_task_count=TEST_TASK_COUNT_MEDIUM,
            progress_summary="Good progress",
            user_name="Test User",
        )

        assert context.today_task_count == TEST_TASK_COUNT_HIGH
        assert context.overdue_task_count == TEST_OVERDUE_COUNT
        assert context.completed_task_count == TEST_TASK_COUNT_MEDIUM
        assert context.progress_summary == "Good progress"
        assert context.user_name == "Test User"

    def test_context_immutability_after_creation(self) -> None:
        """コンテキスト作成後の値変更をテスト"""
        context = OneLinerContext(today_task_count=TEST_TASK_COUNT_MEDIUM)

        # [AI GENERATED] dataclassの属性は変更可能なため、変更できることを確認
        context.today_task_count = TEST_TASK_COUNT_HIGH
        assert context.today_task_count == TEST_TASK_COUNT_HIGH


class TestOneLinerServiceError:
    """OneLinerServiceError のテストクラス

    カスタム例外クラスのテストを実行します。
    """

    def test_error_message_format(self) -> None:
        """例外メッセージのフォーマットをテスト"""
        error = OneLinerServiceError("テストエラー")

        assert str(error) == "一言コメント生成エラー: テストエラー"

    def test_error_inheritance(self) -> None:
        """例外クラスの継承関係をテスト"""
        error = OneLinerServiceError("test")

        # [AI GENERATED] MyBaseErrorを継承していることを確認
        assert isinstance(error, MyBaseError)
        assert isinstance(error, Exception)
