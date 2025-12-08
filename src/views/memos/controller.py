"""Memo Controller Layer.

【責務】
    Controller層はMVPパターンにおける「Presenter/Controller」の役割を担う。
    ユースケースの実行、ApplicationServiceの呼び出し、State更新の調整を行う。

    - ユースケースメソッドの提供（load, search, select, CRUD）
    - MemoApplicationPortを通じたApplicationService呼び出し
    - Stateへの状態反映とreconcile実行
    - 検索クエリの正規化（SearchQueryNormalizerを使用）
    - 並び順の適用（orderingモジュールを使用）
    - 例外処理とログ出力（観測性の向上）

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持と派生計算 → State
    - UIレイアウトの決定 → View
    - データの永続化 → ApplicationService/Repository

【設計の拡張ポイント】
    - SearchQueryNormalizer: 検索クエリの正規化戦略（Strategy パターン）
    - MemoApplicationPort: ApplicationServiceの抽象化（依存性逆転）
    - CRUD メソッド骨格: 統合フェーズで実装予定

【アーキテクチャ上の位置づけ】
    View → Controller → ApplicationService
                ↓           (MemoApplicationPort)
              State
                ↓
            reconcile()

【主な機能】
    - 初期メモ一覧の読み込みとソート
    - タブ切り替え時の状態更新
    - 検索実行と結果反映
    - メモ選択状態の管理
    - ステータス別件数の提供
    - CRUD操作（create/update/delete）の実行
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from loguru import logger

from errors import NotFoundError
from logic.application.memo_ai_job_queue import MemoAiJobSnapshot  # noqa: TC001 - runtime dependency
from models import AiSuggestionStatus, MemoRead, MemoStatus, MemoUpdate, TagRead, TaskRead

from .ordering import sort_memos
from .query import SearchQueryNormalizer

if TYPE_CHECKING:
    from uuid import UUID

    from .state import MemosViewState


class TagApplicationPort(Protocol):
    """TagApplicationService の利用に必要なメソッドを限定したポート。"""

    def get_all_tags(self) -> list[TagRead]:
        """全タグ取得"""
        ...


class MemoApplicationPort(Protocol):
    """MemoApplicationService の利用に必要なメソッドを限定したポート。"""

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        """メモを全件取得する。"""
        ...

    def get_by_id(self, memo_id: UUID, *, with_details: bool = False) -> MemoRead:
        """ID で単一メモを取得する。"""
        ...

    def search(
        self,
        query: str,
        *,
        with_details: bool = False,
        status: MemoStatus | None = None,
    ) -> list[MemoRead]:
        """検索条件に一致するメモを返す。"""
        ...

    def create(
        self,
        title: str,
        content: str,
        *,
        status: MemoStatus = MemoStatus.INBOX,
    ) -> MemoRead:
        """メモを作成する。"""
        ...

    def update(self, memo_id: UUID, update_data: MemoUpdate) -> MemoRead:
        """メモを更新する。"""
        ...

    def delete(self, memo_id: UUID) -> bool:
        """メモを削除する。"""
        ...

    def enqueue_ai_generation(self, memo_id: UUID) -> MemoAiJobSnapshot:
        """AIタスク生成ジョブを登録する。"""
        ...

    def get_ai_job_snapshot(self, job_id: UUID) -> MemoAiJobSnapshot:
        """AＩジョブの状態を取得する。"""
        ...

    def sync_tags(self, memo_id: UUID, tag_ids: list[UUID]) -> MemoRead:
        """メモのタグを同期する。"""
        ...

    def approve_ai_tasks(self, memo_id: UUID, task_ids: list[UUID]) -> list[TaskRead]:
        """Draftタスクを承認する。"""
        ...

    def delete_ai_task(self, memo_id: UUID, task_id: UUID) -> None:
        """Draftタスクを削除する。"""
        ...

    def create_ai_task(
        self,
        memo_id: UUID,
        *,
        title: str,
        description: str | None = None,
        route: str | None = None,
        project_title: str | None = None,
    ) -> TaskRead:
        """Draftタスクを新規作成する。"""
        ...

    def update_ai_task(
        self,
        task_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> TaskRead:
        """Draftタスクを更新する。"""
        ...


@dataclass(slots=True)
class MemosController:
    """MemosView 用の状態操作とサービス呼び出しを集約する。"""

    memo_app: MemoApplicationPort
    state: MemosViewState
    tag_app: TagApplicationPort | None = None
    query_normalizer: SearchQueryNormalizer = field(default_factory=SearchQueryNormalizer)

    def load_initial_memos(self) -> None:
        """初期表示に使用するメモ一覧を読み込む。"""
        memos = self.memo_app.get_all_memos(with_details=False)
        ordered = sort_memos(memos)
        self.state.set_all_memos(ordered)
        self.state.set_search_result("", None)
        self.state.reconcile()

    def update_tab(self, tab: MemoStatus | None) -> None:
        """タブ変更時に状態を更新する。"""
        self.state.set_current_tab(tab)
        self.state.reconcile()

    def update_search(self, query: str) -> None:
        """検索クエリを更新し結果を反映する。"""
        normalized = self.query_normalizer.normalize(query)
        if not normalized:
            self.state.set_search_result("", None)
            self.state.reconcile()
            return

        try:
            results = self.memo_app.search(normalized, with_details=False, status=self.state.current_tab)
        except NotFoundError:
            # 検索に一致しない場合は例外を無視して空配列として扱う
            logger.debug(f"No memos found for query: '{normalized}'")
            results = []
        self.state.set_search_result(normalized, results)
        self.state.reconcile()

    def clear_search(self) -> None:
        """検索条件をリセットする。"""
        self.state.set_search_result("", None)
        self.state.reconcile()

    def select_memo(self, memo: MemoRead | None) -> None:
        """メモ選択を更新する。"""
        memo_id = memo.id if memo is not None else None
        self.state.set_selected_memo(memo_id)
        self.state.reconcile()

    def select_memo_by_id(self, memo_id: UUID | None) -> None:
        """メモIDを直接指定して選択状態を更新する。"""
        self.state.set_selected_memo(memo_id)
        self.state.reconcile()

    def current_memos(self) -> list[MemoRead]:
        """現在の表示条件に基づくメモ一覧を返す。"""
        return self.state.derived_memos()

    def status_counts(self) -> dict[MemoStatus, int]:
        """ステータス別件数を返す。"""
        return self.state.counts_by_status()

    def current_selection(self) -> MemoRead | None:
        """選択中のメモを返す。"""
        return self.state.selected_memo()

    def enqueue_ai_generation(self, memo_id: UUID) -> MemoAiJobSnapshot:
        """AI生成処理をキューに登録し、最新メモ情報をStateへ反映する。"""
        snapshot = self.memo_app.enqueue_ai_generation(memo_id)
        updated = self.memo_app.get_by_id(memo_id, with_details=True)
        self.state.upsert_memo(updated)
        self.state.reconcile()
        return snapshot

    def get_ai_job_snapshot(self, job_id: UUID) -> MemoAiJobSnapshot:
        """AIジョブの状態を取得する。"""
        return self.memo_app.get_ai_job_snapshot(job_id)

    def refresh_memo(self, memo_id: UUID) -> MemoRead:
        """指定メモを再取得してStateへ反映する。"""
        refreshed = self.memo_app.get_by_id(memo_id, with_details=True)
        self.state.upsert_memo(refreshed)
        self.state.reconcile()
        return refreshed

    def mark_memo_archived(self, memo_id: UUID) -> MemoRead:
        """承認後にメモをアーカイブ扱いに更新する。"""
        updated = self.memo_app.update(
            memo_id,
            MemoUpdate(status=MemoStatus.ARCHIVE, ai_suggestion_status=AiSuggestionStatus.REVIEWED),
        )
        self.state.upsert_memo(updated)
        self.state.reconcile()
        return updated

    def approve_ai_tasks(self, memo_id: UUID, task_ids: list[UUID]) -> list[TaskRead]:
        """Draftタスクを承認する。"""
        approved = self.memo_app.approve_ai_tasks(memo_id, task_ids)
        self.refresh_memo(memo_id)
        return approved

    def delete_ai_task(self, memo_id: UUID, task_id: UUID) -> None:
        """Draftタスクを削除する。"""
        self.memo_app.delete_ai_task(memo_id, task_id)
        self.refresh_memo(memo_id)

    def create_ai_task(
        self,
        memo_id: UUID,
        *,
        title: str,
        description: str | None = None,
        route: str | None = None,
        project_title: str | None = None,
    ) -> TaskRead:
        """Draftタスクを新規作成しStateへ反映する。"""
        created = self.memo_app.create_ai_task(
            memo_id,
            title=title,
            description=description,
            route=route,
            project_title=project_title,
        )
        self.refresh_memo(memo_id)
        return created

    def update_ai_task(
        self,
        task_id: UUID,
        *,
        memo_id: UUID,
        title: str | None = None,
        description: str | None = None,
    ) -> TaskRead:
        """Draftタスクを更新してStateを再同期する。"""
        updated = self.memo_app.update_ai_task(task_id, title=title, description=description)
        self.refresh_memo(memo_id)
        return updated

    # --- CRUD operations ---

    def create_memo(
        self,
        title: str,
        content: str,
        *,
        status: MemoStatus = MemoStatus.INBOX,
    ) -> MemoRead:
        """新しいメモを作成する。"""
        created = self.memo_app.create(title=title, content=content, status=status)
        self.state.upsert_memo(created)
        self.state.set_all_memos(sort_memos(self.state.all_memos))
        self.state.set_selected_memo(created.id)
        if self.state.search_query:
            self._refresh_search_results()
        self.state.reconcile()
        return created

    def update_memo(
        self,
        memo_id: UUID,
        *,
        title: str | None = None,
        content: str | None = None,
        status: MemoStatus | None = None,
        ai_status: AiSuggestionStatus | None = None,
    ) -> MemoRead:
        """既存のメモを更新する。"""
        update_payload = MemoUpdate()
        if title is not None:
            update_payload.title = title
        if content is not None:
            update_payload.content = content
        if status is not None:
            update_payload.status = status
        if ai_status is not None:
            update_payload.ai_suggestion_status = ai_status
        updated = self.memo_app.update(memo_id, update_payload)
        self.state.upsert_memo(updated)
        self.state.set_all_memos(sort_memos(self.state.all_memos))
        if self.state.search_query:
            self._refresh_search_results()
        self.state.reconcile()
        return updated

    def delete_memo(self, memo_id: UUID) -> None:
        """メモを削除する。"""
        success = self.memo_app.delete(memo_id)
        if not success:
            msg = f"メモが見つかりません (id={memo_id})"
            raise NotFoundError(msg)

        remaining = [memo for memo in self.state.all_memos if memo.id != memo_id]
        self.state.set_all_memos(sort_memos(remaining))
        if self.state.selected_memo_id == memo_id:
            self.state.set_selected_memo(None)

        if self.state.search_results is not None:
            filtered = [memo for memo in self.state.search_results if memo.id != memo_id]
            self.state.set_search_result(self.state.search_query, filtered)

        if self.state.search_query:
            self._refresh_search_results()

        self.state.reconcile()

    def sync_tags(self, memo_id: UUID, tag_ids: list[UUID]) -> MemoRead:
        """メモにタグを同期する。

        Args:
            memo_id: メモID
            tag_ids: 設定するタグIDのリスト

        Returns:
            MemoRead: 更新されたメモ
        """
        updated = self.memo_app.sync_tags(memo_id, tag_ids)
        self.state.upsert_memo(updated)
        self.state.set_all_memos(sort_memos(self.state.all_memos))
        if self.state.search_query:
            self._refresh_search_results()
        self.state.reconcile()
        return updated

    def _refresh_search_results(self) -> None:
        """現在のクエリに基づいて検索結果を再取得する。"""
        query = self.state.search_query
        if not query:
            return

        try:
            results = self.memo_app.search(
                query,
                with_details=False,
                status=self.state.current_tab,
            )
        except NotFoundError:
            results = []

        self.state.set_search_result(query, results)

    # --- Tag operations ---

    def load_tags(self) -> None:
        """全タグを読み込む。"""
        if self.tag_app is None:
            logger.warning("TagApplicationPort not provided, skipping tag loading")
            return
        tags = self.tag_app.get_all_tags()
        self.state.set_all_tags(tags)

    def get_all_tags(self) -> list[TagRead]:
        """現在の全タグを返す。"""
        return self.state.all_tags
