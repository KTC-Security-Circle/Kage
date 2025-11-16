"""Home Controller Layer.

【責務】
    Controller層はMVPパターンにおける「Presenter/Controller」の役割を担う。
    データの取得、State更新の調整を行う。

    - データの取得（HomeQueryを使用）
    - Stateへの状態反映
    - 例外処理とログ出力

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持 → State
    - UIレイアウトの決定 → View

【アーキテクチャ上の位置づけ】
    View → Controller → HomeQuery
                ↓
              State

【主な機能】
    - 初期データの読み込み
    - デイリーレビュー情報の取得
    - Inboxメモの取得
    - 統計情報の取得
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from .query import HomeQuery
    from .state import HomeViewState


@dataclass(slots=True)
class HomeController:
    """HomeView 用の状態操作とデータ取得を集約する。"""

    state: HomeViewState
    query: HomeQuery

    def load_initial_data(self) -> None:
        """初期データを読み込む。

        デイリーレビュー、Inboxメモ、統計情報を取得してStateに反映する。
        """
        try:
            logger.debug("Loading initial home data")

            # デイリーレビューを取得
            review = self.query.get_daily_review()
            self.state.set_daily_review(review)

            # Inboxメモを取得
            inbox_memos = self.query.get_inbox_memos()
            self.state.set_inbox_memos(inbox_memos)

            # 統計情報を取得
            stats = self.query.get_stats()
            self.state.set_stats(stats)

            logger.debug(f"Loaded: {len(inbox_memos)} inbox memos, stats={stats}")

        except Exception as e:
            logger.error(f"Failed to load initial home data: {e}")
            raise

    def refresh_data(self) -> None:
        """データを再読み込みする。

        全データを最新の状態に更新する。
        """
        self.load_initial_data()
