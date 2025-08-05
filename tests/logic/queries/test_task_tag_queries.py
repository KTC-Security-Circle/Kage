"""タスクタグクエリテストモジュール

タスクタグ関連のQuery DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.queries.task_tag_queries import (
    CheckTaskTagExistsQuery,
    GetAllTaskTagsQuery,
    GetTaskTagByTaskAndTagQuery,
    GetTaskTagsByTagIdQuery,
    GetTaskTagsByTaskIdQuery,
)


class TestGetTaskTagsByTaskIdQuery:
    """GetTaskTagsByTaskIdQueryのテストクラス"""

    def test_get_task_tags_by_task_id_query(self) -> None:
        """GetTaskTagsByTaskIdQueryを作成する"""
        # Arrange
        task_id = uuid4()

        # Act
        query = GetTaskTagsByTaskIdQuery(task_id=task_id)

        # Assert
        assert query.task_id == task_id


class TestGetTaskTagsByTagIdQuery:
    """GetTaskTagsByTagIdQueryのテストクラス"""

    def test_get_task_tags_by_tag_id_query(self) -> None:
        """GetTaskTagsByTagIdQueryを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        query = GetTaskTagsByTagIdQuery(tag_id=tag_id)

        # Assert
        assert query.tag_id == tag_id


class TestGetTaskTagByTaskAndTagQuery:
    """GetTaskTagByTaskAndTagQueryのテストクラス"""

    def test_get_task_tag_by_task_and_tag_query(self) -> None:
        """GetTaskTagByTaskAndTagQueryを作成する"""
        # Arrange
        task_id = uuid4()
        tag_id = uuid4()

        # Act
        query = GetTaskTagByTaskAndTagQuery(task_id=task_id, tag_id=tag_id)

        # Assert
        assert query.task_id == task_id
        assert query.tag_id == tag_id


class TestCheckTaskTagExistsQuery:
    """CheckTaskTagExistsQueryのテストクラス"""

    def test_check_task_tag_exists_query(self) -> None:
        """CheckTaskTagExistsQueryを作成する"""
        # Arrange
        task_id = uuid4()
        tag_id = uuid4()

        # Act
        query = CheckTaskTagExistsQuery(task_id=task_id, tag_id=tag_id)

        # Assert
        assert query.task_id == task_id
        assert query.tag_id == tag_id


class TestGetAllTaskTagsQuery:
    """GetAllTaskTagsQueryのテストクラス"""

    def test_get_all_task_tags_query(self) -> None:
        """GetAllTaskTagsQueryを作成する"""
        # Arrange & Act
        query = GetAllTaskTagsQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetAllTaskTagsQuery)
