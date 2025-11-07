"""MemoApplicationService のテスト（現行API）

Unit of Work のモックを用い、MemoApplicationService の公開APIを検証する。
"""

import uuid
from unittest.mock import Mock

import pytest

from agents.base import AgentError
from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
from agents.task_agents.memo_to_task.state import MemoToTaskState
from logic.application.memo_application_service import (
    ContentValidationError,
    MemoApplicationError,
    MemoApplicationService,
)
from models import MemoRead, MemoStatus, MemoUpdate

# テスト用定数
EXPECTED_PAIR_COUNT = 2


class TestMemoApplicationService:
    """MemoApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_memo_service = Mock()

        mock_uow.service_factory = mock_service_factory
        # ApplicationService 実装は uow.get_service(...) と uow.service_factory.get_service(...) の
        # 両方を使用するため、どちらも同じモックを返すように設定する。
        mock_uow.get_service = Mock(return_value=mock_memo_service)
        mock_service_factory.get_service.return_value = mock_memo_service

        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def memo_app_service(self, mock_unit_of_work_factory: Mock) -> MemoApplicationService:
        """MemoApplicationServiceのインスタンスを作成"""
        return MemoApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_memo_read(self) -> MemoRead:
        """テスト用のMemoReadデータを作成"""
        return MemoRead(
            id=uuid.uuid4(),
            title="メモタイトル",
            content="テスト用メモ",
            status=MemoStatus.INBOX,
        )

    def test_create_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
        sample_memo_read: MemoRead,
    ) -> None:
        """正常系: メモ作成成功"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_memo_service.create.return_value = sample_memo_read

        result = memo_app_service.create(title="メモタイトル", content="テスト用メモ")

        assert isinstance(result, MemoRead)
        assert result.title == sample_memo_read.title
        mock_memo_service.create.assert_called_once()

    @pytest.mark.parametrize(
        ("title", "content", "expected_msg"),
        [
            ("", "内容", "メモタイトルを入力してください"),
            ("   ", "内容", "メモタイトルを入力してください"),
            ("タイトル", "", "メモ内容を入力してください"),
            ("タイトル", "   ", "メモ内容を入力してください"),
        ],
    )
    def test_create_validation_error(
        self, memo_app_service: MemoApplicationService, title: str, content: str, expected_msg: str
    ) -> None:
        """異常系: 作成時のバリデーションエラー"""
        with pytest.raises(ContentValidationError, match=expected_msg):
            memo_app_service.create(title=title, content=content)

    def test_update_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
        sample_memo_read: MemoRead,
    ) -> None:
        """正常系: メモ更新成功"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        updated = sample_memo_read.model_copy(update={"content": "更新後メモ"})
        mock_memo_service.update.return_value = updated

        upd = MemoUpdate(content="更新後メモ")
        result = memo_app_service.update(sample_memo_read.id, upd)

        assert isinstance(result, MemoRead)
        assert result.content == "更新後メモ"
        mock_memo_service.update.assert_called_once()

    def test_delete_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: メモ削除成功"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        memo_id = uuid.uuid4()
        mock_memo_service.delete.return_value = True

        result = memo_app_service.delete(memo_id)

        assert result is True
        mock_memo_service.delete.assert_called_once_with(memo_id)

    def test_get_by_id_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
        sample_memo_read: MemoRead,
    ) -> None:
        """正常系: ID指定メモ取得"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_memo_service.get_by_id.return_value = sample_memo_read

        result = memo_app_service.get_by_id(sample_memo_read.id)

        assert result == sample_memo_read
        mock_memo_service.get_by_id.assert_called_once_with(sample_memo_read.id, with_details=False)

    def test_get_by_id_not_found(self, memo_app_service: MemoApplicationService, mock_unit_of_work: Mock) -> None:
        """正常系: ID指定メモ取得で見つからない場合"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_memo_service.get_by_id.return_value = None

        memo_id = uuid.uuid4()
        result = memo_app_service.get_by_id(memo_id)

        assert result is None
        mock_memo_service.get_by_id.assert_called_once_with(memo_id, with_details=False)

    def test_get_all_memos(self, memo_app_service: MemoApplicationService, mock_unit_of_work: Mock) -> None:
        """正常系: 全件取得"""
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        memos = [
            MemoRead(id=uuid.uuid4(), title="A", content="a", status=MemoStatus.INBOX),
            MemoRead(id=uuid.uuid4(), title="B", content="b", status=MemoStatus.INBOX),
        ]
        mock_memo_service.get_all.return_value = memos

        result = memo_app_service.get_all_memos()

        assert result == memos
        assert len(result) == EXPECTED_PAIR_COUNT
        mock_memo_service.get_all.assert_called_once_with(with_details=False)

    def test_clarify_memo_returns_clarify_for_empty_input(
        self,
        memo_app_service: MemoApplicationService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """メモが空の場合はタスクなし・clarifyステータスを返す"""

        monkeypatch.setattr(MemoApplicationService, "_collect_existing_tag_names", lambda _self: [])

        empty_memo = MemoRead(id=uuid.uuid4(), title="空メモ", content="   ", status=MemoStatus.INBOX)

        result = memo_app_service.clarify_memo(empty_memo)

        assert result.tasks == []
        assert result.suggested_memo_status == "clarify"

    def test_clarify_memo_success_with_due_date_and_tags(
        self,
        memo_app_service: MemoApplicationService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """エージェントの結果が期日とタグを含む場合にそのまま返す"""

        existing_tags = ["レポート", "買い物"]
        monkeypatch.setattr(MemoApplicationService, "_collect_existing_tag_names", lambda _self: existing_tags)

        memo = MemoRead(
            id=uuid.uuid4(),
            title="レポート整理",
            content="レポートをまとめる",
            status=MemoStatus.INBOX,
        )

        agent_output = MemoToTaskAgentOutput(
            tasks=[
                TaskDraft(
                    title="金曜までにレポート提出",
                    description="部長へメール送付",
                    due_date="2025-11-10",
                    tags=["レポート"],
                    route="calendar",
                )
            ],
            suggested_memo_status="active",
        )

        def _fake_invoke(self: MemoApplicationService, _state: MemoToTaskState) -> MemoToTaskAgentOutput:
            assert _state["memo"] is memo
            assert getattr(_state["memo"], "title", "") == memo.title
            return agent_output

        monkeypatch.setattr(MemoApplicationService, "_invoke_memo_to_task_agent", _fake_invoke)

        result = memo_app_service.clarify_memo(memo)

        assert result.suggested_memo_status == "active"
        assert result.tasks[0].due_date == "2025-11-10"
        assert result.tasks[0].tags == ["レポート"]

    def test_clarify_memo_agent_error_raises(
        self,
        memo_app_service: MemoApplicationService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """エージェントがエラーを返す場合は例外を送出"""

        monkeypatch.setattr(MemoApplicationService, "_collect_existing_tag_names", lambda _self: [])

        error_response = AgentError("failure")

        def _fake_invoke_error(
            self: MemoApplicationService,
            _state: MemoToTaskState,
        ) -> AgentError:
            return error_response

        monkeypatch.setattr(MemoApplicationService, "_invoke_memo_to_task_agent", _fake_invoke_error)

        failing_memo = MemoRead(
            id=uuid.uuid4(),
            title="エラーになる入力",
            content="エラーになる入力",
            status=MemoStatus.INBOX,
        )

        with pytest.raises(MemoApplicationError):
            memo_app_service.clarify_memo(failing_memo)

    def test_generate_tasks_from_memo_returns_only_task_list(
        self,
        memo_app_service: MemoApplicationService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """generate_tasks_from_memoはタスクリストのみを返却する"""

        agent_output = MemoToTaskAgentOutput(
            tasks=[
                TaskDraft(title="牛乳を買う", description=None, due_date=None, tags=["買い物"], route="progress"),
                TaskDraft(title="請求書送付", description="経理宛", due_date=None, tags=["仕事"], route="next_action"),
            ],
            suggested_memo_status="active",
        )

        monkeypatch.setattr(
            MemoApplicationService,
            "clarify_memo",
            lambda _self, _memo: agent_output,
        )

        memo = MemoRead(id=uuid.uuid4(), title="買い物リスト", content="買い物リスト", status=MemoStatus.INBOX)

        tasks = memo_app_service.generate_tasks_from_memo(memo)

        assert tasks == agent_output.tasks
        assert tasks is not agent_output.tasks
    # 追加: 検索API
    def test_search_empty_query_returns_empty(self, memo_app_service: MemoApplicationService) -> None:
        """空クエリは空配列を返す"""
        assert memo_app_service.search("") == []

    def test_search_delegates_to_service_and_filters_status(
        self, memo_app_service: MemoApplicationService, mock_unit_of_work: Mock
    ) -> None:
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        m1 = MemoRead(id=uuid.uuid4(), title="t1", content="c1", status=MemoStatus.INBOX)
        m2 = MemoRead(id=uuid.uuid4(), title="t2", content="c2", status=MemoStatus.ARCHIVE)
        mock_memo_service.search_memos.return_value = [m1, m2]
        mock_memo_service.list_by_status.return_value = [m1]

        out = memo_app_service.search("t", status=MemoStatus.INBOX)

        assert out == [m1]
        mock_memo_service.search_memos.assert_called_once_with("t", with_details=False)
        mock_memo_service.list_by_status.assert_called_once_with(MemoStatus.INBOX, with_details=False)

    def test_search_filters_by_tags_using_repository(
        self, memo_app_service: MemoApplicationService, mock_unit_of_work: Mock
    ) -> None:
        # 準備: サービス検索は2件返る
        mock_memo_service = mock_unit_of_work.service_factory.get_service.return_value
        t1 = uuid.uuid4()
        t2 = uuid.uuid4()
        m1 = MemoRead(id=t1, title="x", content="x", status=MemoStatus.INBOX)
        m2 = MemoRead(id=t2, title="y", content="y", status=MemoStatus.INBOX)
        mock_memo_service.search_memos.return_value = [m1, m2]

        # リポジトリファクトリとメモリポジトリのモック
        memo_repo_mock = Mock()
        memo_repo_mock.list_by_tag.return_value = [m1]
        repo_factory_mock = Mock()
        repo_factory_mock.create.return_value = memo_repo_mock
        mock_unit_of_work.repository_factory = repo_factory_mock

        out = memo_app_service.search("x", tags=[uuid.uuid4()])
        assert out == [m1]
