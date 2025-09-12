"""メモサービスのテスト"""

import uuid
from unittest.mock import Mock

import pytest

from logic.repositories.memo import MemoRepository
from logic.repositories.task import TaskRepository
from logic.services.memo_service import (
    MemoService,
    MemoServiceCheckError,
    MemoServiceCreateError,
    MemoServiceDeleteError,
    MemoServiceGetError,
    MemoServiceUpdateError,
)
from models import Memo, MemoCreate, MemoRead, MemoUpdate, Task
from tests.logic.helpers import create_test_task

EXPECTED_MEMO_PAIR_COUNT = 2


class TestMemoService:
    """MemoServiceのテストクラス"""

    @pytest.fixture
    def mock_memo_repo(self) -> Mock:
        """モックメモリポジトリ"""
        return Mock(spec=MemoRepository)

    @pytest.fixture
    def mock_task_repo(self) -> Mock:
        """モックタスクリポジトリ"""
        return Mock(spec=TaskRepository)

    @pytest.fixture
    def memo_service(self, mock_memo_repo: Mock, mock_task_repo: Mock) -> MemoService:
        """MemoServiceインスタンス"""
        return MemoService(mock_memo_repo, mock_task_repo)

    def test_create_memo_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ作成のテスト（正常系）"""
        # Arrange
        task = create_test_task()
        if task.id is None:
            pytest.fail("Task ID should not be None after creation")
        memo_data = MemoCreate(content="テスト用メモ", task_id=task.id)

        created_memo = Memo(
            id=uuid.uuid4(),
            content="テスト用メモ",
            task_id=task.id,
        )

        mock_task_repo.get_by_id.return_value = task
        mock_memo_repo.create.return_value = created_memo

        # Act
        result = memo_service.create_memo(memo_data)

        # Assert
        assert isinstance(result, MemoRead)
        assert result.content == "テスト用メモ"
        assert result.task_id == task.id
        mock_task_repo.get_by_id.assert_called_once_with(task.id)
        mock_memo_repo.create.assert_called_once_with(memo_data)

    def test_create_memo_task_not_found(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ作成のテスト（タスクが見つからない場合）"""
        # Arrange
        task_id = uuid.uuid4()
        memo_data = MemoCreate(content="テスト用メモ", task_id=task_id)

        mock_task_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MemoServiceCheckError, match=r"タスクID .* が見つかりません"):
            memo_service.create_memo(memo_data)

        mock_task_repo.get_by_id.assert_called_once_with(task_id)
        mock_memo_repo.create.assert_not_called()

    def test_create_memo_creation_failed(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ作成のテスト（作成に失敗した場合）"""
        # Arrange
        task = create_test_task()
        if task.id is None:
            pytest.fail("Task ID should not be None after creation")
        memo_data = MemoCreate(content="テスト用メモ", task_id=task.id)

        mock_task_repo.get_by_id.return_value = task
        mock_memo_repo.create.return_value = None

        # Act & Assert
        with pytest.raises(MemoServiceCreateError, match="メモの作成に失敗しました"):
            memo_service.create_memo(memo_data)

    def test_update_memo_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ更新のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()

        existing_memo = Memo(
            id=memo_id,
            content="更新前メモ",
            task_id=task_id,
        )

        updated_memo = Memo(
            id=memo_id,
            content="更新後メモ",
            task_id=task_id,
        )

        memo_data = MemoUpdate(content="更新後メモ")

        mock_memo_repo.get_by_id.return_value = existing_memo
        mock_memo_repo.update.return_value = updated_memo

        # Act
        result = memo_service.update_memo(memo_id, memo_data)

        # Assert
        assert isinstance(result, MemoRead)
        assert result.content == "更新後メモ"
        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)
        mock_memo_repo.update.assert_called_once_with(memo_id, memo_data)

    def test_update_memo_not_found(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ更新のテスト（メモが見つからない場合）"""
        # Arrange
        memo_id = uuid.uuid4()
        memo_data = MemoUpdate(content="更新後メモ")

        mock_memo_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MemoServiceCheckError, match=r"メモID .* が見つかりません"):
            memo_service.update_memo(memo_id, memo_data)

        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)
        mock_memo_repo.update.assert_not_called()

    def test_delete_memo_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ削除のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()

        existing_memo = Memo(
            id=memo_id,
            content="削除対象メモ",
            task_id=task_id,
        )

        mock_memo_repo.get_by_id.return_value = existing_memo
        mock_memo_repo.delete.return_value = True

        # Act
        result = memo_service.delete_memo(memo_id)

        # Assert
        assert result is True
        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)
        mock_memo_repo.delete.assert_called_once_with(memo_id)

    def test_delete_memo_not_found(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ削除のテスト（メモが見つからない場合）"""
        # Arrange
        memo_id = uuid.uuid4()

        mock_memo_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MemoServiceCheckError, match=r"メモID .* が見つかりません"):
            memo_service.delete_memo(memo_id)

        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)
        mock_memo_repo.delete.assert_not_called()

    def test_get_memo_by_id_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """IDでメモ取得のテスト（正常系）"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()

        memo = Memo(
            id=memo_id,
            content="取得テスト用メモ",
            task_id=task_id,
        )

        mock_memo_repo.get_by_id.return_value = memo

        # Act
        result = memo_service.get_memo_by_id(memo_id)

        # Assert
        assert isinstance(result, MemoRead)
        assert result.id == memo_id
        assert result.content == "取得テスト用メモ"
        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)

    def test_get_memo_by_id_not_found(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """IDでメモ取得のテスト（見つからない場合）"""
        # Arrange
        memo_id = uuid.uuid4()

        mock_memo_repo.get_by_id.return_value = None

        # Act
        result = memo_service.get_memo_by_id(memo_id)

        # Assert
        assert result is None
        mock_memo_repo.get_by_id.assert_called_once_with(memo_id)

    def test_get_all_memos_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """全メモ取得のテスト（正常系）"""
        # Arrange
        task_id = uuid.uuid4()
        memos = [
            Memo(id=uuid.uuid4(), content="メモ1", task_id=task_id),
            Memo(id=uuid.uuid4(), content="メモ2", task_id=task_id),
        ]

        mock_memo_repo.get_all.return_value = memos

        # Act
        result = memo_service.get_all_memos()

        # Assert
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        assert all(isinstance(memo, MemoRead) for memo in result)
        contents = [memo.content for memo in result]
        assert "メモ1" in contents
        assert "メモ2" in contents
        mock_memo_repo.get_all.assert_called_once()

    def test_get_memos_by_task_id_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """タスクIDでメモ取得のテスト（正常系）"""
        # Arrange
        task_id = uuid.uuid4()
        task = Task(id=task_id, title="テストタスク")
        memos = [
            Memo(id=uuid.uuid4(), content="タスクメモ1", task_id=task_id),
            Memo(id=uuid.uuid4(), content="タスクメモ2", task_id=task_id),
        ]

        mock_task_repo.get_by_id.return_value = task
        mock_memo_repo.get_by_task_id.return_value = memos

        # Act
        result = memo_service.get_memos_by_task_id(task_id)

        # Assert
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        assert all(isinstance(memo, MemoRead) for memo in result)
        contents = [memo.content for memo in result]
        assert "タスクメモ1" in contents
        assert "タスクメモ2" in contents
        mock_task_repo.get_by_id.assert_called_once_with(task_id)
        mock_memo_repo.get_by_task_id.assert_called_once_with(task_id)

    def test_get_memos_by_task_id_task_not_found(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """タスクIDでメモ取得のテスト（タスクが見つからない場合）"""
        # Arrange
        task_id = uuid.uuid4()

        mock_task_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MemoServiceCheckError, match=r"タスクID .* が見つかりません"):
            memo_service.get_memos_by_task_id(task_id)

        mock_task_repo.get_by_id.assert_called_once_with(task_id)
        mock_memo_repo.get_by_task_id.assert_not_called()

    def test_search_memos_success(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ検索のテスト（正常系）"""
        # Arrange
        search_query = "Python"
        task_id = uuid.uuid4()
        matching_memos = [
            Memo(id=uuid.uuid4(), content="Pythonプログラミング", task_id=task_id),
            Memo(id=uuid.uuid4(), content="Python学習メモ", task_id=task_id),
        ]

        mock_memo_repo.search_by_content.return_value = matching_memos

        # Act
        result = memo_service.search_memos(search_query)

        # Assert
        assert len(result) == EXPECTED_MEMO_PAIR_COUNT
        assert all(isinstance(memo, MemoRead) for memo in result)
        contents = [memo.content for memo in result]
        assert "Pythonプログラミング" in contents
        assert "Python学習メモ" in contents
        mock_memo_repo.search_by_content.assert_called_once_with(search_query)

    def test_search_memos_no_results(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ検索のテスト（結果なし）"""
        # Arrange
        search_query = "存在しないキーワード"

        mock_memo_repo.search_by_content.return_value = []

        # Act
        result = memo_service.search_memos(search_query)

        # Assert
        assert len(result) == 0
        mock_memo_repo.search_by_content.assert_called_once_with(search_query)

    def test_create_memo_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ作成時の例外処理テスト"""
        # Arrange
        task = create_test_task()
        if task.id is None:
            pytest.fail("Task ID should not be None after creation")
        memo_data = MemoCreate(content="テスト用メモ", task_id=task.id)

        mock_task_repo.get_by_id.return_value = task
        mock_memo_repo.create.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceCreateError, match="メモの作成に失敗しました"):
            memo_service.create_memo(memo_data)

    def test_update_memo_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ更新時の例外処理テスト"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()

        existing_memo = Memo(
            id=memo_id,
            content="更新前メモ",
            task_id=task_id,
        )

        memo_data = MemoUpdate(content="更新後メモ")

        mock_memo_repo.get_by_id.return_value = existing_memo
        mock_memo_repo.update.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceUpdateError, match="メモの更新に失敗しました"):
            memo_service.update_memo(memo_id, memo_data)

    def test_delete_memo_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ削除時の例外処理テスト"""
        # Arrange
        memo_id = uuid.uuid4()
        task_id = uuid.uuid4()

        existing_memo = Memo(
            id=memo_id,
            content="削除対象メモ",
            task_id=task_id,
        )

        mock_memo_repo.get_by_id.return_value = existing_memo
        mock_memo_repo.delete.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceDeleteError, match="メモの削除に失敗しました"):
            memo_service.delete_memo(memo_id)

    def test_get_memo_by_id_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ取得時の例外処理テスト"""
        # Arrange
        memo_id = uuid.uuid4()

        mock_memo_repo.get_by_id.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceGetError, match="メモの取得に失敗しました"):
            memo_service.get_memo_by_id(memo_id)

    def test_get_all_memos_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """全メモ取得時の例外処理テスト"""
        # Arrange
        mock_memo_repo.get_all.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceGetError, match="メモ一覧の取得に失敗しました"):
            memo_service.get_all_memos()

    def test_get_memos_by_task_id_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """タスクIDでメモ取得時の例外処理テスト"""
        # Arrange
        task_id = uuid.uuid4()
        task = Task(id=task_id, title="テストタスク")

        mock_task_repo.get_by_id.return_value = task
        mock_memo_repo.get_by_task_id.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceGetError, match="タスク別メモの取得に失敗しました"):
            memo_service.get_memos_by_task_id(task_id)

    def test_search_memos_exception_handling(
        self,
        memo_service: MemoService,
        mock_memo_repo: Mock,
        mock_task_repo: Mock,
    ) -> None:
        """メモ検索時の例外処理テスト"""
        # Arrange
        search_query = "Python"

        mock_memo_repo.search_by_content.side_effect = Exception("データベースエラー")

        # Act & Assert
        with pytest.raises(MemoServiceGetError, match="メモの検索に失敗しました"):
            memo_service.search_memos(search_query)
