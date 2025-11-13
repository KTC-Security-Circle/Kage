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

    # ================================================================================
    # TODO: [ロジック担当者向け] CRUD操作メソッドの実装
    # ================================================================================
    #
    # 以下のメソッドを実装してください。ApplicationServiceと連携して
    # データベースへの永続化とStateの更新を行います。
    #
    # 前提条件:
    # - TermApplicationService が実装済みであること
    # - Term, TermCreate, TermUpdate モデルが models/__init__.py に定義済み
    # - データベースマイグレーションが適用済みであること
    #
    # --------------------------------------------------------------------------------
    # async def create_term(self, form_data: dict[str, object]) -> None:
    #     """新しい用語を作成する。
    #
    #     Args:
    #         form_data: ダイアログから受け取ったフォームデータ
    #             - key: str (必須、一意)
    #             - title: str (必須)
    #             - description: str | None
    #             - status: str (TermStatus.value)
    #             - source_url: str | None
    #             - synonyms: list[str]
    #
    #     Raises:
    #         ValueError: バリデーションエラー
    #         IntegrityError: キーの重複など
    #
    #     実装内容:
    #         1. form_data を TermCreate に変換
    #            term_create = TermCreate(
    #                key=form_data["key"],
    #                title=form_data["title"],
    #                description=form_data.get("description"),
    #                status=TermStatus(form_data["status"]),
    #                source_url=form_data.get("source_url"),
    #            )
    #
    #         2. ApplicationService で用語を作成
    #            created_term = await self.app_service.create_term(term_create)
    #
    #         3. 同義語を作成（別途 create_synonyms メソッド）
    #            synonyms = form_data.get("synonyms", [])
    #            if synonyms:
    #                await self.app_service.create_synonyms(created_term.id, synonyms)
    #
    #         4. State を更新
    #            self.state.add_term(created_term)  # ← Stateに add_term メソッド追加必要
    #            self.state.reconcile()
    #
    #         5. ログ出力
    #            logger.info(f"Created term: {created_term.key} (ID: {created_term.id})")
    #     """
    #     pass
    #
    # --------------------------------------------------------------------------------
    # async def update_term(self, term_id: UUID, form_data: dict[str, object]) -> None:
    #     """既存の用語を更新する。
    #
    #     Args:
    #         term_id: 更新対象の用語ID
    #         form_data: 更新データ
    #
    #     実装内容:
    #         1. form_data を TermUpdate に変換
    #         2. ApplicationService で更新
    #         3. 同義語の差分更新（削除 + 追加）
    #         4. State を更新
    #         5. reconcile() 実行
    #     """
    #     pass
    #
    # --------------------------------------------------------------------------------
    # async def delete_term(self, term_id: UUID) -> None:
    #     """用語を削除する。
    #
    #     Args:
    #         term_id: 削除対象の用語ID
    #
    #     実装内容:
    #         1. ApplicationService で削除（同義語はCASCADE削除）
    #         2. State から削除
    #         3. 選択状態をクリア（削除した用語が選択中の場合）
    #         4. reconcile() 実行
    #     """
    #     pass
    #
    # ================================================================================
    # ApplicationService インターフェース（参考）
    # ================================================================================
    #
    # ファイル: src/logic/application/term_application_service.py
    #
    # class TermApplicationService:
    #     """用語管理のApplicationService。
    #
    #     Repository と協調してビジネスロジックを実装します。
    #     """
    #
    #     def __init__(self, term_repo: TermRepository, synonym_repo: SynonymRepository):
    #         self._term_repo = term_repo
    #         self._synonym_repo = synonym_repo
    #
    #     async def create_term(self, data: TermCreate) -> TermRead:
    #         """用語を作成する。
    #
    #         Args:
    #             data: 作成データ
    #
    #         Returns:
    #             作成された用語
    #
    #         Raises:
    #             ValueError: キーが既に存在する場合
    #         """
    #         # キーの一意性チェック
    #         existing = await self._term_repo.find_by_key(data.key)
    #         if existing:
    #             raise ValueError(f"キー '{data.key}' は既に使用されています")
    #
    #         # 用語を作成
    #         term = await self._term_repo.create(data)
    #         return TermRead.model_validate(term)
    #
    #     async def create_synonyms(
    #         self, term_id: UUID, synonyms: list[str]
    #     ) -> list[SynonymRead]:
    #         """同義語を一括作成する。
    #
    #         Args:
    #             term_id: 用語ID
    #             synonyms: 同義語のテキストリスト
    #
    #         Returns:
    #             作成された同義語のリスト
    #         """
    #         created = []
    #         for text in synonyms:
    #             synonym_data = SynonymCreate(text=text, term_id=term_id)
    #             synonym = await self._synonym_repo.create(synonym_data)
    #             created.append(SynonymRead.model_validate(synonym))
    #         return created
    #
    #     async def update_term(self, term_id: UUID, data: TermUpdate) -> TermRead:
    #         """用語を更新する。"""
    #         term = await self._term_repo.update(term_id, data)
    #         if not term:
    #             raise ValueError(f"用語 ID {term_id} が見つかりません")
    #         return TermRead.model_validate(term)
    #
    #     async def delete_term(self, term_id: UUID) -> bool:
    #         """用語を削除する（同義語もCASCADE削除）。"""
    #         return await self._term_repo.delete(term_id)
    #
    #     async def get_term_by_id(self, term_id: UUID) -> TermRead | None:
    #         """IDで用語を取得する。"""
    #         term = await self._term_repo.find_by_id(term_id)
    #         return TermRead.model_validate(term) if term else None
    #
    #     async def list_terms(
    #         self, status: TermStatus | None = None
    #     ) -> list[TermRead]:
    #         """用語一覧を取得する（オプションでステータスフィルタ）。"""
    #         terms = await self._term_repo.list_all(status=status)
    #         return [TermRead.model_validate(t) for t in terms]
    #
    # ================================================================================
    # State への追加メソッド（参考）
    # ================================================================================
    #
    # ファイル: src/views/terms/state.py の TermsViewState クラスに追加
    #
    # def add_term(self, term: Term | TermRead) -> None:
    #     """新しい用語を追加する。
    #
    #     Args:
    #         term: 追加する用語
    #     """
    #     # SampleTerm に変換して追加（暫定）
    #     # 将来的には Term モデルを直接扱う
    #     sample_term = SampleTerm(
    #         id=term.id,
    #         key=term.key,
    #         title=term.title,
    #         description=term.description,
    #         status=SampleTermStatus(term.status.value),
    #         synonyms=term.synonyms if hasattr(term, 'synonyms') else [],
    #         source_url=term.source_url,
    #     )
    #     self.all_terms.append(sample_term)
    #
    # def update_term(self, updated_term: Term | TermRead) -> None:
    #     """既存の用語を更新する。"""
    #     for i, term in enumerate(self.all_terms):
    #         if term.id == updated_term.id:
    #             self.all_terms[i] = self._convert_to_sample_term(updated_term)
    #             break
    #
    # def remove_term(self, term_id: UUID) -> None:
    #     """用語を削除する。"""
    #     self.all_terms = [t for t in self.all_terms if t.id != term_id]
    #
    # ================================================================================
