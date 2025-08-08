"""タスクタグコマンドテストモジュール

タスクタグ関連のCommand DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.commands.task_tag_commands import (
    CreateTaskTagCommand,
    DeleteTaskTagCommand,
    DeleteTaskTagsByTagCommand,
    DeleteTaskTagsByTaskCommand,
)


class TestCreateTaskTagCommand:
    """CreateTaskTagCommandのテストクラス"""

    def test_create_task_tag_command(self) -> None:
        """CreateTaskTagCommandを作成する"""
        # Arrange
        task_id = uuid4()
        tag_id = uuid4()

        # Act
        command = CreateTaskTagCommand(task_id=task_id, tag_id=tag_id)

        # Assert
        assert command.task_id == task_id
        assert command.tag_id == tag_id

    def test_to_task_tag_create(self) -> None:
        """CreateTaskTagCommandからTaskTagCreateに変換する"""
        # Arrange
        task_id = uuid4()
        tag_id = uuid4()
        command = CreateTaskTagCommand(task_id=task_id, tag_id=tag_id)

        # Act
        task_tag_create = command.to_task_tag_create()

        # Assert
        assert task_tag_create.task_id == task_id
        assert task_tag_create.tag_id == tag_id


class TestDeleteTaskTagCommand:
    """DeleteTaskTagCommandのテストクラス"""

    def test_delete_task_tag_command(self) -> None:
        """DeleteTaskTagCommandを作成する"""
        # Arrange
        task_id = uuid4()
        tag_id = uuid4()

        # Act
        command = DeleteTaskTagCommand(task_id=task_id, tag_id=tag_id)

        # Assert
        assert command.task_id == task_id
        assert command.tag_id == tag_id


class TestDeleteTaskTagsByTaskCommand:
    """DeleteTaskTagsByTaskCommandのテストクラス"""

    def test_delete_task_tags_by_task_command(self) -> None:
        """DeleteTaskTagsByTaskCommandを作成する"""
        # Arrange
        task_id = uuid4()

        # Act
        command = DeleteTaskTagsByTaskCommand(task_id=task_id)

        # Assert
        assert command.task_id == task_id


class TestDeleteTaskTagsByTagCommand:
    """DeleteTaskTagsByTagCommandのテストクラス"""

    def test_delete_task_tags_by_tag_command(self) -> None:
        """DeleteTaskTagsByTagCommandを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        command = DeleteTaskTagsByTagCommand(tag_id=tag_id)

        # Assert
        assert command.tag_id == tag_id
