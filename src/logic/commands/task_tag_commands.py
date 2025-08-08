"""タスクタグ関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import TaskTagCreate

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class CreateTaskTagCommand:
    """タスクタグ関連作成コマンド"""

    task_id: UUID
    tag_id: UUID

    def to_task_tag_create(self) -> TaskTagCreate:
        """TaskTagCreateモデルに変換

        Returns:
            TaskTagCreate: モデル変換結果
        """
        return TaskTagCreate(
            task_id=self.task_id,
            tag_id=self.tag_id,
        )


@dataclass
class DeleteTaskTagCommand:
    """タスクタグ関連削除コマンド"""

    task_id: UUID
    tag_id: UUID


@dataclass
class DeleteTaskTagsByTaskCommand:
    """タスクのすべてのタグ関連削除コマンド"""

    task_id: UUID


@dataclass
class DeleteTaskTagsByTagCommand:
    """タグのすべてのタスク関連削除コマンド"""

    tag_id: UUID
