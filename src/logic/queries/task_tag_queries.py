"""タスクタグ関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class GetTaskTagsByTaskIdQuery:
    """タスクID指定でタスクタグ関連取得クエリ"""

    task_id: UUID


@dataclass
class GetTaskTagsByTagIdQuery:
    """タグID指定でタスクタグ関連取得クエリ"""

    tag_id: UUID


@dataclass
class GetTaskTagByTaskAndTagQuery:
    """タスクIDとタグIDでタスクタグ関連取得クエリ"""

    task_id: UUID
    tag_id: UUID


@dataclass
class CheckTaskTagExistsQuery:
    """タスクタグ関連存在確認クエリ"""

    task_id: UUID
    tag_id: UUID


@dataclass
class GetAllTaskTagsQuery:
    """全タスクタグ関連取得クエリ"""
