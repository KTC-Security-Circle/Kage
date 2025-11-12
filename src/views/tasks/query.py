"""Tasks Query Abstraction.

CQRS の Query 側。テスト容易性のため InMemory 実装を同梱。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


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
