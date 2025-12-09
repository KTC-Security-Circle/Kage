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
    - 依存性注入: ApplicationServiceのモック注入によるテスト容易性

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
    - CRUD操作
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, TypeVar

from loguru import logger

from errors import NotFoundError
from models import TermRead, TermStatus, TermUpdate

from .query import SearchQueryNormalizer
from .utils import sort_terms

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from logic.application.terminology_application_service import (
        TerminologyApplicationService,
    )

    from .state import TermsViewState

T = TypeVar("T")


class TermFormData(TypedDict, total=False):
    """用語作成・更新フォームデータの型定義。

    ApplicationServiceに渡すフォームデータの構造を型安全に定義する。
    total=False により、すべてのキーがオプショナルとして扱われる。
    実際の必須性はバリデーション層で検証される。

    Attributes:
        key: 用語の一意キー（必須）
        title: 用語のタイトル（必須）
        description: 用語の説明（任意）
        status: 用語のステータス（TermStatus または str）
        source_url: 参照元URL（任意）
        synonyms: 同義語のリスト（任意）
    """

    key: str
    title: str
    description: str | None
    status: str | TermStatus
    source_url: str | None
    synonyms: list[str]


class TermApplicationPort(Protocol):
    """用語管理ApplicationServiceの抽象インターフェース。"""

    def list_terms(self, status: TermStatus | None = None) -> list[TermRead]:  # pragma: no cover - interface
        """用語一覧を取得する。"""
        ...

    def search_terms(self, query: str) -> list[TermRead]:  # pragma: no cover - interface
        """用語を検索する。"""
        ...

    def sync_tags(self, term_id: UUID, tag_ids: list[UUID]) -> TermRead:  # pragma: no cover - interface
        """用語のタグを同期する。"""
        ...

    def create_term(self, form_data: TermFormData) -> TermRead:  # pragma: no cover - interface
        """用語を作成する。"""
        ...

    def update_term(self, term_id: UUID, form_data: TermFormData) -> TermRead:  # pragma: no cover - interface
        """用語を更新する。"""
        ...

    def delete_term(self, term_id: UUID) -> bool:  # pragma: no cover - interface
        """用語を削除する。"""
        ...


@dataclass(slots=True)
class TermsController:
    """TermsView 用の状態操作とサービス呼び出しを集約する。"""

    state: TermsViewState
    service: TermApplicationPort
    query_normalizer: SearchQueryNormalizer = field(default_factory=SearchQueryNormalizer)
    _tag_service: Any = field(default=None)  # TagApplicationService

    def get_all_tags(self) -> list[Any]:
        """全タグを取得する。

        Returns:
            タグのリスト
        """
        if self._tag_service is None:
            return []
        try:
            return self._tag_service.get_all_tags()
        except Exception as e:
            logger.error(f"Failed to get all tags: {e}")
            return []

    async def sync_tags(self, term_id: UUID, tag_ids: list[UUID]) -> TermRead:
        """用語のタグを同期し、更新された用語を返す。

        Args:
            term_id: 用語ID
            tag_ids: タグIDのリスト

        Returns:
            TermRead: タグが同期された用語

        Raises:
            Exception: タグ同期に失敗した場合
        """
        try:
            updated_term = await self._call_service(self.service.sync_tags, term_id, tag_ids)
        except Exception as e:
            logger.error(f"Failed to sync tags for term {term_id}: {e}")
            raise
        else:
            # Stateを更新（タグ情報を含む最新データに更新）
            self.state.upsert_term(updated_term)
            logger.info(f"用語 {term_id} のタグを同期しました")
            return updated_term

    async def load_initial_terms(self) -> None:
        """初期表示に使用する用語一覧を読み込む。"""
        logger.info("Loading initial terms")
        terms = await self._call_service(self.service.list_terms)
        ordered = sort_terms(terms)
        self.state.set_all_terms(ordered)
        self.state.set_search_result("", None)
        logger.info("Loaded {} terms", len(terms))

    def update_tab(self, tab: TermStatus) -> None:
        """タブ変更時に状態を更新する。"""
        logger.debug("Switching to tab: {}", tab)
        self.state.set_current_tab(tab)

    async def update_search(self, query: str) -> None:
        """検索クエリを更新し結果を反映する。"""
        normalized = self.query_normalizer.normalize(query)
        logger.debug("Search query: {}", normalized.normalized)

        if not normalized.normalized:
            self.state.set_search_result("", None)
            return

        results = await self._perform_search(normalized.normalized)
        self.state.set_search_result(normalized.normalized, results)

    def select_term(self, term_id: UUID | None) -> None:
        """用語を選択する。"""
        logger.debug("Selecting term: {}", term_id)
        self.state.set_selected_term(term_id)

    def get_counts(self) -> dict[TermStatus, int]:
        """ステータス別の用語件数を取得する。"""
        return self.state.counts_by_status

    async def create_term(self, form_data: TermFormData) -> TermRead:
        """新しい用語を作成し、状態を更新する。"""
        logger.info("Creating term: {}", form_data.get("key"))
        created_term = await self._call_service(self.service.create_term, form_data)
        self.state.upsert_term(created_term)
        logger.info("Created term: {} (ID: {})", created_term.key, created_term.id)
        return created_term

    async def update_term(self, term_id: UUID, form_data: TermFormData) -> TermRead:
        """既存の用語を更新する。"""
        logger.info("Updating term: {}", term_id)
        updated_term = await self._call_service(self.service.update_term, term_id, form_data)
        self.state.upsert_term(updated_term)
        logger.info("Updated term: {} (ID: {})", updated_term.key, updated_term.id)
        return updated_term

    async def delete_term(self, term_id: UUID) -> bool:
        """用語を削除する。"""
        logger.info("Deleting term: {}", term_id)
        success = await self._call_service(self.service.delete_term, term_id)

        if success:
            self.state.all_terms = [t for t in self.state.all_terms if t.id != term_id]
            if self.state.search_results is not None:
                self.state.search_results = [t for t in self.state.search_results if t.id != term_id]
            self.state.rebuild_index()
            if self.state.selected_term_id == term_id:
                self.state.selected_term_id = None
            logger.info("Deleted term: {}", term_id)

        return success

    async def _perform_search(self, query: str) -> list[TermRead]:
        """検索を実行する。"""
        results = await self._call_service(self.service.search_terms, query)
        return sort_terms(results)

    async def _call_service(self, func: Callable[..., T], *args: object, **kwargs: object) -> T:
        """ブロッキングなサービス呼び出しをスレッドで実行する。"""
        return await asyncio.to_thread(func, *args, **kwargs)


