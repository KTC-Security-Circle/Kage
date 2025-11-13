"""Tags View の表示ユーティリティ群。

純粋関数のみを提供し、UIや副作用は含まない。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import TagDict


def sort_tags_by_name(tags: list[TagDict]) -> list[TagDict]:
    """名前昇順でソートした配列を返す。

    Args:
        tags: タグ配列

    Returns:
        名前昇順の新しい配列
    """
    return sorted(tags, key=lambda t: t.get("name", "").lower())


def filter_tags_by_query(tags: list[TagDict], query: str) -> list[TagDict]:
    """検索語でフィルタしたタグ配列を返す。

    Args:
        tags: タグ配列
        query: 正規化済み検索語（小文字）

    Returns:
        フィルタ後の新しい配列
    """
    if not query:
        return list(tags)
    return [t for t in tags if query in t.get("name", "").lower() or query in t.get("description", "").lower()]
