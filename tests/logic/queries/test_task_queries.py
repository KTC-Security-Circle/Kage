"""タスククエリテストモジュール

タスク関連のQuery DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.queries.task_queries import (
    GetAllTasksByStatusDictQuery,
    GetTaskByIdQuery,
    GetTasksByStatusQuery,
    GetTodayTasksCountQuery,
)
from models import TaskStatus


class TestGetTasksByStatusQuery:
    """GetTasksByStatusQueryのテストクラス"""

    def test_get_tasks_by_status_query(self) -> None:
        """GetTasksByStatusQueryを作成する"""
        # Arrange & Act
        query = GetTasksByStatusQuery(status=TaskStatus.INBOX)

        # Assert
        assert query.status == TaskStatus.INBOX

    def test_get_tasks_by_status_query_various_statuses(self) -> None:
        """様々なステータスでGetTasksByStatusQueryを作成する"""
        # Arrange
        statuses = [
            TaskStatus.INBOX,
            TaskStatus.NEXT_ACTION,
            TaskStatus.WAITING_FOR,
            TaskStatus.SOMEDAY_MAYBE,
            TaskStatus.DELEGATED,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ]

        for status in statuses:
            # Act
            query = GetTasksByStatusQuery(status=status)

            # Assert
            assert query.status == status


class TestGetTodayTasksCountQuery:
    """GetTodayTasksCountQueryのテストクラス"""

    def test_get_today_tasks_count_query(self) -> None:
        """GetTodayTasksCountQueryを作成する"""
        # Arrange & Act
        query = GetTodayTasksCountQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetTodayTasksCountQuery)


class TestGetTaskByIdQuery:
    """GetTaskByIdQueryのテストクラス"""

    def test_get_task_by_id_query(self) -> None:
        """GetTaskByIdQueryを作成する"""
        # Arrange
        task_id = uuid4()

        # Act
        query = GetTaskByIdQuery(task_id=task_id)

        # Assert
        assert query.task_id == task_id


class TestGetAllTasksByStatusDictQuery:
    """GetAllTasksByStatusDictQueryのテストクラス"""

    def test_get_all_tasks_by_status_dict_query(self) -> None:
        """GetAllTasksByStatusDictQueryを作成する"""
        # Arrange & Act
        query = GetAllTasksByStatusDictQuery()

        # Assert
        # [AI GENERATED] パラメータがないクエリなので、インスタンスが正常に作成されることを確認
        assert isinstance(query, GetAllTasksByStatusDictQuery)
