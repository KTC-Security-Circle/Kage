"""タスク関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from models import TaskStatus


@dataclass
class GetTasksByStatusQuery:
    """ステータス別タスク取得クエリ"""

    status: TaskStatus


@dataclass
class GetTodayTasksCountQuery:
    """今日のタスク件数取得クエリ"""


@dataclass
class GetTaskByIdQuery:
    """ID指定タスク取得クエリ"""

    task_id: UUID


@dataclass
class GetAllTasksByStatusDictQuery:
    """全ステータス別タスク取得クエリ"""
