"""Term Query Layer.

【責務】
    検索クエリの定義と正規化戦略を提供する。

    - 検索クエリのデータ構造定義
    - 正規化戦略（トリム、小文字化等）
    - 将来的な拡張（部分一致、あいまい検索、タグ検索等）

【責務外（他層の担当）】
    - 実際の検索実行 → Controller/ApplicationService
    - 検索結果の整形 → Presenter
    - UI要素の構築 → Components
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TermSearchQuery:
    """用語検索のクエリを表現するデータクラス。"""

    raw: str
    normalized: str


class SearchQueryNormalizer:
    """検索クエリの正規化を担当する。"""

    def normalize(self, raw: str) -> TermSearchQuery:
        """生のクエリ文字列を正規化する。

        Args:
            raw: 入力された生のクエリ文字列

        Returns:
            正規化されたクエリオブジェクト
        """
        normalized = raw.strip().lower()
        return TermSearchQuery(raw=raw, normalized=normalized)
