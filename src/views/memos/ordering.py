"""Memo Ordering Policies.

【責務】
    メモの並び順を決定するポリシーを集約する。
    Controllerからロジックを分離し、拡張・変更を容易にする。

    - ステータスごとの表示優先順位の定義
    - メモのソートキー計算
    - メモリスト全体のソート処理

【責務外（他層の担当）】
    - メモデータの取得 → Controller
    - ソート結果の状態保持 → State
    - UI表示 → View/Presenter

【設計上の特徴】
    - ステータス順序マップ（_STATUS_ORDER）の集中管理
    - 拡張可能な設計（新しいステータス追加に対応）
    - 純粋関数による実装（副作用なし）

【アーキテクチャ上の位置づけ】
    Controller → ordering.sort_memos()
                    ↓
                get_memo_sort_key()
                    ↓
                _STATUS_ORDER

【拡張ポイント】
    - 新しいステータス追加時は _STATUS_ORDER に追加
    - 複雑なソートロジック（日付順、タイトル順等）も追加可能
    - Strategyパターンで複数のソート戦略を切り替え可能

【提供する関数】
    - get_memo_sort_key(): 単一メモのソートキー取得
    - sort_memos(): メモリスト全体のソート
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from models import MemoStatus

if TYPE_CHECKING:
    from models import MemoRead


# ステータスごとの表示順序（数値が小さいほど優先）
_STATUS_ORDER: dict[MemoStatus, int] = {
    MemoStatus.INBOX: 0,
    MemoStatus.ACTIVE: 1,
    MemoStatus.IDEA: 2,
    MemoStatus.ARCHIVE: 3,
}


def get_memo_sort_key(memo: MemoRead) -> int:
    """メモのソートキーを取得する。

    ステータスごとに安定した順序を提供する。

    Args:
        memo: ソート対象のメモ

    Returns:
        ソートキー（数値）
    """
    return _STATUS_ORDER.get(memo.status, 99)


def sort_memos(memos: list[MemoRead]) -> list[MemoRead]:
    """メモリストをステータス順にソートする。

    Args:
        memos: ソート対象のメモリスト

    Returns:
        ソート済みのメモリスト
    """
    return sorted(memos, key=get_memo_sort_key)
