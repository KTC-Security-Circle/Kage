"""Shared component types to avoid circular imports.

MemoListData など、複数モジュールから参照されるUI用データ型を集約する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # 型チェック時のみ解決して循環依存を回避
    from .memo_card import MemoCardData


@dataclass(frozen=True, slots=True)
class MemoListData:
    """メモリスト表示用データ

    Attributes:
        cards: 表示するメモカードデータのリスト
        empty_message: リストが空の場合のメッセージ
    """

    cards: tuple[MemoCardData, ...]  # type: ignore[name-defined]  # 解決はTYPE_CHECKING時のみ
    empty_message: str | None = None
