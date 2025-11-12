"""Tasks Ordering Strategies.

単純なフィールドベースのソート戦略を定義。将来 priority 計算拡張などに対応可能。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # Runtime不要
    from collections.abc import Iterable


class OrderStrategy(Protocol):
    """並び替え戦略インターフェース。"""

    def key(self, item: dict) -> str:
        """アイテムからソートキーを取得する。"""
        ...


@dataclass
class FieldOrder:
    """単純フィールド順。欠損時は None を返し安定ソート。"""

    field: str

    def key(self, item: dict) -> str:
        value: object | None = item.get(self.field, None)
        # ISO8601 文字列 (日付/日時) は文字列比較で概ね妥当な順序になる
        return str(value) if value is not None else ""
        # TODO: locale対応の文字列比較 (例: ICU) や自然順ソート ("Task 2" < "Task 10") が必要になれば
        #       strategy 実装を追加する。現在は単純な str() による辞書式。


ORDERING_MAP: dict[str, OrderStrategy] = {
    "created_at": FieldOrder("created_at"),
    "updated_at": FieldOrder("updated_at"),
    "due_date": FieldOrder("due_date"),
}

# TODO: ユーザー定義順序 (ドラッグ&ドロップ保存) を扱うためには別ストラテジー UserDefinedOrder が必要。
# TODO: 複合ソート (updated_at DESC, priority DESC) などのチェーン構成をサポートする CompositeOrderStrategy を検討。


def apply_order(items: Iterable[dict], strategy: OrderStrategy, *, descending: bool) -> list[dict]:
    """指定戦略で並び替えを実行する。

    Args:
        items: ソート対象イテラブル
        strategy: 戦略実装
        descending: 降順ソートするか
    Returns:
        ソート後リスト
    """
    return sorted(items, key=strategy.key, reverse=descending)
    # TODO: 大量データのときはサーバー側/DB側ソートへ委譲し、ここではキー抽出用 Query 拡張に切り替える。
