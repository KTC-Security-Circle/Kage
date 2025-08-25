"""メモ関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import MemoCreate, MemoUpdate

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class CreateMemoCommand:
    """メモ作成コマンド"""

    content: str
    task_id: UUID

    def to_memo_create(self) -> MemoCreate:
        """MemoCreateモデルに変換

        Returns:
            MemoCreate: モデル変換結果
        """
        return MemoCreate(
            content=self.content,
            task_id=self.task_id,
        )


@dataclass
class UpdateMemoCommand:
    """メモ更新コマンド"""

    memo_id: UUID
    content: str

    def to_memo_update(self) -> MemoUpdate:
        """MemoUpdateモデルに変換

        Returns:
            MemoUpdate: モデル変換結果
        """
        return MemoUpdate(content=self.content)


@dataclass
class DeleteMemoCommand:
    """メモ削除コマンド"""

    memo_id: UUID
