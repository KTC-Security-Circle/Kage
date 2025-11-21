"""Tasks Query Abstraction.

CQRS の Query 側。テスト容易性のため InMemory 実装を同梱。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from models import TaskRead

    from .controller import TaskApplicationPort


class TasksQuery(Protocol):
    """タスク取得用ポートインターフェース。"""

    def list_items(self, keyword: str, status: str | None) -> list[dict]:
        """タスク一覧を返す。

        Args:
            keyword: タイトル検索用キーワード（小文字で部分一致）
            status: フィルタするステータス（todo/progress/completed）
        Returns:
            タスク辞書のリスト
        """
        ...

    # TODO: ページネーションや無限スクロールに対応するためのインターフェースを拡張する。
    #       例: list_items_paged(keyword, status, *, offset, limit) -> PagedResult。
    # TODO: MVC化で永続層(Repository/Service)と接続。SQLModel/ORM連携やN+1対策、
    #       キャッシュ戦略 (LRU/TTL) の導入。I/O 例外に対するリトライ/フォールバック方針を決める。


@dataclass(slots=True)
class InMemoryTasksQuery:
    """軽量なインメモリ実装（プロトタイピング / テスト用）。"""

    data: list[dict]

    def list_items(self, keyword: str, status: str | None) -> list[dict]:
        items = self.data
        if keyword:
            k = keyword.lower()
            items = [x for x in items if k in str(x.get("title", "")).lower()]
        if status:
            items = [x for x in items if x.get("status") == status]
        return list(items)

    # 暫定: ステータス更新（Query 層での変更は本来は Command 層）
    def update_item_status(self, task_id: str, new_status: str) -> None:
        for x in self.data:
            if str(x.get("id")) == str(task_id):
                x["status"] = new_status
                return


@dataclass(slots=True)
class ServiceBasedTasksQuery:
    """TaskApplicationService を使用した実装。"""

    _service: TaskApplicationPort

    def list_items(self, keyword: str, status: str | None) -> list[dict]:
        """タスク一覧を ApplicationService 経由で取得する。

        Args:
            keyword: タイトル検索用キーワード
            status: フィルタするステータス

        Returns:
            タスク辞書のリスト
        """
        from models import TaskStatus

        status_enum = TaskStatus(status) if status else None
        items = self._service.search(
            keyword,
            with_details=False,
            status=status_enum,
        )
        return [self._task_read_to_dict(item) for item in items]

    def update_item_status(self, task_id: str, new_status: str) -> None:
        """タスクのステータスを更新する。

        Args:
            task_id: タスクID
            new_status: 新しいステータス
        """
        from uuid import UUID

        from loguru import logger

        from models import TaskStatus, TaskUpdate

        try:
            tid = UUID(task_id)
            status_enum = TaskStatus(new_status)
            update_data = TaskUpdate(status=status_enum)
            self._service.update(tid, update_data)
        except (ValueError, Exception) as e:
            logger.warning(f"Failed to update task status: {e}")

    def _task_read_to_dict(self, task: TaskRead) -> dict:
        """TaskRead を辞書形式に変換する。

        Args:
            task: TaskRead インスタンス

        Returns:
            タスク情報の辞書
        """

        def _s(v: object | None) -> str:
            return "" if v is None else str(v)

        return {
            "id": _s(task.id),
            "title": _s(task.title),
            "description": _s(task.description),
            "status": _s(task.status.value if task.status else ""),
            "due_date": _s(task.due_date),
            "created_at": _s(task.created_at),
            "updated_at": _s(task.updated_at),
            "completed_at": _s(task.completed_at),
            "project_id": _s(task.project_id),
        }
        # TODO: 見つからない場合の扱いを決める (例外送出 or ログ警告)。将来的に Command へ移設。
