"""メモApplication Serviceのテスト"""

import uuid
from unittest.mock import Mock

import pytest

from logic.application.memo_application_service import MemoApplicationService
from logic.commands.memo_commands import CreateMemoCommand, DeleteMemoCommand, UpdateMemoCommand
from logic.queries.memo_queries import (
    GetAllMemosQuery,
    GetMemoByIdQuery,
    GetMemosByTaskIdQuery,
    SearchMemosQuery,
)
from models import MemoRead

# 定数
EXPECTED_MEMO_PAIR_COUNT = 2


class TestMemoApplicationService:
    """MemoApplicationServiceのテストクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_memo_service = Mock()

        # [AI GENERATED] モックの階層構造を設定
        mock_uow.service_factory = mock_service_factory
        mock_service_factory.create_memo_service.return_value = mock_memo_service

        # [AI GENERATED] コンテキストマネージャとして機能させる
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

    def test_create_memo_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """メモ作成のテスト（正常系）"""
        # Arrange
        task_id = uuid.uuid4()
        command = CreateMemoCommand(content="テスト用メモ", task_id=task_id)

        created_memo = MemoRead(
            id=uuid.uuid4(),
            content="テスト用メモ",
            task_id=task_id,
        )

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.create_memo.return_value = created_memo

        # Act
        result = memo_app_service.create_memo(command)

        # Assert
        assert result == created_memo
        mock_memo_service.create_memo.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_create_memo_validation_error(
        self,
        memo_app_service: MemoApplicationService,
    ) -> None:
        """メモ作成のテスト（バリデーションエラー）"""
        # Arrange
        task_id = uuid.uuid4()
        command = CreateMemoCommand(content="", task_id=task_id)  # 空文字

        # Act & Assert
        with pytest.raises(ValueError, match="メモ内容を入力してください"):
            memo_app_service.create_memo(command)

    def test_create_memo_whitespace_validation(
        self,
        memo_app_service: MemoApplicationService,
    ) -> None:
        """メモ作成のテスト（空白のみのバリデーションエラー）"""
        # Arrange
        task_id = uuid.uuid4()
        command = CreateMemoCommand(content="   ", task_id=task_id)  # 空白のみ

        # Act & Assert
        with pytest.raises(ValueError, match="メモ内容を入力してください"):
            memo_app_service.create_memo(command)

    def test_update_memo_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """メモ更新のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()
        command = UpdateMemoCommand(memo_id=memo_id, content="更新後メモ")

        updated_memo = MemoRead(
            id=memo_id,
            content="更新後メモ",
            task_id=task_id,
        )

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.update_memo.return_value = updated_memo

        # Act
        result = memo_app_service.update_memo(command)

        # Assert
        assert result == updated_memo
        mock_memo_service.update_memo.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_update_memo_validation_error(
        self,
        memo_app_service: MemoApplicationService,
    ) -> None:
        """メモ更新のテスト（バリデーションエラー）"""
        # Arrange
        memo_id = uuid.uuid4()
        command = UpdateMemoCommand(memo_id=memo_id, content="")  # 空文字

        # Act & Assert
        with pytest.raises(ValueError, match="メモ内容を入力してください"):
            memo_app_service.update_memo(command)

    def test_delete_memo_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """メモ削除のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        command = DeleteMemoCommand(memo_id=memo_id)

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.delete_memo.return_value = True

        # Act
        result = memo_app_service.delete_memo(command)

        # Assert
        assert result is True
        mock_memo_service.delete_memo.assert_called_once_with(memo_id)
        mock_unit_of_work.commit.assert_called_once()

    def test_get_memo_by_id_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """IDでメモ取得のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()
        query = GetMemoByIdQuery(memo_id=memo_id)

        memo = MemoRead(
            id=memo_id,
            content="取得テスト用メモ",
            task_id=task_id,
        )

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.get_memo_by_id.return_value = memo

        # Act
        result = memo_app_service.get_memo_by_id(query)

        # Assert
        assert result == memo
        mock_memo_service.get_memo_by_id.assert_called_once_with(memo_id)

    def test_get_memo_by_id_not_found(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """IDでメモ取得のテスト（見つからない場合）"""
        # Arrange
        memo_id = uuid.uuid4()
        query = GetMemoByIdQuery(memo_id=memo_id)

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.get_memo_by_id.return_value = None

        # Act
        result = memo_app_service.get_memo_by_id(query)

        # Assert
        assert result is None
        mock_memo_service.get_memo_by_id.assert_called_once_with(memo_id)

    def test_get_all_memos_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """全メモ取得のテスト（正常系）"""
        # Arrange
        query = GetAllMemosQuery()
        task_id = uuid.uuid4()
        memos = [
            MemoRead(id=uuid.uuid4(), content="メモ1", task_id=task_id),
            MemoRead(id=uuid.uuid4(), content="メモ2", task_id=task_id),
        ]

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.get_all_memos.return_value = memos

        # Act
        result = memo_app_service.get_all_memos(query)

        # Assert
        assert result == memos
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        mock_memo_service.get_all_memos.assert_called_once()

    def test_get_memos_by_task_id_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """タスクIDでメモ取得のテスト（正常系）"""
        # Arrange
        task_id = uuid.uuid4()
        query = GetMemosByTaskIdQuery(task_id=task_id)
        memos = [
            MemoRead(id=uuid.uuid4(), content="タスクメモ1", task_id=task_id),
            MemoRead(id=uuid.uuid4(), content="タスクメモ2", task_id=task_id),
        ]

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.get_memos_by_task_id.return_value = memos

        # Act
        result = memo_app_service.get_memos_by_task_id(query)

        # Assert
        assert result == memos
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        mock_memo_service.get_memos_by_task_id.assert_called_once_with(task_id)

    def test_search_memos_success(
        self,
        memo_app_service: MemoApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """メモ検索のテスト（正常系）"""
        # Arrange
        search_query = "Python"
        query = SearchMemosQuery(query=search_query)
        task_id = uuid.uuid4()
        matching_memos = [
            MemoRead(id=uuid.uuid4(), content="Pythonプログラミング", task_id=task_id),
            MemoRead(id=uuid.uuid4(), content="Python学習メモ", task_id=task_id),
        ]

        # [AI GENERATED] モックの設定
        mock_memo_service = mock_unit_of_work.service_factory.create_memo_service.return_value
        mock_memo_service.search_memos.return_value = matching_memos

        # Act
        result = memo_app_service.search_memos(query)

        # Assert
        assert result == matching_memos
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        mock_memo_service.search_memos.assert_called_once_with(search_query)

    def test_search_memos_empty_query(
        self,
        memo_app_service: MemoApplicationService,
    ) -> None:
        """メモ検索のテスト（空のクエリ）"""
        # Arrange
        query = SearchMemosQuery(query="")

        # Act
        result = memo_app_service.search_memos(query)

        # Assert
        assert result == []

    def test_search_memos_whitespace_query(
        self,
        memo_app_service: MemoApplicationService,
    ) -> None:
        """メモ検索のテスト（空白のみのクエリ）"""
        # Arrange
        query = SearchMemosQuery(query="   ")

        # Act
        result = memo_app_service.search_memos(query)

        # Assert
        assert result == []
