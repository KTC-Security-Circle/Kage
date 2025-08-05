"""タグ関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class GetTagByIdQuery:
    """ID指定タグ取得クエリ"""

    tag_id: UUID


@dataclass
class GetAllTagsQuery:
    """全タグ取得クエリ"""


@dataclass
class GetTagByNameQuery:
    """名前指定タグ取得クエリ"""

    name: str


@dataclass
class SearchTagsByNameQuery:
    """名前検索タグ取得クエリ"""

    name_query: str


@dataclass
class CheckTagExistsByNameQuery:
    """名前によるタグ存在確認クエリ"""

    name: str
