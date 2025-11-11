"""Memo Search Query Definitions.

【責務】
    検索条件を表すデータクラスと正規化戦略を定義する。
    ControllerとApplicationService間のインターフェースを明確化する。

    - 検索クエリのデータ構造定義（MemoSearchQuery）
    - 検索クエリの正規化戦略（SearchQueryNormalizer）
    - クエリの妥当性判定（is_empty）

【責務外（他層の担当）】
    - 実際の検索実行 → ApplicationService
    - UIからの入力受付 → View
    - 検索結果の状態保持 → State

【設計上の特徴】
    - Immutableなデータクラス（frozen=True, slots=True）
    - 拡張可能な正規化戦略（SearchQueryNormalizer基底クラス）
    - 型安全なパラメータ定義（status, date_from, tags等）

【アーキテクチャ上の位置づけ】
    View → Controller → query.SearchQueryNormalizer
                            ↓
                        MemoSearchQuery
                            ↓
                    ApplicationService

【拡張ポイント】
    - SearchQueryNormalizerを継承してカスタム正規化戦略を実装
        例: TokenizerQueryNormalizer（形態素解析）
        例: SynonymQueryNormalizer（類義語展開）
        例: StopWordQueryNormalizer（ストップワード除去）
    - MemoSearchQueryに新しいフィルタ条件を追加可能

【提供するクラス】
    - MemoSearchQuery: 検索条件を表すデータクラス
    - SearchQueryNormalizer: 検索クエリ正規化の基底クラス
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from models import MemoStatus


@dataclass(frozen=True, slots=True)
class MemoSearchQuery:
    """メモ検索クエリ。

    検索に必要なパラメータを集約し、型安全な引き渡しを可能にする。
    """

    text: str = ""
    status: MemoStatus | None = None
    date_from: date | None = None
    date_to: date | None = None
    tags: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        """検索クエリが空かどうかを判定する。

        Returns:
            すべての条件が未指定の場合 True
        """
        return not (self.text or self.status or self.date_from or self.date_to or self.tags)


class SearchQueryNormalizer:
    """検索クエリ正規化戦略の基底クラス。

    拡張ポイントとして定義。将来的にトークン化、キーワード抽出などを追加可能。
    """

    def normalize(self, raw_query: str) -> str:
        """生の検索クエリを正規化する。

        Args:
            raw_query: ユーザー入力の生クエリ

        Returns:
            正規化されたクエリ文字列
        """
        return raw_query.strip()
