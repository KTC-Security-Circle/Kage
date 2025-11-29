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

import logging
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

            # Empty data is not an error — 表示上未登録/未利用状態であるためINFO扱いでログ出力
            if not review and not inbox_memos and not stats:
                logger.info("Home initial data empty: no review, no inbox memos, no stats")
                logging.getLogger(__name__).info("Home initial data empty")
            else:
                logger.debug(f"Loaded: {len(inbox_memos)} inbox memos, stats={stats}")

        except Exception as e:
            # それ以外の例外はエラーとしてログ出力し再送出
            logger.error(f"Failed to load initial home data: {e}")
            raise

    def refresh_data(self) -> None:
        """データを再読み込みする。

        全データを最新の状態に更新する。
        """
        self.load_initial_data()

    def start_loading_one_liner(self) -> None:
        """AI一言生成のローディングを開始する。

        バックグラウンド生成開始時に呼び出され、State をローディング状態に設定する。
        """
        logger.debug("[Controller] AI一言ローディング状態をTrueに設定")
        self.state.set_loading_one_liner(is_loading=True)

    def set_one_liner_message(self, message: str | None) -> None:
        """AI一言メッセージを設定する。

        バックグラウンド生成完了時に呼び出され、State にメッセージを反映する。

        Args:
            message: 生成されたメッセージ(失敗時はNone)
        """
        logger.debug(f"[Controller] AI一言メッセージを設定: {message[:50] if message else 'None'}...")
        self.state.set_one_liner_message(message)

        # daily_reviewのmessageフィールドを更新(生成された場合のみ)
        if message:
            self.state.daily_review["message"] = message
            logger.debug("[Controller] daily_reviewにメッセージを反映")

    def generate_one_liner_sync(self) -> str | None:
        """AI一言メッセージを同期的に生成する。

        バックグラウンドスレッドから呼び出される。

        Returns:
            生成されたメッセージ(失敗時はNone)
        """
        try:
            logger.debug("[Controller] AI一言生成開始（同期処理）")
            # HomeQueryにget_one_liner_message()がある場合はそれを使用
            if hasattr(self.query, "get_one_liner_message"):
                # テストのため
                import time

                logger.debug("[Controller] Query.get_one_liner_message()を呼び出し")
                time.sleep(10)
                result = self.query.get_one_liner_message()  # type: ignore[attr-defined]
                logger.debug(f"[Controller] AI一言生成結果: {result[:50] if result else 'None'}...")
                return result
            # フォールバック: 従来のdaily_reviewから取得
            logger.debug("[Controller] フォールバック: Query.get_daily_review()から取得")
            return self.query.get_daily_review().get("message")
        except Exception as e:
            logger.error(f"[Controller] Failed to generate one-liner message: {e}")
            return None
