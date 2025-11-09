"""Memo UI Components Package.

【責務】
    メモ表示・操作に関する再利用可能なUIコンポーネント群を提供する。
    各コンポーネントはFletのコントロールを継承し、自己完結型のUI部品として機能する。

【コンポーネント一覧と責務】

    MemoActionBar (action_bar.py)
        - 検索フィールドと新規作成ボタンを含むアクションバー
        - タイトル・サブタイトルの表示
        - 検索クエリの入力受付とコールバック
        - 新規作成イベントのトリガー

    MemoStatusTabs (status_tabs.py)
        - 4つのステータスタブ（Inbox/Active/Idea/Archive）の表示
        - タブごとの件数バッジ表示
        - アクティブタブの視覚的フィードバック
        - タブ切り替えイベントのコールバック

    MemoFilters (filters.py)
        - 日付範囲、AI提案状態によるフィルタリングUI
        - フィルタ条件の表示/非表示切り替え
        - フィルタリセット機能
        - フィルタ変更イベントのコールバック

    MemoCard (memo_card.py)
        - 単一メモの表示カード
        - タイトル、内容プレビュー、作成日の表示
        - 選択状態のビジュアルフィードバック
        - クリックイベントのコールバック

    MemoCardList (memo_list.py)
        - メモカードのリスト表示コンテナ
        - 空状態の表示
        - 選択メモのハイライト管理
        - 差分更新による効率的な再描画

【設計上の特徴】
    - Fletコントロール（ft.Container, ft.Column等）を継承
    - コールバック方式によるイベント通知（疎結合）
    - 内部状態の最小化（状態はViewやStateに委譲）
    - 再利用可能な自己完結型コンポーネント

【アーキテクチャ上の位置づけ】
    View → Components（配置・イベント配線）
                ↓
            Callback
                ↓
            View（イベントハンドリング）
                ↓
            Controller

【使用例】
    # アクションバーの作成と配置
    action_bar = MemoActionBar(
        on_create_memo=self._handle_create,
        on_search=self._handle_search,
    )

    # ステータスタブの作成
    status_tabs = MemoStatusTabs(
        on_tab_change=self._handle_tab_change,
        active_status=MemoStatus.INBOX,
        tab_counts={MemoStatus.INBOX: 5, ...},
    )
"""

from .action_bar import MemoActionBar
from .filters import MemoFilters
from .memo_card import MemoCard
from .memo_list import MemoCardList
from .status_tabs import MemoStatusTabs

__all__ = [
    "MemoCard",
    "MemoCardList",
    "MemoActionBar",
    "MemoStatusTabs",
    "MemoFilters",
]
