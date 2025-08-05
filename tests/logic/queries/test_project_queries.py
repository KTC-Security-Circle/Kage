"""プロジェクトクエリテストモジュール

プロジェクト関連のQuery DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.queries.project_queries import (
    GetActiveProjectsQuery,
    GetAllProjectsQuery,
    GetCompletedProjectsQuery,
    GetProjectByIdQuery,
    GetProjectsByStatusQuery,
    SearchProjectsByTitleQuery,
)
from models import ProjectStatus


class TestGetProjectByIdQuery:
    """GetProjectByIdQueryのテストクラス"""

    def test_get_project_by_id_query(self) -> None:
        """GetProjectByIdQueryを作成する"""
        # Arrange
        project_id = uuid4()

        # Act
        query = GetProjectByIdQuery(project_id=project_id)

        # Assert
        assert query.project_id == project_id


class TestGetAllProjectsQuery:
    """GetAllProjectsQueryのテストクラス"""

    def test_get_all_projects_query(self) -> None:
        """GetAllProjectsQueryを作成する"""
        # Arrange & Act
        query = GetAllProjectsQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetAllProjectsQuery)


class TestGetProjectsByStatusQuery:
    """GetProjectsByStatusQueryのテストクラス"""

    def test_get_projects_by_status_query(self) -> None:
        """GetProjectsByStatusQueryを作成する"""
        # Arrange & Act
        query = GetProjectsByStatusQuery(status=ProjectStatus.ACTIVE)

        # Assert
        assert query.status == ProjectStatus.ACTIVE

    def test_get_projects_by_status_query_various_statuses(self) -> None:
        """様々なステータスでGetProjectsByStatusQueryを作成する"""
        # Arrange
        statuses = [
            ProjectStatus.ACTIVE,
            ProjectStatus.ON_HOLD,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ]

        for status in statuses:
            # Act
            query = GetProjectsByStatusQuery(status=status)

            # Assert
            assert query.status == status


class TestSearchProjectsByTitleQuery:
    """SearchProjectsByTitleQueryのテストクラス"""

    def test_search_projects_by_title_query(self) -> None:
        """SearchProjectsByTitleQueryを作成する"""
        # Arrange
        title_query = "テストプロジェクト"

        # Act
        query = SearchProjectsByTitleQuery(title_query=title_query)

        # Assert
        assert query.title_query == title_query

    def test_search_projects_by_title_query_empty_string(self) -> None:
        """空文字列でSearchProjectsByTitleQueryを作成する"""
        # Arrange
        title_query = ""

        # Act
        query = SearchProjectsByTitleQuery(title_query=title_query)

        # Assert
        assert query.title_query == ""

    def test_search_projects_by_title_query_partial_match(self) -> None:
        """部分一致用のSearchProjectsByTitleQueryを作成する"""
        # Arrange
        title_query = "プロジェクト"

        # Act
        query = SearchProjectsByTitleQuery(title_query=title_query)

        # Assert
        assert query.title_query == "プロジェクト"


class TestGetActiveProjectsQuery:
    """GetActiveProjectsQueryのテストクラス"""

    def test_get_active_projects_query(self) -> None:
        """GetActiveProjectsQueryを作成する"""
        # Arrange & Act
        query = GetActiveProjectsQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetActiveProjectsQuery)


class TestGetCompletedProjectsQuery:
    """GetCompletedProjectsQueryのテストクラス"""

    def test_get_completed_projects_query(self) -> None:
        """GetCompletedProjectsQueryを作成する"""
        # Arrange & Act
        query = GetCompletedProjectsQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetCompletedProjectsQuery)
