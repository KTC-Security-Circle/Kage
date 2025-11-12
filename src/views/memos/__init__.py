"""Memo views package.

メモ管理機能のビューコンポーネント群。
MVPパターンに基づき、責務を明確に分離した設計。

ディレクトリ構成:
    memos/
        __init__.py         - パッケージエントリーポイント
        view.py             - View層：画面構築とイベント配線
        controller.py       - Controller層：ユースケース実行と状態更新
        state.py            - State層：View状態の保持と派生計算
        presenter.py        - Presenter層：UI構築・更新・表示ロジック
        ordering.py         - 並び順ポリシーの定義
        query.py            - 検索クエリの型定義と正規化
        components/         - 再利用可能なUIコンポーネント群

責務分離:
    - View: UIレイアウト構築、イベントハンドラー配線、Controller呼び出し
    - Controller: ApplicationService呼び出し、状態更新、ビジネスルール調整
    - State: 表示状態の保持、派生データ計算、選択整合性管理
    - Presenter: データフォーマット、UI要素生成、差分更新ロジック
    - Ordering: メモの並び順決定ロジック（拡張可能）
    - Query: 検索条件の型定義、クエリ正規化戦略（拡張可能）

主な機能:
    - Inbox/Active/Idea/Archive の4つのタブでメモ分類
    - 検索とフィルタリング
    - メモ詳細表示
    - メモ作成・編集・削除（CRUD）※統合フェーズで実装予定
    - AI提案機能（統合フェーズで実装予定）
"""

from .create_memo_view import CreateMemoView
from .view import MemosView

__all__ = [
    "MemosView",
    "CreateMemoView",
]
