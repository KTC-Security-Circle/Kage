"""メモコマンドのテスト"""

import uuid

from logic.commands.memo_commands import CreateMemoCommand, DeleteMemoCommand, UpdateMemoCommand
from models import MemoCreate, MemoUpdate


class TestCreateMemoCommand:
    """CreateMemoCommandのテストクラス"""

    def test_create_memo_command_initialization(self) -> None:
        """CreateMemoCommandの初期化テスト"""
        # Arrange
        content = "テスト用メモ内容"
        task_id = uuid.uuid4()

        # Act
        command = CreateMemoCommand(content=content, task_id=task_id)

        # Assert
        assert command.content == content
        assert command.task_id == task_id

    def test_to_memo_create(self) -> None:
        """to_memo_createメソッドのテスト"""
        # Arrange
        content = "テスト用メモ内容"
        task_id = uuid.uuid4()
        command = CreateMemoCommand(content=content, task_id=task_id)

        # Act
        memo_create = command.to_memo_create()

        # Assert
        assert isinstance(memo_create, MemoCreate)
        assert memo_create.content == content
        assert memo_create.task_id == task_id


class TestUpdateMemoCommand:
    """UpdateMemoCommandのテストクラス"""

    def test_update_memo_command_initialization(self) -> None:
        """UpdateMemoCommandの初期化テスト"""
        # Arrange
        memo_id = uuid.uuid4()
        content = "更新後のメモ内容"

        # Act
        command = UpdateMemoCommand(memo_id=memo_id, content=content)

        # Assert
        assert command.memo_id == memo_id
        assert command.content == content

    def test_to_memo_update(self) -> None:
        """to_memo_updateメソッドのテスト"""
        # Arrange
        memo_id = uuid.uuid4()
        content = "更新後のメモ内容"
        command = UpdateMemoCommand(memo_id=memo_id, content=content)

        # Act
        memo_update = command.to_memo_update()

        # Assert
        assert isinstance(memo_update, MemoUpdate)
        assert memo_update.content == content


class TestDeleteMemoCommand:
    """DeleteMemoCommandのテストクラス"""

    def test_delete_memo_command_initialization(self) -> None:
        """DeleteMemoCommandの初期化テスト"""
        # Arrange
        memo_id = uuid.uuid4()

        # Act
        command = DeleteMemoCommand(memo_id=memo_id)

        # Assert
        assert command.memo_id == memo_id