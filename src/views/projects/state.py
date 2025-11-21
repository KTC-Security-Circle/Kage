"""プロジェクト画面のUI状態管理

単一のUI状態コンテナとして ProjectState を定義。
イベント駆動での状態更新パターンを提供する。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from models import ProjectStatus

SortKey = Literal["created_at", "updated_at", "title", "due_date"]
StatusFilter = ProjectStatus | None


@dataclass(frozen=True)
class ProjectState:
    """プロジェクト画面の単一UI状態コンテナ。

    イベント駆動でのみ更新し、常に不変オブジェクトとして扱う。
    選択状態、フィルタ、並び順などの表示に関わる状態を一元管理する。

    Attributes:
        keyword: 検索キーワード
        status: ステータスフィルタ（None = 全て）
        sort_key: 並び替えキー
        sort_desc: 降順フラグ
        selected_id: 選択中のプロジェクトID
    """

    keyword: str = ""
    status: StatusFilter = None
    sort_key: SortKey = "updated_at"
    sort_desc: bool = True
    selected_id: str | None = None

    def update(self, **changes: object) -> ProjectState:
        """不変更新。常に新しいインスタンスを返す。

        Args:
            **changes: 更新する属性と値のペア

        Returns:
            更新された新しい ProjectState インスタンス
        """
        return replace(self, **changes)

    def clear_selection(self) -> ProjectState:
        """選択状態をクリアする。

        Returns:
            選択がクリアされた新しい ProjectState インスタンス
        """
        return self.update(selected_id=None)

    def toggle_sort_direction(self) -> ProjectState:
        """並び順を反転する。

        Returns:
            並び順が反転された新しい ProjectState インスタンス
        """
        return self.update(sort_desc=not self.sort_desc)
