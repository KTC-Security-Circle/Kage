"""Term Controller Layer.

【責務】
    Controller層はMVPパターンにおける「Presenter/Controller」の役割を担う。
    ユースケースの実行、ApplicationServiceの呼び出し、State更新の調整を行う。

    - ユースケースメソッドの提供（load, search, select, CRUD）
    - TermApplicationPortを通じたApplicationService呼び出し
    - Stateへの状態反映と自動整合性保証
    - 検索クエリの正規化（SearchQueryNormalizerを使用）
    - 並び順の適用（utilsモジュールを使用）
    - 例外処理とログ出力（観測性の向上）

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持と派生計算 → State
    - UIレイアウトの決定 → View
    - データの永続化 → ApplicationService/Repository

【設計の拡張ポイント】
    - SearchQueryNormalizer: 検索クエリの正規化戦略（Strategy パターン）
    - TermApplicationPort: ApplicationServiceの抽象化（依存性逆転、Protocol実装済み）
    - 依存性注入: service=None時は暫定的にサンプルデータを使用

【アーキテクチャ上の位置づけ】
    View → Controller → ApplicationService
                ↓           (TermApplicationPort)
              State
                ↓
         自動整合性保証（derived property）

【主な機能】
    - 初期用語一覧の読み込みとソート
    - タブ切り替え時の状態更新
    - 検索実行と結果反映
    - 用語選択状態の管理
    - ステータス別件数の提供
    - CRUD操作（create/update/delete）※ApplicationService統合時に完全動作
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from loguru import logger

from views.sample import SampleTermStatus, get_sample_terms

from .query import SearchQueryNormalizer
from .utils import sort_terms

if TYPE_CHECKING:
    from uuid import UUID

    from views.sample import SampleTerm

    from .state import TermsViewState


class TermApplicationPort(Protocol):
    """用語管理ApplicationServiceの抽象インターフェース。

    依存性逆転の原則に従い、Controller層が具体的なApplicationService実装に
    依存しないよう、Protocolで抽象化する。

    将来的な実装:
        - src/logic/application/term_application_service.py に TermApplicationService を実装
        - UnitOfWorkパターンによるトランザクション管理
        - Repository経由のデータアクセス
    """

    async def list_terms(self, status: SampleTermStatus | None = None) -> list[SampleTerm]:
        """用語一覧を取得する。

        Args:
            status: フィルタするステータス。Noneの場合は全件取得。

        Returns:
            用語のリスト
        """
        ...

    async def search_terms(self, query: str) -> list[SampleTerm]:
        """用語を検索する。

        Args:
            query: 検索クエリ

        Returns:
            検索にマッチした用語のリスト
        """
        ...

    async def create_term(self, form_data: dict[str, object]) -> SampleTerm:
        """用語を作成する。

        Args:
            form_data: フォームデータ

        Returns:
            作成された用語

        Raises:
            ValueError: バリデーションエラー
        """
        ...

    async def update_term(self, term_id: UUID, form_data: dict[str, object]) -> SampleTerm:
        """用語を更新する。

        Args:
            term_id: 更新対象の用語ID
            form_data: 更新データ

        Returns:
            更新された用語

        Raises:
            ValueError: バリデーションエラー
        """
        ...

    async def delete_term(self, term_id: UUID) -> bool:
        """用語を削除する。

        Args:
            term_id: 削除対象の用語ID

        Returns:
            削除成功時True

        Raises:
            ValueError: 用語が見つからない場合
        """
        ...


@dataclass(slots=True)
class TermsController:
    """TermsView 用の状態操作とサービス呼び出しを集約する。

    依存性注入により、ApplicationServiceをモック可能な設計とする。
    service=Noneの場合は暫定的にサンプルデータを使用する。
    """

    state: TermsViewState
    service: TermApplicationPort | None = None
    query_normalizer: SearchQueryNormalizer = field(default_factory=SearchQueryNormalizer)

    async def load_initial_terms(self) -> None:
        """初期表示に使用する用語一覧を読み込む。"""
        logger.info("Loading initial terms")

        if self.service:
            terms = await self.service.list_terms()
        else:
            # 暫定: サンプルデータ使用
            terms = get_sample_terms()

        ordered = sort_terms(terms)
        self.state.set_all_terms(ordered)
        self.state.set_search_result("", None)
        logger.info(f"Loaded {len(terms)} terms")

    def update_tab(self, tab: SampleTermStatus) -> None:
        """タブ変更時に状態を更新する。

        Args:
            tab: 選択されたタブのステータス
        """
        logger.debug(f"Switching to tab: {tab}")
        self.state.set_current_tab(tab)

    async def update_search(self, query: str) -> None:
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
            results = await self._perform_search(normalized.normalized)
            self.state.set_search_result(normalized.normalized, results)

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
        return self.state.counts_by_status

    async def _perform_search(self, query: str) -> list[SampleTerm]:
        """検索を実行する。

        Args:
            query: 正規化済みの検索クエリ

        Returns:
            検索にマッチした用語のリスト
        """
        if self.service:
            results = await self.service.search_terms(query)
        else:
            # 暫定: ローカル検索
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

    async def create_term(self, form_data: dict[str, object]) -> SampleTerm:
        """新しい用語を作成する。

        Args:
            form_data: ダイアログから受け取ったフォームデータ
                - key: str (必須、一意)
                - title: str (必須)
                - description: str | None
                - status: str (TermStatus.value)
                - source_url: str | None
                - synonyms: list[str]

        Returns:
            作成された用語

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: ApplicationServiceが未設定の場合
        """
        if not self.service:
            msg = "ApplicationService が設定されていません"
            raise RuntimeError(msg)

        logger.info(f"Creating term: {form_data.get('key')}")
        created_term = await self.service.create_term(form_data)

        # State を更新
        self.state.upsert_term(created_term)

        logger.info(f"Created term: {created_term.key} (ID: {created_term.id})")
        return created_term

    async def update_term(self, term_id: UUID, form_data: dict[str, object]) -> SampleTerm:
        """既存の用語を更新する。

        Args:
            term_id: 更新対象の用語ID
            form_data: 更新データ

        Returns:
            更新された用語

        Raises:
            ValueError: バリデーションエラー
            RuntimeError: ApplicationServiceが未設定の場合
        """
        if not self.service:
            msg = "ApplicationService が設定されていません"
            raise RuntimeError(msg)

        logger.info(f"Updating term: {term_id}")
        updated_term = await self.service.update_term(term_id, form_data)

        # State を更新
        self.state.upsert_term(updated_term)

        logger.info(f"Updated term: {updated_term.key} (ID: {updated_term.id})")
        return updated_term

    async def delete_term(self, term_id: UUID) -> bool:
        """用語を削除する。

        Args:
            term_id: 削除対象の用語ID

        Returns:
            削除成功時True

        Raises:
            ValueError: 用語が見つからない場合
            RuntimeError: ApplicationServiceが未設定の場合
        """
        if not self.service:
            msg = "ApplicationService が設定されていません"
            raise RuntimeError(msg)

        logger.info(f"Deleting term: {term_id}")
        success = await self.service.delete_term(term_id)

        if success:
            # State から削除
            self.state.all_terms = [t for t in self.state.all_terms if t.id != term_id]
            self.state.rebuild_index()

            # 選択状態をクリア
            if self.state.selected_term_id == term_id:
                self.state.selected_term_id = None

            logger.info(f"Deleted term: {term_id}")

        return success
