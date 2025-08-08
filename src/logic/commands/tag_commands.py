"""タグ関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import TagCreate, TagUpdate

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class CreateTagCommand:
    """タグ作成コマンド"""

    name: str

    def to_tag_create(self) -> TagCreate:
        """TagCreateモデルに変換

        Returns:
            TagCreate: モデル変換結果
        """
        return TagCreate(name=self.name)


@dataclass
class UpdateTagCommand:
    """タグ更新コマンド"""

    tag_id: UUID
    name: str | None = None

    def to_tag_update(self) -> TagUpdate:
        """TagUpdateモデルに変換

        Returns:
            TagUpdate: モデル変換結果
        """
        return TagUpdate(name=self.name)


@dataclass
class DeleteTagCommand:
    """タグ削除コマンド"""

    tag_id: UUID
