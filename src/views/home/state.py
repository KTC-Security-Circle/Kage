"""Home State Layer.

【責務】
    State層はホーム画面の表示状態の保持と派生データ計算を担う。

    - デイリーレビュー情報の保持
    - Inboxメモの保持
    - 統計情報の保持（タスク数、プロジェクト数）
    - 選択状態の管理

【責務外（他層の担当）】
    - データの取得 → Controller/ApplicationService
    - UI要素の構築 → Presenter
    - イベントハンドリング → View

【設計上の特徴】
    - Immutableなデータクラス
    - 副作用を排除したsetter設計
    - 派生データのメソッド化

【アーキテクチャ上の位置づけ】
    Controller → State.set_xxx()
                    ↓
    View → State.daily_review
        → State.inbox_memos
        → State.stats
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from views.shared.base_view import BaseViewState


@dataclass(slots=True)
class HomeViewState(BaseViewState):
    """HomeView の表示状態を管理するデータクラス。

    View 自体は UI 制御のみに集中させ、状態の保持と派生計算をこのクラスへ委譲する。
    """

    daily_review: dict[str, Any] = field(default_factory=dict)
    inbox_memos: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def set_daily_review(self, review: dict[str, Any]) -> None:
        """デイリーレビュー情報を設定する。

        Args:
            review: デイリーレビュー情報を含む辞書
        """
        self.daily_review = review

    def set_inbox_memos(self, memos: list[dict[str, Any]]) -> None:
        """Inboxメモを設定する。

        Args:
            memos: Inboxメモのリスト
        """
        self.inbox_memos = list(memos)

    def set_stats(self, stats: dict[str, int]) -> None:
        """統計情報を設定する。

        Args:
            stats: 統計情報を含む辞書
        """
        self.stats = dict(stats)

    def has_inbox_memos(self) -> bool:
        """Inboxメモが存在するか判定する。

        Returns:
            Inboxメモが1件以上ある場合True
        """
        return len(self.inbox_memos) > 0
