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
        if self.field == "priority":
            if value is None:
                return "0000"
            if isinstance(value, int):
                return f"{value:04d}"
            try:
                return f"{int(value):04d}"
            except Exception:
                return "0000"
        return str(value) if value is not None else ""


ORDERING_MAP: dict[str, OrderStrategy] = {
    "created_at": FieldOrder("created_at"),
    "updated_at": FieldOrder("updated_at"),
    "priority": FieldOrder("priority"),
}


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
