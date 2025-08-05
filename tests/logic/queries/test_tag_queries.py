"""タグクエリテストモジュール

タグ関連のQuery DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.queries.tag_queries import (
    CheckTagExistsByNameQuery,
    GetAllTagsQuery,
    GetTagByIdQuery,
    GetTagByNameQuery,
    SearchTagsByNameQuery,
)


class TestGetTagByIdQuery:
    """GetTagByIdQueryのテストクラス"""

    def test_get_tag_by_id_query(self) -> None:
        """GetTagByIdQueryを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        query = GetTagByIdQuery(tag_id=tag_id)

        # Assert
        assert query.tag_id == tag_id


class TestGetAllTagsQuery:
    """GetAllTagsQueryのテストクラス"""

    def test_get_all_tags_query(self) -> None:
        """GetAllTagsQueryを作成する"""
        # Arrange & Act
        query = GetAllTagsQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetAllTagsQuery)


class TestGetTagByNameQuery:
    """GetTagByNameQueryのテストクラス"""

    def test_get_tag_by_name_query(self) -> None:
        """GetTagByNameQueryを作成する"""
        # Arrange & Act
        query = GetTagByNameQuery(name="Test Tag")

        # Assert
        assert query.name == "Test Tag"

    def test_get_tag_by_name_query_japanese(self) -> None:
        """日本語名でGetTagByNameQueryを作成する"""
        # Arrange & Act
        query = GetTagByNameQuery(name="テストタグ")

        # Assert
        assert query.name == "テストタグ"

    def test_get_tag_by_name_query_empty_string(self) -> None:
        """空文字列でGetTagByNameQueryを作成する"""
        # Arrange & Act
        query = GetTagByNameQuery(name="")

        # Assert
        assert query.name == ""


class TestSearchTagsByNameQuery:
    """SearchTagsByNameQueryのテストクラス"""

    def test_search_tags_by_name_query(self) -> None:
        """SearchTagsByNameQueryを作成する"""
        # Arrange & Act
        query = SearchTagsByNameQuery(name_query="Test")

        # Assert
        assert query.name_query == "Test"

    def test_search_tags_by_name_query_japanese(self) -> None:
        """日本語でSearchTagsByNameQueryを作成する"""
        # Arrange & Act
        query = SearchTagsByNameQuery(name_query="テスト")

        # Assert
        assert query.name_query == "テスト"

    def test_search_tags_by_name_query_empty_string(self) -> None:
        """空文字列でSearchTagsByNameQueryを作成する"""
        # Arrange & Act
        query = SearchTagsByNameQuery(name_query="")

        # Assert
        assert query.name_query == ""

    def test_search_tags_by_name_query_partial_match(self) -> None:
        """部分一致用のSearchTagsByNameQueryを作成する"""
        # Arrange & Act
        query = SearchTagsByNameQuery(name_query="タグ")

        # Assert
        assert query.name_query == "タグ"


class TestCheckTagExistsByNameQuery:
    """CheckTagExistsByNameQueryのテストクラス"""

    def test_check_tag_exists_by_name_query(self) -> None:
        """CheckTagExistsByNameQueryを作成する"""
        # Arrange & Act
        query = CheckTagExistsByNameQuery(name="Test Tag")

        # Assert
        assert query.name == "Test Tag"

    def test_check_tag_exists_by_name_query_japanese(self) -> None:
        """日本語名でCheckTagExistsByNameQueryを作成する"""
        # Arrange & Act
        query = CheckTagExistsByNameQuery(name="テストタグ")

        # Assert
        assert query.name == "テストタグ"

    def test_check_tag_exists_by_name_query_empty_string(self) -> None:
        """空文字列でCheckTagExistsByNameQueryを作成する"""
        # Arrange & Act
        query = CheckTagExistsByNameQuery(name="")

        # Assert
        assert query.name == ""
