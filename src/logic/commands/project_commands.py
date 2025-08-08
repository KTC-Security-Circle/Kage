"""プロジェクト関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import ProjectCreate, ProjectStatus, ProjectUpdate

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class CreateProjectCommand:
    """プロジェクト作成コマンド"""

    title: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.ACTIVE

    def to_project_create(self) -> ProjectCreate:
        """ProjectCreateモデルに変換

        Returns:
            ProjectCreate: モデル変換結果
        """
        return ProjectCreate(
            title=self.title,
            description=self.description,
            status=self.status,
        )


@dataclass
class UpdateProjectCommand:
    """プロジェクト更新コマンド"""

    project_id: UUID
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None

    def to_project_update(self) -> ProjectUpdate:
        """ProjectUpdateモデルに変換

        Returns:
            ProjectUpdate: モデル変換結果
        """
        return ProjectUpdate(
            title=self.title,
            description=self.description,
            status=self.status,
        )


@dataclass
class DeleteProjectCommand:
    """プロジェクト削除コマンド"""

    project_id: UUID


@dataclass
class UpdateProjectStatusCommand:
    """プロジェクトステータス更新コマンド"""

    project_id: UUID
    new_status: ProjectStatus

    def to_project_update(self) -> ProjectUpdate:
        """ProjectUpdateモデルに変換

        Returns:
            ProjectUpdate: モデル変換結果
        """
        return ProjectUpdate(status=self.new_status)
