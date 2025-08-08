"""プロジェクト関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from models import ProjectStatus


@dataclass
class GetProjectByIdQuery:
    """ID指定プロジェクト取得クエリ"""

    project_id: UUID


@dataclass
class GetAllProjectsQuery:
    """全プロジェクト取得クエリ"""


@dataclass
class GetProjectsByStatusQuery:
    """ステータス別プロジェクト取得クエリ"""

    status: ProjectStatus


@dataclass
class SearchProjectsByTitleQuery:
    """タイトル検索プロジェクト取得クエリ"""

    title_query: str


@dataclass
class GetActiveProjectsQuery:
    """アクティブプロジェクト取得クエリ"""


@dataclass
class GetCompletedProjectsQuery:
    """完了プロジェクト取得クエリ"""
