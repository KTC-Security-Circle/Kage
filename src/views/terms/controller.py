"""Term Controller Layer.

【責務】
    Controller層はMVPパターンにおける「Presenter/Controller」の役割を担う。
    ユースケースの実行、ApplicationServiceの呼び出し、State更新の調整を行う。

    - ユースケースメソッドの提供（load, search, select, CRUD）
    - TermApplicationPortを通じたApplicationService呼び出し（将来実装予定）
    - Stateへの状態反映とreconcile実行
    - 検索クエリの正規化（SearchQueryNormalizerを使用）
    - 並び順の適用（utilsモジュールを使用）
    - 例外処理とログ出力（観測性の向上）

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持と派生計算 → State
    - UIレイアウトの決定 → View
    - データの永続化 → ApplicationService/Repository（将来実装）

【設計の拡張ポイント】
    - SearchQueryNormalizer: 検索クエリの正規化戦略（Strategy パターン）
    - TermApplicationPort: ApplicationServiceの抽象化（依存性逆転）※将来実装
    - CRUD メソッド骨格: 統合フェーズで実装予定

【アーキテクチャ上の位置づけ】
    View → Controller → ApplicationService（将来）
                ↓           (TermApplicationPort)
              State
                ↓
            reconcile()

【主な機能】
    - 初期用語一覧の読み込みとソート
    - タブ切り替え時の状態更新
    - 検索実行と結果反映
    - 用語選択状態の管理
    - ステータス別件数の提供
    - CRUD操作の骨格（create/update/delete）※未実装
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from loguru import logger

from views.sample import SampleTermStatus, get_sample_terms

from .query import SearchQueryNormalizer
from .utils import sort_terms

if TYPE_CHECKING:
    from uuid import UUID

    from views.sample import SampleTerm

    from .state import TermsViewState


@dataclass(slots=True)
class TermsController:
    """TermsView 用の状態操作とサービス呼び出しを集約する。"""

    state: TermsViewState
    query_normalizer: SearchQueryNormalizer = field(default_factory=SearchQueryNormalizer)

    def load_initial_terms(self) -> None:
        """初期表示に使用する用語一覧を読み込む。"""
        logger.info("Loading initial terms")
        terms = get_sample_terms()
        ordered = sort_terms(terms)
        self.state.set_all_terms(ordered)
        self.state.set_search_result("", None)
        self.state.reconcile()
        logger.info(f"Loaded {len(terms)} terms")

    def update_tab(self, tab: SampleTermStatus) -> None:
        """タブ変更時に状態を更新する。

        Args:
            tab: 選択されたタブのステータス
        """
        logger.debug(f"Switching to tab: {tab}")
        self.state.set_current_tab(tab)
        self.state.reconcile()

    def update_search(self, query: str) -> None:
        """検索クエリを更新し結果を反映する。

        Args:
            query: 検索クエリ文字列
        """
        normalized = self.query_normalizer.normalize(query)
        logger.debug(f"Search query: {normalized.normalized}")

        if not normalized.normalized:
            # 空クエリの場合は検索を無効化
            self.state.set_search_result("", None)
        else:
            # 検索を実行
            results = self._perform_search(normalized.normalized)
            self.state.set_search_result(normalized.normalized, results)

        self.state.reconcile()

    def select_term(self, term_id: UUID | None) -> None:
        """用語を選択する。

        Args:
            term_id: 選択する用語のID。Noneの場合は選択解除。
        """
        logger.debug(f"Selecting term: {term_id}")
        self.state.set_selected_term(term_id)

    def get_counts(self) -> dict[SampleTermStatus, int]:
        """ステータス別の用語件数を取得する。

        Returns:
            ステータスごとの件数
        """
        return self.state.counts_by_status()

    def _perform_search(self, query: str) -> list[SampleTerm]:
        """検索を実行する。

        Args:
            query: 正規化済みの検索クエリ

        Returns:
            検索にマッチした用語のリスト
        """
        # 全用語から検索（将来的にはApplicationServiceに委譲）
        results = [term for term in self.state.all_terms if self._matches_query(term, query)]
        return sort_terms(results)

    def _matches_query(self, term: SampleTerm, query: str) -> bool:
        """用語が検索クエリにマッチするかを判定する。

        Args:
            term: 判定対象の用語
            query: 検索クエリ（小文字）

        Returns:
            マッチする場合はTrue
        """
        # タイトル、キー、説明、同義語で検索
        return (
            query in term.title.lower()
            or query in term.key.lower()
            or (term.description and query in term.description.lower())
            or any(query in synonym.lower() for synonym in term.synonyms)
        )
