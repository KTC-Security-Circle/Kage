"""検索クエリ正規化ユーティリティとデータクラス。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchQuery:
    """Raw検索文字列を保持し、派生として正規化文字列を提供する。"""

    raw: str

    @property
    def normalized(self) -> str:
        """前後空白除去 + 小文字化した検索語を返す。"""
        return self.raw.strip().lower()