class TerminologyApplicationPortAdapter(TermApplicationPort):
    """TerminologyApplicationService を TermApplicationPort に適合させる。"""

    def __init__(self, service: TerminologyApplicationService) -> None:
        self._service = service

    def list_terms(self, status: TermStatus | None = None) -> list[TermRead]:
        try:
            if status:
                return self._service.search(query=None, status=status)
            return self._service.get_all()
        except NotFoundError:
            logger.info("TerminologyApplicationService returned no records.")
            return []

    def search_terms(self, query: str) -> list[TermRead]:
        return self._service.search(query=query)

    def create_term(self, form_data: TermFormData) -> TermRead:
        status = _parse_status(form_data.get("status"), default=TermStatus.DRAFT)
        description = _clean_text(form_data.get("description"))
        source_url = _clean_text(form_data.get("source_url"))
        key = _clean_text(form_data.get("key"), default="") or ""
        title = _clean_text(form_data.get("title"), default="") or ""
        return self._service.create(
            key=key,
            title=title,
            description=description,
            status=status or TermStatus.DRAFT,
            source_url=source_url,
        )

    def update_term(self, term_id: UUID, form_data: TermFormData) -> TermRead:
        update_model = TermUpdate(
            key=_clean_text(form_data.get("key")),
            title=_clean_text(form_data.get("title")),
            description=_clean_text(form_data.get("description")),
            status=_parse_status(form_data.get("status")),
            source_url=_clean_text(form_data.get("source_url")),
        )
        return self._service.update(term_id, update_model)

    def delete_term(self, term_id: UUID) -> bool:
        return self._service.delete(term_id)

    def sync_tags(self, term_id: UUID, tag_ids: list[UUID]) -> TermRead:
        return self._service.sync_tags(term_id, tag_ids)


def _parse_status(value: str | TermStatus | None, *, default: TermStatus | None = None) -> TermStatus | None:
    """フォームから渡されたステータス値を TermStatus に変換する。"""
    if isinstance(value, TermStatus):
        return value
    if isinstance(value, str) and value:
        try:
            return TermStatus(value)
        except ValueError:
            logger.warning("Unknown term status value: {}", value)
            return default
    return default


def _clean_text(value: str | None, *, default: str | None = None) -> str | None:
    """文字列フィールドをトリムし、空文字の場合はデフォルト値を返す。"""
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default
