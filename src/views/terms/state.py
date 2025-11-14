"""Term State Layer.

【責務】
    State層は表示状態の保持と派生データ計算を担う。
    Viewが必要とする全ての状態を一元管理し、整合性を保証する。

    - 表示状態の保持（current_tab, search_query, selected_term_id 等）
    - 全用語データの保持（all_terms）
    - 検索結果の保持（search_results）
    - 派生データの計算（フィルタリング済み用語一覧、ステータス別件数）
    - 用語IDインデックスの管理（高速検索用）
    - 選択状態の自動整合性保証

【責務外（他層の担当）】
    - データの取得・永続化 → Controller/ApplicationService
    - UI要素の構築 → Presenter
    - イベントハンドリング → View
    - 並び順の決定 → utils モジュール

【設計上の特徴】
    - Immutableなデータクラス（dataclass with slots）
    - 副作用を排除したsetter設計（自動整合性保証）
    - インデックス（_by_id）による高速検索
    - 派生データのプロパティ化（visible_terms, selected_term, counts_by_status）

【アーキテクチャ上の位置づけ】
    Controller → State.set_xxx()
                    ↓
              自動整合性保証
                    ↓
    View → State.visible_terms
        → State.selected_term
        → State.counts_by_status
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from models import TermRead, TermStatus


@dataclass(slots=True)
# TODO: 設計上の改善点
#   - reconcile()を排除し、derived propertyで自動計算
#   - 不変性の徹底（setterで新しいインスタンスを返す、または内部でキャッシュ無効化）
#   - Domain StateとPresentation Stateの明確な分離
class TermsViewState:
    """TermsView の表示状態を管理するデータクラス。

    View 自体は UI 制御のみに集中させ、状態の保持と派生計算をこのクラスへ委譲する。
    """

    current_tab: TermStatus = TermStatus.APPROVED
    search_query: str = ""
    all_terms: list[TermRead] = field(default_factory=list)
    search_results: list[TermRead] | None = None
    selected_term_id: UUID | None = None
    # id -> TermRead のインデックス。全用語(all_terms)に対して構築する。
    _by_id: dict[UUID, TermRead] = field(default_factory=dict, repr=False)

    def set_all_terms(self, terms: list[TermRead]) -> None:
        """全用語一覧を更新する。

        Args:
            terms: 表示対象となる用語のシーケンス
        """
        self.all_terms = list(terms)
        self.rebuild_index()
        self._validate_selection()

    def set_search_result(self, query: str, results: list[TermRead] | None) -> None:
        """検索クエリと結果を保存する。

        Args:
            query: 入力された検索クエリ
            results: 検索結果。`None` の場合は検索を無効化した扱いとなる。
        """
        self.search_query = query
        self.search_results = results
        self._validate_selection()

    def set_current_tab(self, tab: TermStatus) -> None:
        """アクティブなタブを設定する。

        Args:
            tab: 選択したタブに対応するステータス
        """
        self.current_tab = tab
        self.selected_term_id = None

    def set_selected_term(self, term_id: UUID | None) -> None:
        """選択中の用語IDを更新する。

        Args:
            term_id: 選択する用語のID。None の場合は選択解除。
        """
        self.selected_term_id = term_id

    def upsert_term(self, term: TermRead) -> None:
        """単一の用語を追加または更新する。

        Args:
            term: 追加または更新する用語
        """
        for i, existing in enumerate(self.all_terms):
            if existing.id == term.id:
                self.all_terms[i] = term
                self._by_id[term.id] = term
                return
        self.all_terms.append(term)
        self._by_id[term.id] = term

    def _validate_selection(self) -> None:
        """選択中の用語が現在の派生リストに存在するかを検証し、存在しない場合は選択解除する。

        これはsetterメソッド内で自動的に呼ばれるため、reconcile()を手動で呼ぶ必要はない。
        """
        if self.selected_term_id is None:
            return

        derived = self.visible_terms
        if not any(t.id == self.selected_term_id for t in derived):
            self.selected_term_id = None

    @property
    def visible_terms(self) -> list[TermRead]:
        """現在のタブと検索条件でフィルタリングした用語一覧を返す（derived property）。

        Returns:
            表示対象の用語リスト
        """
        # 検索結果が存在する場合はそれを優先
        source = self.search_results if self.search_results is not None else self.all_terms

        # タブによるステータスフィルタ
        return [t for t in source if t.status == self.current_tab]

    @property
    def is_searching(self) -> bool:
        """検索中かどうかを返す。

        Returns:
            検索中の場合True
        """
        return self.search_results is not None and bool(self.search_query)

    def derived_terms(self) -> list[TermRead]:
        """【非推奨】visible_terms プロパティを使用してください。

        このメソッドは後方互換性のために残されていますが、
        新しいコードでは `visible_terms` プロパティを使用してください。

        マイグレーションガイド:
            ```python
            # 変更前
            terms = state.derived_terms()

            # 変更後
            terms = state.visible_terms
            ```

        Returns:
            表示対象の用語リスト

        Warnings:
            DeprecationWarning: このメソッドは将来のバージョンで削除されます。

        Note:
            削除予定バージョン: v2.0.0
        """
        import warnings

        warnings.warn(
            "derived_terms() は非推奨です。visible_terms プロパティを使用してください。",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.visible_terms

    @property
    def selected_term(self) -> TermRead | None:
        """選択中の用語を返す（derived property）。

        Returns:
            選択中の用語。未選択の場合は None。
        """
        if self.selected_term_id is None:
            return None
        return self._by_id.get(self.selected_term_id)

    @property
    def counts_by_status(self) -> dict[TermStatus, int]:
        """ステータス別の用語件数を集計する（derived property）。

        Returns:
            ステータスごとの件数を持つ辞書
        """
        counts: dict[TermStatus, int] = {
            TermStatus.APPROVED: 0,
            TermStatus.DRAFT: 0,
            TermStatus.DEPRECATED: 0,
        }
        for term in self.all_terms:
            if term.status in counts:
                counts[term.status] += 1
        return counts

    def rebuild_index(self) -> None:
        """IDインデックスを再構築する。"""
        self._by_id = {term.id: term for term in self.all_terms}
