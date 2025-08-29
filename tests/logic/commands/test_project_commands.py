"""プロジェクトコマンドテストモジュール

プロジェクト関連のCommand DTOsのテストコード
"""

from __future__ import annotations

from uuid import uuid4

from logic.commands.project_commands import (
    CreateProjectCommand,
    DeleteProjectCommand,
    UpdateProjectCommand,
    UpdateProjectStatusCommand,
)
from models import ProjectStatus


class TestCreateProjectCommand:
    """CreateProjectCommandのテストクラス"""

    def test_create_project_command_minimal(self) -> None:
        """最小限の引数でCreateProjectCommandを作成する"""
        # Arrange & Act
        command = CreateProjectCommand(title="Test Project")

        # Assert
        assert command.title == "Test Project"
        assert command.description == ""
        assert command.status == ProjectStatus.ACTIVE

    def test_create_project_command_full(self) -> None:
        """全ての引数を指定してCreateProjectCommandを作成する"""
        # Arrange & Act
        command = CreateProjectCommand(
            title="Full Project",
            description="詳細な説明",
            status=ProjectStatus.ON_HOLD,
        )

        # Assert
        assert command.title == "Full Project"
        assert command.description == "詳細な説明"
        assert command.status == ProjectStatus.ON_HOLD

    def test_to_project_create_minimal(self) -> None:
        """最小限のCreateProjectCommandからProjectCreateに変換する"""
        # Arrange
        command = CreateProjectCommand(title="Test Project")

        # Act
        project_create = command.to_project_create()

        # Assert
        assert project_create.title == "Test Project"
        assert project_create.description == ""
        assert project_create.status == ProjectStatus.ACTIVE

    def test_to_project_create_full(self) -> None:
        """完全なCreateProjectCommandからProjectCreateに変換する"""
        # Arrange
        command = CreateProjectCommand(
            title="Full Project",
            description="詳細な説明",
            status=ProjectStatus.ON_HOLD,
        )

        # Act
        project_create = command.to_project_create()

        # Assert
        assert project_create.title == "Full Project"
        assert project_create.description == "詳細な説明"
        assert project_create.status == ProjectStatus.ON_HOLD


class TestUpdateProjectCommand:
    """UpdateProjectCommandのテストクラス"""

    def test_update_project_command_minimal(self) -> None:
        """最小限の引数でUpdateProjectCommandを作成する"""
        # Arrange
        project_id = uuid4()

        # Act
        command = UpdateProjectCommand(project_id=project_id)

        # Assert
        assert command.project_id == project_id
        assert command.title is None
        assert command.description is None
        assert command.status is None

    def test_update_project_command_partial(self) -> None:
        """部分的な更新でUpdateProjectCommandを作成する"""
        # Arrange
        project_id = uuid4()

        # Act
        command = UpdateProjectCommand(
            project_id=project_id,
            title="Updated Project",
        )

        # Assert
        assert command.project_id == project_id
        assert command.title == "Updated Project"
        assert command.description is None
        assert command.status is None

    def test_update_project_command_full(self) -> None:
        """全ての引数を指定してUpdateProjectCommandを作成する"""
        # Arrange
        project_id = uuid4()

        # Act
        command = UpdateProjectCommand(
            project_id=project_id,
            title="Updated Full Project",
            description="更新された詳細な説明",
            status=ProjectStatus.COMPLETED,
        )

        # Assert
        assert command.project_id == project_id
        assert command.title == "Updated Full Project"
        assert command.description == "更新された詳細な説明"
        assert command.status == ProjectStatus.COMPLETED

    def test_to_project_update_minimal(self) -> None:
        """最小限のUpdateProjectCommandからProjectUpdateに変換する"""
        # Arrange
        project_id = uuid4()
        command = UpdateProjectCommand(project_id=project_id)

        # Act
        project_update = command.to_project_update()

        # Assert
        assert project_update.title is None
        assert project_update.description is None
        assert project_update.status is None

    def test_to_project_update_full(self) -> None:
        """完全なUpdateProjectCommandからProjectUpdateに変換する"""
        # Arrange
        project_id = uuid4()
        command = UpdateProjectCommand(
            project_id=project_id,
            title="Updated Full Project",
            description="更新された詳細な説明",
            status=ProjectStatus.COMPLETED,
        )

        # Act
        project_update = command.to_project_update()

        # Assert
        assert project_update.title == "Updated Full Project"
        assert project_update.description == "更新された詳細な説明"
        assert project_update.status == ProjectStatus.COMPLETED


class TestDeleteProjectCommand:
    """DeleteProjectCommandのテストクラス"""

    def test_delete_project_command(self) -> None:
        """DeleteProjectCommandを作成する"""
        # Arrange
        project_id = uuid4()

        # Act
        command = DeleteProjectCommand(project_id=project_id)

        # Assert
        assert command.project_id == project_id


class TestUpdateProjectStatusCommand:
    """UpdateProjectStatusCommandのテストクラス"""

    def test_update_project_status_command(self) -> None:
        """UpdateProjectStatusCommandを作成する"""
        # Arrange
        project_id = uuid4()
        new_status = ProjectStatus.COMPLETED

        # Act
        command = UpdateProjectStatusCommand(project_id=project_id, new_status=new_status)

        # Assert
        assert command.project_id == project_id
        assert command.new_status == new_status

    def test_update_project_status_command_various_statuses(self) -> None:
        """様々なステータスでUpdateProjectStatusCommandを作成する"""
        # Arrange
        project_id = uuid4()
        statuses = [
            ProjectStatus.ACTIVE,
            ProjectStatus.ON_HOLD,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ]

        for status in statuses:
            # Act
            command = UpdateProjectStatusCommand(project_id=project_id, new_status=status)

            # Assert
            assert command.project_id == project_id
            assert command.new_status == status

    def test_to_project_update(self) -> None:
        """UpdateProjectStatusCommandからProjectUpdateに変換する"""
        # Arrange
        project_id = uuid4()
        new_status = ProjectStatus.COMPLETED
        command = UpdateProjectStatusCommand(project_id=project_id, new_status=new_status)

        # Act
        project_update = command.to_project_update()

        # Assert
        assert project_update.status == new_status
