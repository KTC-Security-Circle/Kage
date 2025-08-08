"""タグコマンドテストモジュール

タグ関連のCommand DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.commands.tag_commands import (
    CreateTagCommand,
    DeleteTagCommand,
    UpdateTagCommand,
)


class TestCreateTagCommand:
    """CreateTagCommandのテストクラス"""

    def test_create_tag_command(self) -> None:
        """CreateTagCommandを作成する"""
        # Arrange & Act
        command = CreateTagCommand(name="Test Tag")

        # Assert
        assert command.name == "Test Tag"

    def test_create_tag_command_japanese(self) -> None:
        """日本語名でCreateTagCommandを作成する"""
        # Arrange & Act
        command = CreateTagCommand(name="テストタグ")

        # Assert
        assert command.name == "テストタグ"

    def test_create_tag_command_empty_string(self) -> None:
        """空文字列でCreateTagCommandを作成する"""
        # Arrange & Act
        command = CreateTagCommand(name="")

        # Assert
        assert command.name == ""

    def test_to_tag_create(self) -> None:
        """CreateTagCommandからTagCreateに変換する"""
        # Arrange
        command = CreateTagCommand(name="Test Tag")

        # Act
        tag_create = command.to_tag_create()

        # Assert
        assert tag_create.name == "Test Tag"

    def test_to_tag_create_japanese(self) -> None:
        """日本語名のCreateTagCommandからTagCreateに変換する"""
        # Arrange
        command = CreateTagCommand(name="テストタグ")

        # Act
        tag_create = command.to_tag_create()

        # Assert
        assert tag_create.name == "テストタグ"


class TestUpdateTagCommand:
    """UpdateTagCommandのテストクラス"""

    def test_update_tag_command_minimal(self) -> None:
        """最小限の引数でUpdateTagCommandを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        command = UpdateTagCommand(tag_id=tag_id)

        # Assert
        assert command.tag_id == tag_id
        assert command.name is None

    def test_update_tag_command_with_name(self) -> None:
        """名前を指定してUpdateTagCommandを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        command = UpdateTagCommand(tag_id=tag_id, name="Updated Tag")

        # Assert
        assert command.tag_id == tag_id
        assert command.name == "Updated Tag"

    def test_to_tag_update_minimal(self) -> None:
        """最小限のUpdateTagCommandからTagUpdateに変換する"""
        # Arrange
        tag_id = uuid4()
        command = UpdateTagCommand(tag_id=tag_id)

        # Act
        tag_update = command.to_tag_update()

        # Assert
        assert tag_update.name is None

    def test_to_tag_update_with_name(self) -> None:
        """名前付きのUpdateTagCommandからTagUpdateに変換する"""
        # Arrange
        tag_id = uuid4()
        command = UpdateTagCommand(tag_id=tag_id, name="Updated Tag")

        # Act
        tag_update = command.to_tag_update()

        # Assert
        assert tag_update.name == "Updated Tag"


class TestDeleteTagCommand:
    """DeleteTagCommandのテストクラス"""

    def test_delete_tag_command(self) -> None:
        """DeleteTagCommandを作成する"""
        # Arrange
        tag_id = uuid4()

        # Act
        command = DeleteTagCommand(tag_id=tag_id)

        # Assert
        assert command.tag_id == tag_id
