"""Tags View Controller

ApplicationService を介してタグ・関連メモ/タスクを操作し、State を更新する。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from loguru import logger

from models import TagUpdate

from .utils import sort_tags_by_name

if TYPE_CHECKING:
    from datetime import datetime

if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from models import MemoRead, TagRead, TaskRead

    from .query import SearchQuery
    from .state import TagDict, TagsViewState


class TagApplicationPort(Protocol):
    """TagApplicationService の利用に必要なポート。"""

    def get_all_tags(self) -> list[TagRead]:  # pragma: no cover - interface
        """全タグを取得する。"""

    def search(self, query: str) -> list[TagRead]:  # pragma: no cover - interface
        """検索キーワードに一致したタグを返す。"""

    def create(
        self,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> TagRead:  # pragma: no cover - interface
        """タグを作成する。"""

    def update(self, tag_id: uuid.UUID, update_data: TagUpdate) -> TagRead:  # pragma: no cover - interface
        """タグを更新する。"""

    def delete(self, tag_id: uuid.UUID) -> bool:  # pragma: no cover - interface
        """タグを削除する。"""


class MemoApplicationPort(Protocol):
    """MemoApplicationService を抽象化するポート。"""

    def list_by_tag(
        self, tag_id: uuid.UUID, *, with_details: bool = False
    ) -> list[MemoRead]:  # pragma: no cover - interface
        """タグIDでメモ一覧を取得する。"""


class TaskApplicationPort(Protocol):
    """TaskApplicationService を抽象化するポート。"""

    def list_by_tag(
        self, tag_id: uuid.UUID, *, with_details: bool = False
    ) -> list[TaskRead]:  # pragma: no cover - interface
        """タグIDでタスク一覧を取得する。"""


@dataclass(slots=True)
class _TagUsageCacheEntry:
    """タグに紐づくメモ・タスクのキャッシュ。"""

    memos: list[MemoRead]
    tasks: list[TaskRead]


class TagsController:
    """Tags View の調停役。"""

    def __init__(
        self,
        state: TagsViewState,
        tag_service: TagApplicationPort,
        memo_service: MemoApplicationPort,
        task_service: TaskApplicationPort,
    ) -> None:
        self.state = state
        self._tag_service = tag_service
        self._memo_service = memo_service
        self._task_service = task_service
        self._usage_cache: dict[str, _TagUsageCacheEntry] = {}

    # ------------------------------------------------------------------
    # Initial Load / Refresh
    # ------------------------------------------------------------------
    def load_initial_tags(self) -> None:
        """初回ロード時にタグを取得する。"""
        if self.state.initial_loaded:
            return
        tags = self._tag_service.get_all_tags()
        self._usage_cache.clear()
        self._apply_tags(tags, preserve_selection=False)
        self.state.initial_loaded = True

    def refresh(self) -> None:
        """最新のタグを再取得する。"""
        tags = self._tag_service.get_all_tags()
        self._usage_cache.clear()
        self._apply_tags(tags, preserve_selection=True)

    # ------------------------------------------------------------------
    # Search / Select
    # ------------------------------------------------------------------
    def update_search(self, query: SearchQuery) -> None:
        """検索文字列を更新する。"""
        self.state.search_text = query.normalized

    def select_tag(self, tag_id: str) -> None:
        """指定タグを選択する。"""
        if any(tag["id"] == tag_id for tag in self.state.items):
            self.state.selected_id = tag_id

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def create_tag(self, name: str, color: str | None = None, description: str | None = None) -> TagDict:
        """タグを新規作成し状態に反映する。"""
        normalized_description = description.strip() if description else None
        normalized_color = color.strip() if color else None
        created = self._tag_service.create(name, normalized_description, normalized_color)
        created_dict = self._serialize_tag(created)
        self.state.items = sort_tags_by_name([*self.state.items, created_dict])
        self.state.selected_id = created_dict["id"]
        self._usage_cache[created_dict["id"]] = _TagUsageCacheEntry(memos=[], tasks=[])
        return created_dict

    def update_tag(
        self,
        tag_id: str,
        *,
        name: str | None = None,
        color: str | None = None,
        description: str | None = None,
    ) -> TagDict:
        """タグ情報を更新し State を同期する。"""
        tag_uuid = self._to_uuid(tag_id)
        update_data = TagUpdate(
            name=name.strip() if name is not None else None,
            color=color.strip() if color is not None else None,
            description=description.strip() if description is not None else None,
        )
        updated = self._tag_service.update(tag_uuid, update_data)
        updated_dict = self._serialize_tag(updated)
        self.state.items = sort_tags_by_name([updated_dict if tag["id"] == tag_id else tag for tag in self.state.items])
        self.state.selected_id = tag_id
        self._reset_usage_cache(tag_id)
        return updated_dict

    def delete_tag(self, tag_id: str) -> bool:
        """タグを削除し状態へ反映する。"""
        tag_uuid = self._to_uuid(tag_id)
        success = self._tag_service.delete(tag_uuid)
        if not success:
            return False
        self.state.items = [tag for tag in self.state.items if tag["id"] != tag_id]
        self.state.reconcile_after_delete()
        self._reset_usage_cache(tag_id)
        return True

    # ------------------------------------------------------------------
    # Related Data
    # ------------------------------------------------------------------
    def get_related_memos(self, tag_id: str) -> list[dict[str, str]]:
        """タグに紐づくメモを取得する。"""
        usage = self._ensure_usage(tag_id)
        related: list[dict[str, str]] = []
        for memo in usage.memos:
            memo_id = getattr(memo, "id", None)
            related.append(
                {
                    "id": str(memo_id) if memo_id else "",
                    "title": getattr(memo, "title", "") or "(無題のメモ)",
                    "description": getattr(memo, "content", "") or "",
                }
            )
        return related

    def get_related_tasks(self, tag_id: str) -> list[dict[str, str]]:
        """タグに紐づくタスクを取得する。"""
        usage = self._ensure_usage(tag_id)
        related: list[dict[str, str]] = []
        for task in usage.tasks:
            task_id = getattr(task, "id", None)
            status = getattr(task, "status", None)
            status_value = getattr(status, "value", str(status)) if status else ""
            related.append(
                {
                    "id": str(task_id) if task_id else "",
                    "title": getattr(task, "title", "") or "(無題のタスク)",
                    "description": getattr(task, "description", "") or "",
                    "status": status_value,
                }
            )
        return related

    def get_tag_counts(self, tag_id: str) -> dict[str, int]:
        """タグに紐づくメモ/タスク件数を返す。"""
        usage = self._ensure_usage(tag_id)
        memo_count = len(usage.memos)
        task_count = len(usage.tasks)
        return {
            "memo_count": memo_count,
            "task_count": task_count,
            "total_count": memo_count + task_count,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _apply_tags(self, tags: list[TagRead], *, preserve_selection: bool) -> None:
        serialized = sort_tags_by_name([self._serialize_tag(tag) for tag in tags])
        previous_selection = self.state.selected_id if preserve_selection else None
        self.state.items = serialized
        if previous_selection and any(tag["id"] == previous_selection for tag in serialized):
            self.state.selected_id = previous_selection
        elif not serialized:
            self.state.selected_id = None

    def _serialize_tag(self, tag: TagRead) -> TagDict:
        tag_id = getattr(tag, "id", None)
        name = getattr(tag, "name", "")
        description = getattr(tag, "description", "") or ""
        color = getattr(tag, "color", None) or "#607d8b"
        created_at = self._format_datetime(getattr(tag, "created_at", None))
        updated_at = self._format_datetime(getattr(tag, "updated_at", None))
        if tag_id is None:
            msg = "タグIDが取得できませんでした。"
            logger.warning(msg)
            generated = uuid.uuid4()
            tag_id = generated
        return {
            "id": str(tag_id),
            "name": name,
            "color": color,
            "description": description,
            "created_at": created_at,
            "updated_at": updated_at,
        }

    def _ensure_usage(self, tag_id: str) -> _TagUsageCacheEntry:
        cached = self._usage_cache.get(tag_id)
        if cached is not None:
            return cached
        tag_uuid = self._to_uuid(tag_id)
        memos = self._memo_service.list_by_tag(tag_uuid, with_details=False)
        tasks = self._task_service.list_by_tag(tag_uuid, with_details=False)
        entry = _TagUsageCacheEntry(memos=memos, tasks=tasks)
        self._usage_cache[tag_id] = entry
        return entry

    def _reset_usage_cache(self, tag_id: str | None = None) -> None:
        if tag_id is None:
            self._usage_cache.clear()
        else:
            self._usage_cache.pop(tag_id, None)

    def _format_datetime(self, value: datetime | str | None) -> str:
        if value is None:
            return "-"
        if isinstance(value, str):
            return value
        return value.replace(microsecond=0).isoformat(sep=" ")

    def _to_uuid(self, tag_id: str) -> uuid.UUID:
        try:
            return uuid.UUID(tag_id)
        except (ValueError, TypeError) as exc:  # pragma: no cover - バリデーション
            msg = f"不正なタグIDです: {tag_id}"
            raise ValueError(msg) from exc
