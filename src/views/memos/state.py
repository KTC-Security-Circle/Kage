"""状態管理モジュール.

MemosView で使用する状態データおよび派生データ計算を切り出す。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from models import MemoRead, MemoStatus

if TYPE_CHECKING:
    from uuid import UUID


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

    def set_all_memos(self, memos: list[MemoRead]) -> None:
        """全メモ一覧を更新する。

        Args:
            memos: 表示対象となるメモのシーケンス
        """
        self.all_memos = list(memos)
        # 一貫性のため、全件からインデックスを再構築
        self._rebuild_index()
        self._reset_selection_if_missing()

    def set_search_result(self, query: str, results: list[MemoRead] | None) -> None:
        """検索クエリと結果を保存する。

        Args:
            query: 入力された検索クエリ
            results: 検索結果。`None` の場合は検索を無効化した扱いとなる。
        """
        self.search_query = query
        self.search_results = results
        self._reset_selection_if_missing()

    def set_current_tab(self, tab: MemoStatus | None) -> None:
        """アクティブなタブを設定する。

        Args:
            tab: 選択したタブに対応するステータス
        """
        self.current_tab = tab
        self.selected_memo_id = None
        self._reset_selection_if_missing()

    def set_selected_memo(self, memo_id: UUID | None) -> None:
        """選択中のメモIDを更新する。

        Args:
            memo_id: 選択したメモのUUID
        """
        self.selected_memo_id = memo_id
        self._reset_selection_if_missing()

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

    def _filter_by_tab(self, memos: list[MemoRead]) -> list[MemoRead]:
        """タブの状態に応じてメモをフィルタリングする。"""
        if self.current_tab is None:
            return list(memos)
        return [memo for memo in memos if memo.status == self.current_tab]

    def _reset_selection_if_missing(self) -> None:
        """選択中のメモが現在の一覧に存在しない場合は選択を解除する。"""
        if self.selected_memo_id is None:
            return
        if not any(memo.id == self.selected_memo_id for memo in self.derived_memos()):
            self.selected_memo_id = None

    def _rebuild_index(self) -> None:
        """all_memos から id -> MemoRead のインデックスを再構築する。"""
        self._by_id = {memo.id: memo for memo in self.all_memos}

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
        # 選択が外れる条件は従来通りに委ねる
        self._reset_selection_if_missing()
