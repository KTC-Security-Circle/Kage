"""Home View Components Package.

【責務】
    ホーム画面表示に関する再利用可能なUIコンポーネント群を提供する。

【コンポーネント一覧と責務】

    DailyReviewCard (daily_review_card.py)
        - デイリーレビューの表示
        - 日次サマリー情報の表示
        - アクションボタンの配置

    InboxMemosSection (inbox_memos_section.py)
        - Inboxメモのリスト表示
        - メモクリック時のコールバック
        - 「すべて見る」リンク

    StatsCards (stats_cards.py)
        - 統計カード群の表示
        - 次のアクション、インボックス、プロジェクトの統計
        - クリック時のナビゲーション

【設計上の特徴】
    - Fletコントロール（ft.Container等）を継承
    - コールバック方式によるイベント通知
    - Presenterから受け取ったデータを表示
"""

from __future__ import annotations

from .daily_review_card import DailyReviewCard
from .inbox_memos_section import InboxMemosSection
from .stats_cards import StatsCards

__all__ = [
    "DailyReviewCard",
    "InboxMemosSection",
    "StatsCards",
]
