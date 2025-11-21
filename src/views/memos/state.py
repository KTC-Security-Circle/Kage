"""Memo State Layer.

【責務】
    State層は表示状態の保持と派生データ計算を担う。
    Viewが必要とする全ての状態を一元管理し、整合性を保証する。

    - 表示状態の保持（current_tab, search_query, selected_memo_id 等）
    - 全メモデータの保持（all_memos）
    - 検索結果の保持（search_results）
    - 派生データの計算（フィルタリング済みメモ一覧、ステータス別件数）
    - メモIDインデックスの管理（高速検索用）
    - 選択状態の整合性保証（reconcile）

【責務外（他層の担当）】
    - データの取得・永続化 → Controller/ApplicationService
    - UI要素の構築 → Presenter
    - イベントハンドリング → View
    - 並び順の決定 → ordering モジュール

【設計上の特徴】
    - Immutableなデータクラス（dataclass with slots）
    - 副作用を排除したsetter設計（reconcile()で整合性保証）
    - インデックス（_by_id）による高速検索
    - 派生データのメソッド化（derived_memos, counts_by_status）

【アーキテクチャ上の位置づけ】
    Controller → State.set_xxx()
                    ↓
                State.reconcile()
                    ↓
    View → State.derived_memos()
        → State.selected_memo()
        → State.counts_by_status()

【主な機能】
    - タブ・検索条件に基づくメモ一覧の派生
    - 選択メモの高速取得（O(1)）
    - ステータス別件数の集計
    - 選択整合性の自動調整（reconcile）
    - 単一メモの追加・更新（upsert_memo）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from models import AiSuggestionStatus, MemoRead, MemoStatus

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


@dataclass(slots=True)
class AiSuggestedTask:
    """AI提案タスクのUI状態を表すデータ。"""

    task_id: str
    title: str
    description: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    due_date: datetime | None = None


@dataclass(slots=True)
class MemoAiFlowState:
    """メモごとのAI提案フロー状態。"""

    status_override: AiSuggestionStatus | None = None
    generated_tasks: list[AiSuggestedTask] = field(default_factory=list)
    selected_task_ids: set[str] = field(default_factory=set)
    editing_task_id: str | None = None
    is_generating: bool = False
    job_id: UUID | None = None
    job_status: str | None = None
    error_message: str | None = None


@dataclass(slots=True)
class MemosViewState:
    """MemosView の表示状態を管理するデータクラス。

    View 自体は UI 制御のみに集中させ、状態の保持と派生計算をこのクラスへ委譲する。
    """

    current_tab: MemoStatus | None = MemoStatus.INBOX
    search_query: str = ""
    all_memos: list[MemoRead] = field(default_factory=list)
    search_results: list[MemoRead] | None = None
    selected_memo_id: UUID | None = None
    # id -> MemoRead のインデックス。全メモ(all_memos)に対して構築する。
    _by_id: dict[UUID, MemoRead] = field(default_factory=dict, repr=False)
    _ai_flow: dict[UUID, MemoAiFlowState] = field(default_factory=dict, repr=False)

    def set_all_memos(self, memos: list[MemoRead]) -> None:
        """全メモ一覧を更新する。

        Args:
            memos: 表示対象となるメモのシーケンス
        """
        self.all_memos = list(memos)
        # 一貫性のため、全件からインデックスを再構築
        self._rebuild_index()

    def set_search_result(self, query: str, results: list[MemoRead] | None) -> None:
        """検索クエリと結果を保存する。

        Args:
            query: 入力された検索クエリ
            results: 検索結果。`None` の場合は検索を無効化した扱いとなる。
        """
        self.search_query = query
        self.search_results = results

    def set_current_tab(self, tab: MemoStatus | None) -> None:
        """アクティブなタブを設定する。

        Args:
            tab: 選択したタブに対応するステータス
        """
        self.current_tab = tab
        self.selected_memo_id = None

    def set_selected_memo(self, memo_id: UUID | None) -> None:
        """選択中のメモIDを更新する。

        Args:
            memo_id: 選択したメモのUUID
        """
        self.selected_memo_id = memo_id

    def derived_memos(self) -> list[MemoRead]:
        """現在のタブと検索条件に基づくメモ一覧を返す。

        Returns:
            表示対象のメモ一覧
        """
        base = self.search_results if self.search_results is not None else self.all_memos
        return self._filter_by_tab(base)

    def counts_by_status(self) -> dict[MemoStatus, int]:
        """全メモからステータスごとの件数を算出する。

        Returns:
            ステータス別件数を表す辞書
        """
        counts: dict[MemoStatus, int] = {
            MemoStatus.INBOX: 0,
            MemoStatus.ACTIVE: 0,
            MemoStatus.IDEA: 0,
            MemoStatus.ARCHIVE: 0,
        }
        for memo in self.all_memos:
            if memo.status in counts:
                counts[memo.status] += 1
        return counts

    def selected_memo(self) -> MemoRead | None:
        """選択中のメモを取得する。

        Returns:
            選択されている `MemoRead`。存在しない場合は `None`。
        """
        if self.selected_memo_id is None:
            return None
        # O(1) での取得を優先（all_memos に対するインデックス）
        return self._by_id.get(self.selected_memo_id)

    def memo_by_id(self, memo_id: UUID) -> MemoRead | None:
        """指定IDのメモを返す。"""
        return self._by_id.get(memo_id)

    def _filter_by_tab(self, memos: list[MemoRead]) -> list[MemoRead]:
        """タブの状態に応じてメモをフィルタリングする。"""
        if self.current_tab is None:
            return list(memos)
        return [memo for memo in memos if memo.status == self.current_tab]

    def reconcile(self) -> None:
        """選択状態の整合性を確保する。

        選択中のメモが現在の表示対象に存在しない場合、選択を解除する。
        状態変更後に Controller から明示的に呼び出される。
        """
        if self.selected_memo_id is None:
            return
        if not any(memo.id == self.selected_memo_id for memo in self.derived_memos()):
            self.selected_memo_id = None

    def _rebuild_index(self) -> None:
        """all_memos から id -> MemoRead のインデックスを再構築する。"""
        self._by_id = {memo.id: memo for memo in self.all_memos}

    # --- AI提案UI状態の管理 ---

    def ai_flow_state_for(self, memo_id: UUID) -> MemoAiFlowState:
        """指定メモのAI提案状態を取得（未作成なら初期化）。"""
        if memo_id not in self._ai_flow:
            self._ai_flow[memo_id] = MemoAiFlowState()
        return self._ai_flow[memo_id]

    def clear_ai_flow_state(self, memo_id: UUID) -> None:
        """AI提案状態をリセットする。"""
        self._ai_flow.pop(memo_id, None)

    def set_ai_status_override(self, memo_id: UUID, status: AiSuggestionStatus | None) -> None:
        """UI表示用のAIステータスを上書き設定する。"""
        self.ai_flow_state_for(memo_id).status_override = status

    def effective_ai_status(self, memo: MemoRead) -> AiSuggestionStatus:
        """表示に用いるAIステータスを返す。"""
        state = self._ai_flow.get(memo.id)
        if state and state.status_override is not None:
            return state.status_override
        return getattr(memo, "ai_suggestion_status", AiSuggestionStatus.NOT_REQUESTED)

    def set_generated_tasks(self, memo_id: UUID, tasks: list[AiSuggestedTask]) -> None:
        """生成済みタスク一覧を更新する。"""
        state = self.ai_flow_state_for(memo_id)
        state.generated_tasks = list(tasks)
        state.selected_task_ids = {task.task_id for task in tasks}
        state.is_generating = False

    def toggle_task_selection(self, memo_id: UUID, task_id: str) -> None:
        """タスクの選択状態をトグルする。"""
        state = self.ai_flow_state_for(memo_id)
        if task_id in state.selected_task_ids:
            state.selected_task_ids.remove(task_id)
        else:
            state.selected_task_ids.add(task_id)

    def track_ai_job(self, memo_id: UUID, job_id: UUID, status: str) -> None:
        """ジョブ追跡情報を設定する。"""
        state = self.ai_flow_state_for(memo_id)
        state.job_id = job_id
        state.job_status = status
        state.error_message = None
        state.is_generating = True

    def update_job_status(self, memo_id: UUID, *, status: str, error: str | None = None) -> None:
        """ジョブ状態を更新する。"""
        state = self.ai_flow_state_for(memo_id)
        state.job_status = status
        state.error_message = error
        if error:
            state.is_generating = False

    def get_selected_tasks(self, memo_id: UUID) -> list[AiSuggestedTask]:
        """選択済みタスクを返す。"""
        state = self.ai_flow_state_for(memo_id)
        return [task for task in state.generated_tasks if task.task_id in state.selected_task_ids]

    # --- Priority C: optional helper for single-memo updates ---
    def upsert_memo(self, memo: MemoRead) -> None:
        """単一メモを all_memos とインデックスに反映する。

        既存IDなら置換、未登録なら追加する（順序は既存の末尾）。
        UIの安定順序が必要な場合は、呼び出し側で再ソートする。
        """
        # インデックス更新
        self._by_id[memo.id] = memo
        # リスト反映
        for i, m in enumerate(self.all_memos):
            if m.id == memo.id:
                self.all_memos[i] = memo
                break
        else:
            self.all_memos.append(memo)
