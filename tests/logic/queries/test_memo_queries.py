"""メモクエリのテスト"""

import uuid

from logic.queries.memo_queries import (
    GetAllMemosQuery,
    GetMemoByIdQuery,
    GetMemosByTaskIdQuery,
    SearchMemosQuery,
)


class TestGetMemoByIdQuery:
    """GetMemoByIdQueryのテストクラス"""

    def test_get_memo_by_id_query_initialization(self) -> None:
        """GetMemoByIdQueryの初期化テスト"""
        # Arrange
        memo_id = uuid.uuid4()

        # Act
        query = GetMemoByIdQuery(memo_id=memo_id)

        # Assert
        assert query.memo_id == memo_id


class TestGetAllMemosQuery:
    """GetAllMemosQueryのテストクラス"""

    def test_get_all_memos_query_initialization(self) -> None:
        """GetAllMemosQueryの初期化テスト"""
        # Act
        query = GetAllMemosQuery()

        # Assert
        assert query is not None


class TestGetMemosByTaskIdQuery:
    """GetMemosByTaskIdQueryのテストクラス"""

    def test_get_memos_by_task_id_query_initialization(self) -> None:
        """GetMemosByTaskIdQueryの初期化テスト"""
        # Arrange
        task_id = uuid.uuid4()

        # Act
        query = GetMemosByTaskIdQuery(task_id=task_id)

        # Assert
        assert query.task_id == task_id


class TestSearchMemosQuery:
    """SearchMemosQueryのテストクラス"""

    def test_search_memos_query_initialization(self) -> None:
        """SearchMemosQueryの初期化テスト"""
        # Arrange
        search_query = "Python"

        # Act
        query = SearchMemosQuery(query=search_query)

        # Assert
        assert query.query == search_query
