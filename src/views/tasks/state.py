"""Tasks State Container.

不変な表示状態を 1 箇所で管理する。イベント経由でのみ更新され、UI直接操作は不可。
MemosView のパターンを簡略適用。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

SortKey = Literal["created_at", "updated_at", "priority"]
TaskStatus = Literal["todo", "todays", "progress", "waiting", "completed", "canceled", "overdue"]
StatusFilter = TaskStatus | None


@dataclass(frozen=True)
class TasksState:
    """タスク画面の単一UI状態コンテナ。

    Args/Returns は update メソッド以外不要なため docstring を簡潔化。詳細な責務:
      - キーワード検索文字列
      - ステータスフィルタ
      - ソートキー & 降順フラグ
      - 選択ID (将来拡張)
    """

    keyword: str = ""
    status: StatusFilter = None  # 現在のタブも兼ねる
    sort_key: SortKey = "updated_at"
    sort_desc: bool = True
    selected_id: str | None = None

    def update(self, **changes: object) -> TasksState:
        """不変更新で新しい状態を生成する。

        Args:
            **changes: 変更するフィールド名と値
        Returns:
            新しい TasksState インスタンス
        """
        return replace(self, **changes)
