"""プロジェクト並び替え戦略

Strategy パターンでプロジェクトデータの並び替えロジックを抽象化。
異なる並び替え条件を柔軟に切り替え可能な構成を提供する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterable


class OrderStrategy(Protocol):
    """並び替え戦略の抽象インターフェース。

    各戦略は key メソッドを実装し、sorted() 関数のキー関数として使用される。
    """

    # TODO: 並び替えキー型の拡張
    # - 現在は戻り値型を str に限定しているため、数値や datetime を文字列化して不自然な辞書順になる恐れがある。
    # - 今後は SortableKey 型 (str | int | float | datetime) を導入し、FieldOrder.key の実装を更新する。
    # - None の扱い (先頭/末尾) 方針を決めた上で、必要ならタプル (flag, value) 形式へ拡張する。
    def key(self, item: dict[str, Any]) -> str:
        """並び替えキーを生成する。

        Args:
            item: 並び替え対象のプロジェクトデータ

        Returns:
            並び替えに使用するキー値
        """
        ...


@dataclass
class FieldOrder:
    """単純なフィールドベースの並び替え戦略。

    指定されたフィールドの値をキーとして使用する。
    フィールドが存在しない場合は空文字を返して安定動作を担保する。

    Attributes:
        field: 並び替えに使用するフィールド名
    """

    field: str

    def key(self, item: dict[str, Any]) -> str:
        """フィールド値をキーとして返す。

        Args:
            item: プロジェクトデータ辞書

        Returns:
            指定フィールドの値（存在しない場合は空文字）
        """
        value = item.get(self.field, "")
        return str(value) if value is not None else ""


# 利用可能な並び替え戦略のマッピング
# TODO: サーバー/DB 側のフィールドと同期
# - Repository 層でのソートキーと一致させてください。
# - クライアント側で未対応のキーが指定された場合のフォールバック方針も検討すると安全です。
ORDERING_MAP: dict[str, OrderStrategy] = {
    "created_at": FieldOrder("created_at"),
    "updated_at": FieldOrder("updated_at"),
    "title": FieldOrder("title"),
    "due_date": FieldOrder("due_date"),
}


def apply_order_desc(
    items: Iterable[dict[str, Any]],
    strategy: OrderStrategy,
) -> list[dict[str, Any]]:
    """指定された戦略で項目を降順に並び替える。

    Args:
        items: 並び替え対象の項目一覧
        strategy: 使用する並び替え戦略

    Returns:
        降順に並び替えされた項目のリスト
    """
    return sorted(items, key=strategy.key, reverse=True)


def apply_order_asc(
    items: Iterable[dict[str, Any]],
    strategy: OrderStrategy,
) -> list[dict[str, Any]]:
    """指定された戦略で項目を昇順に並び替える。

    Args:
        items: 並び替え対象の項目一覧
        strategy: 使用する並び替え戦略

    Returns:
        昇順に並び替えされた項目のリスト
    """
    return sorted(items, key=strategy.key, reverse=False)


def apply_order(
    items: Iterable[dict[str, Any]],
    strategy: OrderStrategy,
    *,
    desc: bool,
) -> list[dict[str, Any]]:
    """指定された戦略で項目を並び替える。

    Args:
        items: 並び替え対象の項目一覧
        strategy: 使用する並び替え戦略
        desc: 降順フラグ（True=降順、False=昇順）

    Returns:
        並び替えされた項目のリスト
    """
    return apply_order_desc(items, strategy) if desc else apply_order_asc(items, strategy)


def get_order_strategy(sort_key: str) -> OrderStrategy:
    """並び替えキーに対応する戦略を取得する。

    Args:
        sort_key: 並び替えキー

    Returns:
        対応する並び替え戦略

    Raises:
        KeyError: 不正な並び替えキーが指定された場合
    """
    if sort_key not in ORDERING_MAP:
        valid_keys = ", ".join(ORDERING_MAP.keys())
        msg = f"Invalid sort key '{sort_key}'. Valid keys: {valid_keys}"
        raise KeyError(msg)
    return ORDERING_MAP[sort_key]
