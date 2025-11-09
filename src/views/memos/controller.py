"""MemosView のドメインロジックを保持するコントローラ。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from errors import NotFoundError
from models import MemoRead, MemoStatus

if TYPE_CHECKING:
    from uuid import UUID

    from .state import MemosViewState


_STATUS_ORDER: dict[MemoStatus, int] = {
    MemoStatus.INBOX: 0,
    MemoStatus.ACTIVE: 1,
    MemoStatus.IDEA: 2,
    MemoStatus.ARCHIVE: 3,
}


class MemoApplicationPort(Protocol):
    """MemoApplicationService の利用に必要なメソッドを限定したポート。"""

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        """メモを全件取得する。"""
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


@dataclass(slots=True)
class MemosController:
    """MemosView 用の状態操作とサービス呼び出しを集約する。"""

    memo_app: MemoApplicationPort
    state: MemosViewState

    def load_initial_memos(self) -> None:
        """初期表示に使用するメモ一覧を読み込む。"""
        memos = self.memo_app.get_all_memos(with_details=False)
        ordered = sorted(memos, key=self._memo_sort_key)
        self.state.set_all_memos(ordered)
        self.state.set_search_result("", None)

    def update_tab(self, tab: MemoStatus | None) -> None:
        """タブ変更時に状態を更新する。"""
        self.state.set_current_tab(tab)

    def update_search(self, query: str) -> None:
        """検索クエリを更新し結果を反映する。"""
        normalized = query.strip()
        if not normalized:
            self.state.set_search_result("", None)
            return

        try:
            results = self.memo_app.search(normalized, with_details=False, status=self.state.current_tab)
        except NotFoundError:
            # 検索に一致しない場合は例外を無視して空配列として扱う
            results = []
        self.state.set_search_result(normalized, results)

    def clear_search(self) -> None:
        """検索条件をリセットする。"""
        self.state.set_search_result("", None)

    def select_memo(self, memo: MemoRead | None) -> None:
        """メモ選択を更新する。"""
        memo_id = memo.id if memo is not None else None
        self.state.set_selected_memo(memo_id)

    def select_memo_by_id(self, memo_id: UUID | None) -> None:
        """メモIDを直接指定して選択状態を更新する。"""
        self.state.set_selected_memo(memo_id)

    def current_memos(self) -> list[MemoRead]:
        """現在の表示条件に基づくメモ一覧を返す。"""
        return self.state.derived_memos()

    def status_counts(self) -> dict[MemoStatus, int]:
        """ステータス別件数を返す。"""
        return self.state.counts_by_status()

    def current_selection(self) -> MemoRead | None:
        """選択中のメモを返す。"""
        return self.state.selected_memo()

    @staticmethod
    def _memo_sort_key(memo: MemoRead) -> int:
        """状態ごとに安定した順序を提供する。"""
        return _STATUS_ORDER.get(memo.status, 99)
