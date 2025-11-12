"""Tasks View (MVP構成: View層)。

旧カンバン実装を廃止し、MemosView と同等の責務分離 (State / Controller / Presenter / Query / Ordering) を導入。

【責務】
    - レイアウト構築と最低限のイベント配線
    - Controller への委譲と差分再描画
    - BaseView のエラーハンドリング/ローディング利用

【非責務】
    - データ取得 (Query)
    - 並び替え戦略 (ordering)
    - 状態保持と不変更新 (state)
    - 表示用VM生成 (presenter)

初期段階では InMemoryTasksQuery によるモックデータのみを扱う。
後続で ApplicationService 連携へ切り替え可能な構造。
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.shared.base_view import BaseView
from views.shared.components import create_page_header

from .components.detail_panel import DetailPanelProps, TaskDetailPanel
from .components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS
from .components.task_card import TaskCardData
from .components.task_list import TaskList, TaskListProps
from .controller import TasksController
from .presenter import to_detail_from_card
from .query import InMemoryTasksQuery, TasksQuery

if TYPE_CHECKING:
    from .presenter import TaskCardVM
    from .state import TasksState


class TasksView(BaseView):
    """タスク管理のメインビュー (新MVP構成)。

    検索 / ステータスフィルタ / 並び替え / 降順切替 + リスト表示の最小UIを提供。
    """

    def __init__(self, page: ft.Page, *, query: TasksQuery | None = None) -> None:
        """コンストラクタ。

        Args:
            page: Fletページ
            query: テスト差し替え用の Query 実装
        """
        super().__init__(page)
        seed = _default_seed_data()
        self._query: TasksQuery = query or InMemoryTasksQuery(seed)
        self._controller = TasksController(_query=self._query, _on_change=self._on_view_model_change)
        self._list: ft.ListView | None = None  # deprecated: kept for compatibility
        self._status_dropdown: ft.Dropdown | None = None
        self._sort_dropdown: ft.Dropdown | None = None
        self._desc_switch: ft.Switch | None = None
        self._search_field: ft.TextField | None = None
        self._tabs: ft.Tabs | None = None
        self._current_vm: list[TaskCardVM] = []
        # Components
        self._list_comp = TaskList(TaskListProps(on_item_click=self._on_item_clicked_id))
        self._detail_comp = TaskDetailPanel(DetailPanelProps(on_status_change=self._on_status_change))
        logger.info("TasksView initialized with MVP structure")
        # 初期描画データ
        self._controller.refresh()

    # BaseView から呼ばれる
    def build_content(self) -> ft.Control:
        """UIコンテンツを構築する。"""
        # TODO: MVC化に伴い InMemoryQuery を ApplicationService 経由の取得に置き換える。
        # TODO: ツールバーに「新規/編集/削除」アクションを追加。編集は右ペイン内インラインまたはモーダル。
        # TODO: アクセシビリティ改善 (ショートカット/フォーカス移動/スクリーンリーダー対応)。
        # 総件数は Controller から取得（キーワードフィルタを考慮）
        total_count = 0
        try:
            total_count = self._controller.get_total_count()
        except Exception:
            # InMemoryQuery 以外の実装に差し替えた場合でも安全に表示
            total_count = len(self._current_vm)

        header = create_page_header(
            title="タスク",
            subtitle=f"GTDベースのタスク管理 ({total_count}件)",
        )

        self._search_field = ft.TextField(
            label="検索",
            hint_text="タイトルでフィルタ...",
            on_change=lambda e: self._controller.set_keyword(e.control.value or ""),  # type: ignore[arg-type]
            expand=True,
        )

        status_options = [ft.dropdown.Option(key="", text="すべて")] + [
            ft.dropdown.Option(key=value, text=TASK_STATUS_LABELS[value]) for value in TASK_STATUS_LABELS
        ]
        self._status_dropdown = ft.Dropdown(
            label="状態",
            options=status_options,
            value="",
            on_change=lambda e: self._on_status_dd_change(e),  # type: ignore[arg-type]
            width=160,
        )

        self._sort_dropdown = ft.Dropdown(
            label="並び替え",
            options=[
                ft.dropdown.Option("updated_at"),
                ft.dropdown.Option("created_at"),
                ft.dropdown.Option("priority"),
            ],
            value=self._controller.state.sort_key,
            on_change=lambda e: self._controller.set_sort(
                key=e.control.value, descending=self._controller.state.sort_desc
            ),  # type: ignore[arg-type]
            width=160,
        )

        self._desc_switch = ft.Switch(
            label="降順",
            value=self._controller.state.sort_desc,
            on_change=lambda e: self._controller.set_sort(
                key=self._controller.state.sort_key, descending=e.control.value
            ),  # type: ignore[arg-type]
        )

        # タブ (React テンプレート準拠) - 各ステータス件数をバッジ表示
        counts = self._safe_get_counts()
        # タブ: 先頭に「すべて」を追加し単一ソースに統一（status=None を表す）
        total = 0
        try:
            total = self._controller.get_total_count()
        except Exception:
            total = len(self._current_vm)
        self._tab_keys: list[str | None] = [None, *STATUS_ORDER]  # 0番目は None (=すべて)
        tab_texts: list[str] = [f"すべて ({total})"] + [
            f"{TASK_STATUS_LABELS.get(status, status)} ({counts.get(status, 0)})" for status in STATUS_ORDER
        ]
        self._tabs = ft.Tabs(
            selected_index=self._current_tab_index(),
            tabs=[ft.Tab(text=t) for t in tab_texts],
            on_change=self._on_tabs_change,
            expand=True,
        )
        tabs_list = ft.Row([self._tabs], spacing=0)

        # 左: 一覧 / 右: 詳細 (components)
        self._render_items(self._current_vm)

        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self._list_comp.control,
                    col={"xs": 12, "lg": 5},
                    padding=ft.padding.only(right=12),
                ),
                ft.Container(
                    content=self._detail_comp.control,
                    col={"xs": 12, "lg": 7},
                ),
            ],
            expand=True,
        )
        # TODO: 右ペインをタブ化 (概要/履歴/コメント) するなどの拡張を検討。アクティビティ連携も想定。

        controls = ft.Column(
            controls=[
                header,
                ft.Row(
                    controls=[
                        self._search_field,
                        self._status_dropdown,
                        self._sort_dropdown,
                        self._desc_switch,
                    ],
                    spacing=12,
                ),
                ft.Divider(),
                tabs_list,
                ft.Divider(),
                grid,
            ],
            spacing=16,
            expand=True,
        )

        return ft.Container(content=controls, padding=24, expand=True)

    # --- Controller のコールバック ---
    def _on_view_model_change(self, vm_list: list[TaskCardVM]) -> None:
        """ControllerからのVM変化通知を受け取りリストを再描画する。"""
        self._current_vm = vm_list
        self._render_items(vm_list)
        self._refresh_tabs_badges()

    def _render_items(self, items: list[TaskCardVM]) -> None:
        """ListViewへアイテムを反映。"""
        # TaskCardDataへ変換し子コンポーネントへ渡す（MemoCardパターン踏襲）
        cards: list[TaskCardData] = []
        selected = self._controller.state.selected_id
        for vm in items:

            def _on_click_vm(vm: TaskCardVM = vm) -> None:
                self._show_detail(vm)

            cards.append(
                TaskCardData(
                    task_id=str(vm.id),
                    title=vm.title,
                    subtitle=vm.subtitle,
                    status=vm.status,
                    status_label=TASK_STATUS_LABELS.get(vm.status, vm.status),
                    is_selected=(selected == vm.id) if selected else False,
                    on_click=_on_click_vm,
                )
            )
        self._list_comp.set_cards(cards)

    def _show_detail(self, vm: TaskCardVM) -> None:
        """選択タスク詳細を右ペインに表示する。"""
        # Presenter で詳細用VMに昇格させてから渡す
        dvm = to_detail_from_card(vm)
        self._detail_comp.set_item(dvm)
        logger.debug("detail set: id={} title='{}' status={}", vm.id, vm.title, vm.status)
        self._controller.set_selected(vm.id)

    def _count_by_status(self, status: str) -> int:
        return sum(1 for vm in self._current_vm if vm.status == status)

    def _safe_get_counts(self) -> dict[str, int]:
        try:
            return self._controller.get_counts()
        except Exception:
            return {s: self._count_by_status(s) for s in STATUS_ORDER}

    def _current_tab_index(self) -> int:
        try:
            status = self._controller.state.status
            if not status:
                return 0
            return 1 + STATUS_ORDER.index(status)
        except Exception:
            return 0

    def _on_tabs_change(self, e: ft.ControlEvent) -> None:
        idx = getattr(e.control, "selected_index", 0) or 0
        # 0番目は「すべて」= None、それ以外は STATUS_ORDER[idx-1]
        new_status: str | None = None if idx == 0 else STATUS_ORDER[idx - 1]
        self._controller.set_status(new_status)
        if self._status_dropdown is not None:
            self._status_dropdown.value = new_status or ""
            with contextlib.suppress(AssertionError):
                self._status_dropdown.update()

    def _refresh_tabs_badges(self) -> None:
        if not self._tabs:
            return
        counts = self._safe_get_counts()
        # 先頭（すべて）
        total = 0
        try:
            total = self._controller.get_total_count()
        except Exception:
            total = len(self._current_vm)
        if len(self._tabs.tabs) > 0:
            self._tabs.tabs[0].text = f"すべて ({total})"
        # 残りステータス
        for i, status in enumerate(STATUS_ORDER, start=1):
            if i < len(self._tabs.tabs):
                self._tabs.tabs[i].text = f"{TASK_STATUS_LABELS.get(status, status)} ({counts.get(status, 0)})"
        with contextlib.suppress(AssertionError):
            self._tabs.update()
        # TODO: 大量件数時は counts を Controller 側の集計キャッシュから取得し、頻度を制御 (レート制限)。

    def _on_status_dd_change(self, e: ft.ControlEvent) -> None:
        # Dropdown→state 更新 + Tabs の選択も同期
        new_status = e.control.value or None
        self._controller.set_status(new_status)
        if self._tabs is not None:
            idx = 0 if not new_status else 1 + STATUS_ORDER.index(str(new_status))
            self._tabs.selected_index = idx
            with contextlib.suppress(AssertionError):
                self._tabs.update()

    # --- 外部 API (将来統合用) ---
    def get_state_snapshot(self) -> TasksState:
        """現在の状態スナップショットを返す。テスト/デバッグ用。"""
        return self._controller.state

    # --- Component callbacks ---
    def _on_item_clicked(self, vm: TaskCardVM) -> None:
        self._show_detail(vm)

    def _on_item_clicked_id(self, task_id: str) -> None:
        # 現在のVM一覧から該当を検索
        for vm in self._current_vm:
            if vm.id == task_id:
                self._show_detail(vm)
                return

    def _on_status_change(self, task_id: str, new_status: str) -> None:
        # Controller に委譲（InMemoryでは簡易更新）。実装未対応ならログのみ。
        try:
            self._controller.change_task_status(task_id, new_status)
        except AttributeError:
            logger.warning("change_task_status not supported by controller")


def _default_seed_data() -> list[dict[str, object]]:
    """旧ビューのモックを平坦化した初期シードを返す。

    Returns:
        タスク辞書リスト
    """
    return [
        {
            "id": "1",
            "title": "新機能の要件定義",
            "description": "ユーザー要望整理と仕様策定",
            "priority": 3,
            "status": "todo",
            "updated_at": "2024-10-20",
            "created_at": "2024-10-20",
        },
        {
            "id": "2",
            "title": "デザインモックアップ作成",
            "description": "UI/UX初期案",
            "priority": 2,
            "status": "todo",
            "updated_at": "2024-10-22",
            "created_at": "2024-10-22",
        },
        {
            "id": "3",
            "title": "フロントエンド実装",
            "description": "Reactコンポーネント実装",
            "priority": 3,
            "status": "progress",
            "updated_at": "2024-10-18",
            "created_at": "2024-10-18",
        },
        {
            "id": "4",
            "title": "API仕様書作成",
            "description": "バックエンドAPI詳細",
            "priority": 2,
            "status": "progress",
            "updated_at": "2024-10-21",
            "created_at": "2024-10-21",
        },
        {
            "id": "5",
            "title": "環境構築",
            "description": "開発環境セットアップ",
            "priority": 1,
            "status": "completed",
            "updated_at": "2024-10-15",
            "created_at": "2024-10-15",
        },
        {
            "id": "6",
            "title": "本日のレビュー",
            "description": "スタンドアップ用メモ",
            "priority": 2,
            "status": "todays",
            "updated_at": "2024-10-24",
            "created_at": "2024-10-24",
        },
        {
            "id": "7",
            "title": "依頼待ちの回答",
            "description": "法務確認待ち",
            "priority": 2,
            "status": "waiting",
            "updated_at": "2024-10-23",
            "created_at": "2024-10-22",
        },
        {
            "id": "8",
            "title": "不要チケットのクローズ",
            "description": "範囲外のため",
            "priority": 1,
            "status": "canceled",
            "updated_at": "2024-10-19",
            "created_at": "2024-10-17",
        },
        {
            "id": "9",
            "title": "期限切れのバックログ整理",
            "description": "期限超過アイテムの棚卸し",
            "priority": 3,
            "status": "overdue",
            "updated_at": "2024-10-10",
            "created_at": "2024-10-01",
        },
    ]
