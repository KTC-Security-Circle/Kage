"""タスクコマンドテストモジュール

タスク関連のCommand DTOsのテストコード
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from logic.commands.task_commands import (
    CreateTaskCommand,
    DeleteTaskCommand,
    UpdateTaskCommand,
    UpdateTaskStatusCommand,
)
from models import TaskStatus


class TestCreateTaskCommand:
    """CreateTaskCommandのテストクラス"""

    def test_create_task_command_minimal(self) -> None:
        """最小限の引数でCreateTaskCommandを作成する"""
        # Arrange & Act
        command = CreateTaskCommand(title="Test Task")

        # Assert
        assert command.title == "Test Task"
        assert command.description == ""
        assert command.status == TaskStatus.INBOX
        assert command.due_date is None

    def test_create_task_command_full(self) -> None:
        """全ての引数を指定してCreateTaskCommandを作成する"""
        # Arrange
        due_date = datetime.now(tz=UTC).date() + timedelta(days=1)

        # Act
        command = CreateTaskCommand(
            title="Full Task",
            description="詳細な説明",
            status=TaskStatus.NEXT_ACTION,
            due_date=due_date,
        )

        # Assert
        assert command.title == "Full Task"
        assert command.description == "詳細な説明"
        assert command.status == TaskStatus.NEXT_ACTION
        assert command.due_date == due_date

    def test_to_task_create_minimal(self) -> None:
        """最小限のCreateTaskCommandからTaskCreateに変換する"""
        # Arrange
        command = CreateTaskCommand(title="Test Task")

        # Act
        task_create = command.to_task_create()

        # Assert
        assert task_create.title == "Test Task"
        assert task_create.description == ""
        assert task_create.status == TaskStatus.INBOX
        assert task_create.due_date is None

    def test_to_task_create_full(self) -> None:
        """完全なCreateTaskCommandからTaskCreateに変換する"""
        # Arrange
        due_date = datetime.now(tz=UTC).date() + timedelta(days=1)
        command = CreateTaskCommand(
            title="Full Task",
            description="詳細な説明",
            status=TaskStatus.NEXT_ACTION,
            due_date=due_date,
        )

        # Act
        task_create = command.to_task_create()

        # Assert
        assert task_create.title == "Full Task"
        assert task_create.description == "詳細な説明"
        assert task_create.status == TaskStatus.NEXT_ACTION
        assert task_create.due_date == due_date


class TestUpdateTaskCommand:
    """UpdateTaskCommandのテストクラス"""

    def test_update_task_command_minimal(self) -> None:
        """最小限の引数でUpdateTaskCommandを作成する"""
        # Arrange
        task_id = uuid4()

        # Act
        command = UpdateTaskCommand(task_id=task_id, title="Updated Task")

        # Assert
        assert command.task_id == task_id
        assert command.title == "Updated Task"
        assert command.description == ""
        assert command.status == TaskStatus.INBOX
        assert command.due_date is None

    def test_update_task_command_full(self) -> None:
        """全ての引数を指定してUpdateTaskCommandを作成する"""
        # Arrange
        task_id = uuid4()
        due_date = datetime.now(tz=UTC).date() + timedelta(days=2)

        # Act
        command = UpdateTaskCommand(
            task_id=task_id,
            title="Updated Full Task",
            description="更新された詳細な説明",
            status=TaskStatus.COMPLETED,
            due_date=due_date,
        )

        # Assert
        assert command.task_id == task_id
        assert command.title == "Updated Full Task"
        assert command.description == "更新された詳細な説明"
        assert command.status == TaskStatus.COMPLETED
        assert command.due_date == due_date

    def test_to_task_update_minimal(self) -> None:
        """最小限のUpdateTaskCommandからTaskUpdateに変換する"""
        # Arrange
        task_id = uuid4()
        command = UpdateTaskCommand(task_id=task_id, title="Updated Task")

        # Act
        task_update = command.to_task_update()

        # Assert
        assert task_update.title == "Updated Task"
        assert task_update.description == ""
        assert task_update.status == TaskStatus.INBOX
        assert task_update.due_date is None

    def test_to_task_update_full(self) -> None:
        """完全なUpdateTaskCommandからTaskUpdateに変換する"""
        # Arrange
        task_id = uuid4()
        due_date = datetime.now(tz=UTC).date() + timedelta(days=2)
        command = UpdateTaskCommand(
            task_id=task_id,
            title="Updated Full Task",
            description="更新された詳細な説明",
            status=TaskStatus.COMPLETED,
            due_date=due_date,
        )

        # Act
        task_update = command.to_task_update()

        # Assert
        assert task_update.title == "Updated Full Task"
        assert task_update.description == "更新された詳細な説明"
        assert task_update.status == TaskStatus.COMPLETED
        assert task_update.due_date == due_date


class TestDeleteTaskCommand:
    """DeleteTaskCommandのテストクラス"""

    def test_delete_task_command(self) -> None:
        """DeleteTaskCommandを作成する"""
        # Arrange
        task_id = uuid4()

        # Act
        command = DeleteTaskCommand(task_id=task_id)

        # Assert
        assert command.task_id == task_id


class TestUpdateTaskStatusCommand:
    """UpdateTaskStatusCommandのテストクラス"""

    def test_update_task_status_command(self) -> None:
        """UpdateTaskStatusCommandを作成する"""
        # Arrange
        task_id = uuid4()
        new_status = TaskStatus.COMPLETED

        # Act
        command = UpdateTaskStatusCommand(task_id=task_id, new_status=new_status)

        # Assert
        assert command.task_id == task_id
        assert command.new_status == new_status

    def test_update_task_status_command_various_statuses(self) -> None:
        """様々なステータスでUpdateTaskStatusCommandを作成する"""
        # Arrange
        task_id = uuid4()
        statuses = [
            TaskStatus.INBOX,
            TaskStatus.NEXT_ACTION,
            TaskStatus.COMPLETED,
            TaskStatus.SOMEDAY_MAYBE,
        ]

        for status in statuses:
            # Act
            command = UpdateTaskStatusCommand(task_id=task_id, new_status=status)

            # Assert
            assert command.task_id == task_id
            assert command.new_status == status
