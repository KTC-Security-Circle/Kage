"""メモ関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class GetMemoByIdQuery:
    """ID指定メモ取得クエリ"""

    memo_id: UUID


@dataclass
class GetAllMemosQuery:
    """全メモ取得クエリ"""


@dataclass
class GetMemosByTaskIdQuery:
    """タスクID指定メモ取得クエリ"""

    task_id: UUID


@dataclass
class SearchMemosQuery:
    """メモ検索クエリ"""

    query: str
