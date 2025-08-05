"""タスク関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import TaskCreate, TaskStatus, TaskUpdate

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID


@dataclass
class CreateTaskCommand:
    """タスク作成コマンド"""

    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.INBOX
    due_date: date | None = None

    def to_task_create(self) -> TaskCreate:
        """TaskCreateモデルに変換

        Returns:
            TaskCreate: モデル変換結果
        """
        return TaskCreate(
            title=self.title,
            description=self.description,
            status=self.status,
            due_date=self.due_date,
        )


@dataclass
class UpdateTaskCommand:
    """タスク更新コマンド"""

    task_id: UUID
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.INBOX
    due_date: date | None = None

    def to_task_update(self) -> TaskUpdate:
        """TaskUpdateモデルに変換

        Returns:
            TaskUpdate: モデル変換結果
        """
        return TaskUpdate(
            title=self.title,
            description=self.description,
            status=self.status,
            due_date=self.due_date,
        )


@dataclass
class DeleteTaskCommand:
    """タスク削除コマンド"""

    task_id: UUID


@dataclass
class UpdateTaskStatusCommand:
    """タスクステータス更新コマンド"""

    task_id: UUID
    new_status: TaskStatus
