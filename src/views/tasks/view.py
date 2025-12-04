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

import asyncio
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.application.task_application_service import TaskApplicationService
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import HeaderButtonData

from .components import TaskEmptyState, TaskNoSelection, TaskStatusTabs
from .components.detail_panel import DetailPanelProps, TaskDetailPanel
from .components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS
from .components.task_card import TaskCardData
from .components.task_dialog import show_create_task_dialog
from .components.task_list import TaskList, TaskListProps
from .controller import TasksController
from .presenter import to_detail_from_card

if TYPE_CHECKING:
    from .presenter import TaskCardVM
    from .state import TasksState


class TasksView(BaseView):
    """タスク管理のメインビュー (新MVP構成)。

    検索 / ステータスフィルタ / 並び替え / 降順切替 + リスト表示の最小UIを提供。
    """

    def __init__(self, props: BaseViewProps) -> None:
        """コンストラクタ。

        Args:
            props: 共通ビュープロパティ (page, apps コンテナ)
        """
        super().__init__(props)

        # データ取得: ApplicationService を優先して利用する
        # - 例外時のユーザー通知は BaseView の snackbar を利用
        service = self.apps.get_service(TaskApplicationService)

        # コントローラー初期化
        self._controller = TasksController(
            service=service,
            on_change=self._on_view_model_change,
            on_error=lambda msg: self.show_error_snackbar(self.page, msg),
        )

        self._current_vm: list[TaskCardVM] = []
        # Components
        self._status_tabs: TaskStatusTabs | None = None
        self._list_comp = TaskList(TaskListProps(on_item_click=self._on_item_clicked_id))
        self._detail_panel = TaskDetailPanel(DetailPanelProps(on_status_change=self._on_status_change))
        self._no_selection = TaskNoSelection()
        self._detail_control: ft.Control = self._no_selection
        self._empty_state = TaskEmptyState(on_create=self._open_create_dialog)
        logger.info("TasksView initialized with ApplicationService")

        # 初期描画データ（エラーハンドリング付き）
        try:
            self._controller.refresh()
            logger.debug(f"TasksView: 初期データ読み込み完了 ({len(self._current_vm)}件)")
        except Exception as e:
            logger.error(f"TasksView: 初期データ読み込みエラー: {e}")
            # エラーが発生しても空状態で画面を表示する
            self._current_vm = []

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

        header = self.create_header(
            title="タスク",
            subtitle=f"GTDベースのタスク管理 ({total_count}件)",
            search_placeholder="タイトルでフィルタ...",
            on_search=self._handle_search,
            action_buttons=[
                HeaderButtonData(
                    label="新規タスク作成",
                    icon=ft.Icons.ADD,
                    on_click=lambda: self._open_create_dialog(),
                    is_primary=True,
                )
            ],
        )

        # タブコンポーネント
        counts = self._safe_get_counts()

        self._status_tabs = TaskStatusTabs(
            on_tab_change=self._on_tab_status_change,
            active_status=self._controller.state.status,
            tab_counts=counts,
        )

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
                    content=self._detail_control,
                    col={"xs": 12, "lg": 7},
                ),
            ],
            expand=True,
        )
        # TODO: 右ペインをタブ化 (概要/履歴/コメント) するなどの拡張を検討。アクティビティ連携も想定。

        controls = ft.Column(
            controls=[
                header,
                self._status_tabs,
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
        # デバッグ用ログ (フィルタ結果の可視化)
        try:
            counts = self._safe_get_counts()
            logger.debug(
                "filter applied: total={} keyword='{}' status='{}' sort='{}' desc={} counts={}",
                len(vm_list),
                self._controller.state.keyword,
                self._controller.state.status,
                self._controller.state.sort_key,
                self._controller.state.sort_desc,
                counts,
            )
        except Exception as e:  # 安全性優先で失敗を握り潰す
            logger.debug(f"filter debug logging failed: {e}")
        # フィルタ/検索/並び替えの反映を確実に UI に適用
        self.safe_update()

    # --- Search debounce ---
    _SEARCH_DEBOUNCE_MS: int = 300
    _search_debounce_task: asyncio.Task | None = None

    def _handle_search(self, query: str) -> None:
        """Header検索フィールドからの検索処理。"""
        keyword = query.strip()
        self._debounce_keyword_apply(keyword)

    def _debounce_keyword_apply(self, keyword: str) -> None:
        # 既存タスクがあればキャンセル
        if self._search_debounce_task and not self._search_debounce_task.done():
            self._search_debounce_task.cancel()

        async def _apply() -> None:
            try:
                await asyncio.sleep(self._SEARCH_DEBOUNCE_MS / 1000)
                self._controller.set_keyword(keyword)
            except asyncio.CancelledError:
                return
            except Exception as e:  # ログのみ
                logger.debug(f"debounce apply failed: {e}")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 非同期ループ未起動時は即時適用 (テスト環境考慮)
            self._controller.set_keyword(keyword)
            return
        self._search_debounce_task = loop.create_task(_apply())

    def will_unmount(self) -> None:  # type: ignore[override]
        # 検索デバウンスタスクをクリーンアップ
        if self._search_debounce_task and not self._search_debounce_task.done():
            self._search_debounce_task.cancel()
        super().will_unmount()

    def _render_items(self, items: list[TaskCardVM]) -> None:
        """ListViewへアイテムを反映。"""
        # 空状態の場合はTaskListに空カードリストを渡す
        if not items:
            self._list_comp.set_cards([])
            logger.debug("TasksView: タスクリストが空です")
            return

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

        # 詳細パネルを表示
        self._detail_panel.set_item(dvm)
        self._detail_control = self._detail_panel.control
        logger.debug("detail set: id={} title='{}' status={}", vm.id, vm.title, vm.status)
        self._controller.set_selected(vm.id)

    def _count_by_status(self, status: str) -> int:
        return sum(1 for vm in self._current_vm if vm.status == status)

    def _safe_get_counts(self) -> dict[str, int]:
        try:
            return self._controller.get_counts()
        except Exception:
            return {s: self._count_by_status(s) for s in STATUS_ORDER}

    def _refresh_tabs_badges(self) -> None:
        if not self._status_tabs:
            return
        counts = self._safe_get_counts()
        self._status_tabs.update_counts(counts)
        # TODO: 大量件数時は counts を Controller 側の集計キャッシュから取得し、頻度を制御 (レート制限)。

    def _on_tab_status_change(self, status: str | None) -> None:
        """タブステータス変更時のコールバック。

        Args:
            status: 新しいステータス（Noneは「すべて」）
        """
        self._controller.set_status(status)
        self.safe_update()

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
        """タスクステータス変更時のコールバック。

        Args:
            task_id: タスクID
            new_status: 新しいステータス
        """
        try:
            self._controller.change_task_status(task_id, new_status)
            # ステータス変更後に画面を更新
            self.safe_update()
        except AttributeError:
            logger.warning("change_task_status not supported by controller")

    def _open_create_dialog(self) -> None:
        """タスク作成ダイアログを開く。"""
        show_create_task_dialog(
            page=self.page,
            on_save=self._handle_create_task,
        )

    def _handle_create_task(self, task_data: dict[str, str]) -> None:
        """タスク作成処理を実行する。

        Args:
            task_data: タスクデータ(title, description, status など)
        """
        title = task_data.get("title", "").strip()
        description = task_data.get("description", "").strip() or None
        status = task_data.get("status", "").strip()

        if not title:
            self.show_error_snackbar(self.page, "タイトルを入力してください。")
            return

        # Controllerにタスク作成を委譲（ローディング表示付き）
        def _create() -> None:
            self._controller.create_task(
                title=title,
                description=description,
                status=status,
            )

        try:
            self.with_loading(_create)
            # 成功メッセージを表示
            self.show_success_snackbar(f"タスク「{title}」を作成しました。")
            logger.info(f"タスク作成成功: {title}")
            # 明示的に画面を更新
            self.safe_update()
        except Exception as e:
            logger.exception(f"タスク作成中にエラー: {e}")
            self.show_error_snackbar(self.page, "タスクの作成に失敗しました。詳細はログを参照してください。")
