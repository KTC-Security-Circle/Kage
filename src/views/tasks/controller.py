"""Tasks Controller.

View と Query/Ordering/Presenter を調停し状態を不変更新する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:  # 型チェック専用
    from collections.abc import Callable

from .components.shared.constants import STATUS_ORDER
from .ordering import ORDERING_MAP, apply_order
from .presenter import TaskCardVM, to_card_vm
from .state import TasksState

if TYPE_CHECKING:  # 型チェック専用
    from .query import TasksQuery


@dataclass
class TasksController:
    """イベント→状態→取得→並び替え→VM生成→通知を制御する調停役。"""

    _query: TasksQuery
    _on_change: Callable[[list[TaskCardVM]], None]
    _state: TasksState = field(default_factory=TasksState)

    @property
    def state(self) -> TasksState:
        """現在の状態を返す。"""
        return self._state

    # --- Public Events ---
    def set_keyword(self, keyword: str) -> None:
        self._update_and_render(self._state.update(keyword=keyword))

    def set_status(self, status: str | None) -> None:
        self._update_and_render(self._state.update(status=status))

    def set_sort(self, key: str, *, descending: bool) -> None:
        """ソート条件を更新する。

        Args:
            key: ソートキー
            descending: 降順にするか
        """
        self._update_and_render(self._state.update(sort_key=key, sort_desc=descending))

    def refresh(self) -> None:
        """外部からの再読み込み要求。"""
        self._update_and_render(self._state)

    def set_selected(self, task_id: str | None) -> None:
        """選択中のタスクIDを更新する。"""
        self._update_and_render(self._state.update(selected_id=task_id))

    def change_task_status(self, task_id: str, new_status: str) -> None:
        """タスクのステータスを変更し再描画する。

        InMemory実装では Query 側に更新APIを持たせ暫定対応。将来的にCommand層へ委譲予定。

        Args:
            task_id: 変更対象ID
            new_status: 新ステータス
        """
        try:
            # type: ignore[attr-defined] は update_item_status が存在しない実装向け抑止
            if hasattr(self._query, "update_item_status"):
                self._query.update_item_status(task_id, new_status)  # type: ignore[attr-defined]
                logger.debug("Changed task status id={} -> {}", task_id, new_status)
            else:
                logger.warning("Query does not support update_item_status; skipping")
        finally:
            # 反映
            self._update_and_render(self._state)

    # TODO: MVC整備後は Command/ApplicationService 層へ書き込み操作を委譲する。
    #       例: TaskApplicationService.change_status(cmd) にトランザクション管理/ドメイン検証を移管。
    # TODO: 検索入力は debounce / throttle を導入し過剰な再描画を抑制。
    # TODO: _update_and_render の失敗時にユーザー通知 (トースト/ダイアログ) を発火するエラーハンドリングを追加。

    # --- Query helpers for View ---
    def get_counts(self) -> dict[str, int]:
        """現在のキーワードフィルタでのステータス別件数を返す。"""
        counts: dict[str, int] = {}
        for status in STATUS_ORDER:
            counts[status] = len(self._query.list_items(self._state.keyword, status))
        return counts
        # TODO: counts は Query 側で集約できるようにするとクエリ回数を削減可能。
        #       例: get_counts(keyword) -> dict[status, count]

    def get_total_count(self) -> int:
        """現在のキーワードでの総件数。"""
        return len(self._query.list_items(self._state.keyword, None))

    # --- Internal orchestration ---
    def _update_and_render(self, new_state: TasksState) -> None:
        self._state = new_state
        items = self._query.list_items(new_state.keyword, new_state.status)
        strategy = ORDERING_MAP[new_state.sort_key]
        ordered = apply_order(items, strategy, descending=new_state.sort_desc)
        vm: list[TaskCardVM] = to_card_vm(ordered)
        logger.debug(
            "Render tasks count={} keyword='{}' status={} sort={} desc={}",
            len(vm),
            new_state.keyword,
            new_state.status,
            new_state.sort_key,
            new_state.sort_desc,
        )
        try:
            self._on_change(vm)
        except Exception as e:  # defensive
            logger.error(f"on_change callback failed: {e}")
            # TODO: ここでリカバリアクション (再試行/フォールバック) を検討し、View へユーザー向け通知を行う。
