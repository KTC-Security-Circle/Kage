"""Tasks State Container.

不変な表示状態を 1 箇所で管理する。イベント経由でのみ更新され、UI直接操作は不可。
MemosView のパターンを簡略適用。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

SortKey = Literal["created_at", "updated_at", "due_date"]
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

    # TODO: 永続層導入後は selected_id を Repository の存在確認付きで更新する。
    #       不整合 (ID削除済み等) を検出し安全にクリアできる仕組みを追加する。
    # TODO: 派生値 (フィルタ済み件数/overdue件数など) を State に含めるか再検討。
    #       大量データ時は Query 側集計 + キャッシュ層で最適化する。
    # TODO: keyword が長文検索や AND/OR 構文対応になった場合は、
    #       パース済みトークン構造 (例: dataclass ParsedSearchQuery) へ変更する。

    def update(self, **changes: object) -> TasksState:
        """不変更新で新しい状態を生成する。

        Args:
            **changes: 変更するフィールド名と値
        Returns:
            新しい TasksState インスタンス
        """
        return replace(self, **changes)
