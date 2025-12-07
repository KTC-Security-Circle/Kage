"""Memo View Layer.

【責務】
    View層はMVPパターンにおける「View」の役割を担う。
    UIレイアウトの構築、イベントハンドラーの配線、Controllerへの処理委譲を行う。

    - UIコンポーネントの配置とレイアウト構築
    - ユーザーイベント（クリック、検索等）のハンドリング
    - Controllerへのユースケース実行依頼
    - Presenterを使用したUI要素の生成・更新
    - BaseViewを継承したエラーハンドリングとローディング表示

【責務外（他層の担当）】
    - データのフォーマット変換 → Presenter
    - 状態の保持と派生計算 → State
    - ビジネスロジックの実行 → Controller
    - ApplicationServiceの呼び出し → Controller
    - UI要素の生成ロジック → Presenter

【アーキテクチャ上の位置づけ】
    User → View → Controller → ApplicationService
                ↓
            Presenter (UI構築支援)
                ↓
            State (状態参照)

【主な機能】
    - 4つのステータスタブ（Inbox/Active/Idea/Archive）の表示
    - メモ一覧と詳細パネルの2カラムレイアウト
    - 検索・フィルタ機能
    - メモ選択と詳細表示
    - CRUD操作の起点（統合フェーズで実装予定）
"""

from __future__ import annotations

import asyncio
import threading
from datetime import datetime
from uuid import UUID

import flet as ft
from loguru import logger

from logic.application.memo_ai_job_queue import GeneratedTaskPayload, MemoAiJobSnapshot, MemoAiJobStatus
from logic.application.memo_application_service import MemoApplicationService
from models import AiSuggestionStatus, MemoRead, MemoStatus
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import HeaderButtonData
from views.theme import get_error_color, get_outline_color

from . import presenter
from .components import MemoCardList, MemoFilters, MemoStatusTabs
from .controller import MemoApplicationPort, MemosController
from .state import AiSuggestedTask, MemosViewState


class MemosView(BaseView):
    """メモ管理のメインビュー。

    Reactテンプレートの MemosScreen.tsx を参考に実装。
    4つのステータスタブでメモを分類し、検索・フィルタ機能を提供。

    機能:
    - Inbox/Active/Idea/Archive の4つのタブでメモ分類
    - 検索とフィルタリング
    - メモ詳細表示
    - メモ作成・編集・削除
    - AI提案機能（将来実装）
    """

    def __init__(self, props: BaseViewProps, *, memo_app: MemoApplicationPort | None = None) -> None:
        """メモビューを初期化。

        Args:
            props: View共通プロパティ
            memo_app: テストやDI用に注入するメモアプリケーションサービス
        """
        super().__init__(props)

        self.memos_state = MemosViewState()
        if memo_app is None:
            memo_app = self.apps.get_service(MemoApplicationService)
        self.controller = MemosController(memo_app=memo_app, state=self.memos_state)

        # UIコンポーネント
        self._header: ft.Control | None = None
        self._status_tabs: MemoStatusTabs | None = None
        self._memo_list: MemoCardList | None = None
        self._memo_filters: MemoFilters | None = None
        self._detail_panel: ft.Container | None = None
        self._pending_async_tasks: list[asyncio.Task[None]] = []

        self.did_mount()
        self.with_loading(self._load_initial_memos, user_error_message="メモの読み込みに失敗しました")

    def did_mount(self) -> None:
        """マウント時の初期化処理。"""
        super().did_mount()
        logger.info("MemosView mounted")

    def build_content(self) -> ft.Control:  # BaseView.build が呼ぶ
        """メモビューのUIを構築。"""
        # アクションバー
        self._header = self.create_header(
            title="メモ",
            subtitle="思考とアイデアを記録し、AIでタスクに変換",
            search_placeholder="メモを検索...",
            on_search=self._handle_search,
            action_buttons=[
                HeaderButtonData(
                    label="新しいメモ",
                    icon=ft.Icons.ADD,
                    on_click=self._handle_create_memo,
                    is_primary=True,
                ),
            ],
        )

        # ステータスタブ
        self._status_tabs = MemoStatusTabs(
            on_tab_change=self._handle_tab_change,
            active_status=self.memos_state.current_tab or MemoStatus.INBOX,
            tab_counts=self._get_tab_counts(),
        )

        # フィルタ
        self._memo_filters = MemoFilters(
            on_filter_change=self._handle_filter_change,
        )

        # メインコンテンツエリア
        main_content = self._build_main_content()

        return ft.Column(
            controls=[
                self._header,
                self._status_tabs,
                self._memo_filters,
                main_content,
            ],
            spacing=0,
            expand=True,
        )

    def _build_main_content(self) -> ft.Control:
        """メインコンテンツエリアを構築。

        Returns:
            メインコンテンツコントロール
        """
        # メモリスト
        current_memos = self.controller.current_memos()
        selected_memo_id = presenter.memo_id_to_str(self.memos_state.selected_memo_id)
        self._memo_list = MemoCardList(
            memos=current_memos,
            on_memo_select=self._handle_memo_select,
            empty_message=presenter.get_empty_message_for_status(self.memos_state.current_tab),
            selected_memo_id=selected_memo_id,
        )

        # 詳細パネル
        self._detail_panel = self._build_detail_panel()

        # レスポンシブレイアウト
        return ft.Container(
            content=ft.Row(
                controls=[
                    # 左側：メモリスト
                    ft.Container(
                        content=self._memo_list,
                        width=400,
                        padding=ft.padding.all(8),
                        border=ft.border.only(right=ft.BorderSide(width=1, color=get_outline_color())),
                    ),
                    # 右側：詳細パネル
                    ft.Container(
                        content=self._detail_panel,
                        expand=True,
                        padding=ft.padding.all(16),
                    ),
                ],
            ),
            expand=True,
        )

    def _build_detail_panel(self) -> ft.Container:
        """詳細パネルを構築。

        Returns:
            詳細パネルコントロール
        """
        selected_memo = self.controller.current_selection()
        if selected_memo is None:
            return ft.Container(content=presenter.build_empty_detail_panel())

        ai_section = self._build_ai_task_flow_section(selected_memo)
        extra_sections = (ai_section,) if ai_section is not None else None

        return presenter.build_detail_panel(
            selected_memo,
            on_edit=self._handle_edit_memo,
            on_delete=self._handle_delete_memo,
            extra_sections=extra_sections,
        )

    def _build_ai_task_flow_section(self, memo: MemoRead) -> ft.Control | None:
        """AI提案→タスク承認フローのUIを構築する。"""
        ai_status = self.memos_state.effective_ai_status(memo)
        ai_state = self.memos_state.ai_flow_state_for(memo.id)
        return presenter.build_ai_task_flow_panel(
            memo,
            ai_status=ai_status,
            tasks=tuple(ai_state.generated_tasks),
            selected_task_ids=set(ai_state.selected_task_ids),
            editing_task_id=ai_state.editing_task_id,
            error_message=ai_state.error_message,
            on_request_ai=lambda _e, target=memo: self._handle_request_ai_generation(target),
            on_retry_ai=lambda _e, memo_id=memo.id: self._handle_retry_ai_generation(memo_id),
            on_mark_as_idea=lambda _e, memo_id=memo.id: self._handle_mark_memo_as_idea(memo_id),
            on_toggle_task=lambda task_id, memo_id=memo.id: self._handle_toggle_ai_task(memo_id, task_id),
            on_start_edit=lambda task_id, memo_id=memo.id: self._handle_start_edit_ai_task(memo_id, task_id),
            on_cancel_edit=lambda e, memo_id=memo.id: self._handle_cancel_edit_ai_task(memo_id, e),
            on_edit_field_change=lambda task_id, field, value, memo_id=memo.id: self._handle_update_ai_task_field(
                memo_id, task_id, field, value
            ),
            on_save_edit=lambda task_id, memo_id=memo.id: self._handle_save_ai_task_edit(memo_id, task_id),
            on_delete_task=lambda task_id, memo_id=memo.id: self._handle_delete_ai_task(memo_id, task_id),
            on_add_task=lambda _=None, memo_id=memo.id: self._handle_add_ai_task(memo_id),
            on_approve_tasks=lambda _=None, target=memo: self._handle_approve_ai_tasks(target),
        )

    def _get_tab_counts(self) -> dict[MemoStatus, int]:
        """各タブのメモ数を取得。

        Returns:
            タブ別メモ数辞書
        """
        return self.controller.status_counts()

    def _load_initial_memos(self) -> None:
        """DB から初期メモ一覧を読み込む (Inbox を優先)。"""
        try:
            self.controller.load_initial_memos()
            self._refresh()
            memo_count = len(self.controller.current_memos())
            logger.info(f"Loaded {memo_count} memos from DB")
        except Exception as e:
            self.notify_error("メモの読み込みに失敗しました", details=f"{type(e).__name__}: {e}")

    def _update_memo_list(self) -> None:
        """メモリストを更新。"""
        if self._memo_list:
            current_memos = self.controller.current_memos()
            selected_memo_id = presenter.memo_id_to_str(self.memos_state.selected_memo_id)
            try:
                self._memo_list.update_memos(
                    current_memos,
                    selected_memo_id=selected_memo_id,
                )
            except AssertionError as e:
                if "Control must be added to the page first" in str(e):
                    logger.warning(f"Skipping memo list update: {e}")
                else:
                    raise

        if self._status_tabs:
            try:
                self._status_tabs.update_counts(self._get_tab_counts())
                self._status_tabs.set_active(self.memos_state.current_tab or MemoStatus.INBOX)
            except AssertionError as e:
                if "Control must be added to the page first" in str(e):
                    # Component not yet added to page, skip update
                    logger.warning(f"Skipping status tabs update: {e}")
                else:
                    raise

    # イベントハンドラー

    def _handle_create_memo(self) -> None:
        """新規メモ作成ハンドラー。"""
        logger.info("Create memo requested")
        # TODO: ダイアログ版のクイック作成（テンプレートの CreateMemoDialog 相当）を後続で併存させる。
        #       現状はページ遷移でフルスクリーンの CreateMemoView を表示。
        # メモ作成ページへ遷移
        try:
            self.page.go("/memos/create")
        except Exception as e:
            self.notify_error("メモ作成ページへの遷移に失敗しました", details=f"{type(e).__name__}: {e}")

    def _handle_search(self, query: str) -> None:
        """検索ハンドラー。

        Args:
            query: 検索クエリ
        """
        try:
            self.controller.update_search(query)
            self._refresh()
        except Exception as e:
            self.notify_error("検索に失敗しました", details=f"{type(e).__name__}: {e}")
        logger.debug(f"Search query: '{query}' (tab={self.memos_state.current_tab})")

    def _handle_tab_change(self, status: MemoStatus | None) -> None:
        """タブ変更ハンドラー。

        Args:
            status: 選択されたタブのステータス（Noneの場合は無視）
        """
        if status is None:
            return
        try:
            self.controller.update_tab(status)
            if self.memos_state.search_query:
                self.controller.update_search(self.memos_state.search_query)
            self._refresh()
        except Exception as e:
            self.notify_error("タブ切替に失敗しました", details=f"{type(e).__name__}: {e}")
        logger.debug(f"Tab changed to: {status}")

    def _handle_filter_change(self, filter_data: dict[str, object]) -> None:
        """フィルタ変更ハンドラー。

        Args:
            filter_data: フィルタデータ
        """
        logger.debug(f"Filter changed: {filter_data}")
        self._update_memo_list()

    def _handle_memo_select(self, memo: MemoRead) -> None:
        """メモ選択ハンドラー。

        Args:
            memo: 選択されたメモ
        """
        self.controller.select_memo(memo)
        selected_memo_id = presenter.memo_id_to_str(self.memos_state.selected_memo_id)
        # リストの選択ハイライトを更新（詳細パネルと同時に切り替える）
        if self._memo_list:
            try:
                self._memo_list.set_selected_memo(selected_memo_id)
            except AssertionError as e:
                if "Control must be added to the page first" in str(e):
                    # まだページに追加されていない場合はスキップ
                    pass
                else:
                    raise
        self._update_detail_panel()
        logger.debug(f"Memo selected: {memo.id}")

    def _handle_ai_suggestion(self, _: ft.ControlEvent) -> None:
        """AI提案ハンドラー。"""
        logger.info("AI suggestion requested")
        # TODO: AI提案機能を実装
        self.show_info_snackbar("AI提案機能は統合フェーズで実装予定です")

    def _handle_request_ai_generation(self, memo: MemoRead) -> None:
        """MemoToTaskAgentによるタスク生成をキューに登録する。"""

        def _enqueue() -> MemoAiJobSnapshot:
            logger.debug(f"enqueue_ai_generation called: memo_id={memo.id}")
            return self.controller.enqueue_ai_generation(memo.id)

        def _after(snapshot: MemoAiJobSnapshot) -> None:
            self.memos_state.track_ai_job(memo.id, snapshot.job_id, snapshot.status.value)
            self.memos_state.set_ai_status_override(memo.id, AiSuggestionStatus.PENDING)
            ai_state = self.memos_state.ai_flow_state_for(memo.id)
            ai_state.generated_tasks.clear()
            ai_state.selected_task_ids.clear()
            ai_state.editing_task_id = None
            self._refresh()
            logger.debug(f"Polling scheduled for job_id={snapshot.job_id} memo_id={memo.id}")
            self._start_ai_job_polling(snapshot.job_id, memo.id)

        def _task() -> None:
            snapshot = _enqueue()
            _after(snapshot)

        self.with_loading(_task, user_error_message="AIタスク生成の登録に失敗しました")

    def _handle_retry_ai_generation(self, memo_id: UUID) -> None:
        """AI生成処理を再実行する。"""
        memo = self._get_memo_by_id(memo_id)
        if memo is None:
            return
        self._handle_request_ai_generation(memo)

    def _handle_mark_memo_as_idea(self, memo_id: UUID) -> None:
        """メモをアイデア扱いにしてAIフローをリセットする。"""
        memo = self._get_memo_by_id(memo_id)
        if memo is None:
            return

        def _mark() -> None:
            self.controller.update_memo(memo_id, status=MemoStatus.IDEA, ai_status=AiSuggestionStatus.NOT_REQUESTED)

        self.with_loading(_mark, user_error_message="アイデアへの変更に失敗しました")
        self.memos_state.clear_ai_flow_state(memo_id)
        self.show_info_snackbar("メモをアイデアとして保存しました")
        self._refresh()

    def _handle_toggle_ai_task(self, memo_id: UUID, task_id: str) -> None:
        """AI提案タスクの選択状態をトグルする。"""
        self.memos_state.toggle_task_selection(memo_id, task_id)
        self._refresh()

    def _handle_start_edit_ai_task(self, memo_id: UUID, task_id: str) -> None:
        """指定タスクを編集モードに切り替える。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.editing_task_id = task_id
        self._refresh()

    def _handle_cancel_edit_ai_task(self, memo_id: UUID, _: ft.ControlEvent | None = None) -> None:
        """AI提案タスクの編集をキャンセルする。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.editing_task_id = None
        self._refresh()

    def _handle_update_ai_task_field(self, memo_id: UUID, task_id: str, field: str, value: str) -> None:
        """編集中タスクのフィールド値を更新する。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        for task in ai_state.generated_tasks:
            if task.task_id == task_id:
                if field == "title":
                    task.title = value
                elif field == "description":
                    task.description = value
                break

    def _handle_save_ai_task_edit(self, memo_id: UUID, task_id: str) -> None:
        """AI提案タスクの編集結果を確定する。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        target = next((task for task in ai_state.generated_tasks if task.task_id == task_id), None)
        if target is None:
            self.notify_error("タスクが見つかりません")
            return
        try:
            self.controller.update_ai_task(
                memo_id,
                UUID(task_id),
                title=target.title,
                description=target.description,
            )
        except Exception as exc:
            self.notify_error("Draftタスクの更新に失敗しました", details=f"{type(exc).__name__}: {exc}")
            return
        if ai_state.editing_task_id == task_id:
            ai_state.editing_task_id = None
        self.show_success_snackbar("タスク内容を更新しました")
        self._refresh()

    def _handle_delete_ai_task(self, memo_id: UUID, task_id: str) -> None:
        """AI提案タスクを削除する。"""
        try:
            self.controller.delete_ai_task(memo_id, UUID(task_id))
        except Exception as exc:
            self.notify_error("Draftタスクの削除に失敗しました", details=f"{type(exc).__name__}: {exc}")
            return
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.selected_task_ids.discard(task_id)
        if ai_state.editing_task_id == task_id:
            ai_state.editing_task_id = None
        self._refresh()

    def _handle_add_ai_task(self, memo_id: UUID) -> None:
        """AI提案リストに空のタスクを追加する。"""
        try:
            created = self.controller.create_ai_task(
                memo_id,
                title="新しいタスク",
                description="",
                route="next_action",
            )
        except Exception as exc:
            self.notify_error("Draftタスクの追加に失敗しました", details=f"{type(exc).__name__}: {exc}")
            return

        task_id = str(created.id)
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.editing_task_id = task_id
        ai_state.selected_task_ids.add(task_id)
        self._refresh()

    def _handle_approve_ai_tasks(self, memo: MemoRead) -> None:
        """選択されたAI提案タスクを承認済みとして扱う。"""
        ai_state = self.memos_state.ai_flow_state_for(memo.id)
        if not ai_state.selected_task_ids:
            self.show_snack_bar("承認するタスクを選択してください", bgcolor=get_error_color())
            return
        try:
            task_ids = [UUID(task_id) for task_id in ai_state.selected_task_ids]
            self.controller.approve_ai_tasks(memo.id, task_ids)
        except Exception as exc:
            self.notify_error("Draftタスクの承認に失敗しました", details=f"{type(exc).__name__}: {exc}")
            return
        ai_state.status_override = AiSuggestionStatus.REVIEWED
        ai_state.is_generating = False

        def _archive() -> None:
            self.controller.mark_memo_archived(memo.id)

        self.with_loading(_archive, user_error_message="メモのアーカイブに失敗しました")
        self.show_success_snackbar("タスクを承認し、メモをアーカイブしました")
        self._refresh()

    def _start_ai_job_polling(self, job_id: UUID, memo_id: UUID) -> None:
        async def _poll() -> None:
            while True:
                snapshot = await asyncio.to_thread(self.controller.get_ai_job_snapshot, job_id)
                self._process_ai_job_snapshot(memo_id, snapshot)
                if snapshot.status in {MemoAiJobStatus.SUCCEEDED, MemoAiJobStatus.FAILED}:
                    break
                await asyncio.sleep(1.5)

        if self.page and hasattr(self.page, "run_task"):
            try:
                self.page.run_task(_poll)
            except Exception:
                logger.exception("Failed to schedule AI job polling via page.run_task")
            else:
                return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:

            def _runner() -> None:
                logger.debug(f"Starting polling thread for job_id={job_id} memo_id={memo_id}")
                asyncio.run(_poll())

            thread = threading.Thread(target=_runner, name="MemoAiJobPoller", daemon=True)
            thread.start()
        else:
            task = loop.create_task(_poll())
            self._pending_async_tasks.append(task)

    def _process_ai_job_snapshot(self, memo_id: UUID, snapshot: MemoAiJobSnapshot) -> None:
        self.memos_state.update_job_status(memo_id, status=snapshot.status.value, error=snapshot.error_message)
        if snapshot.status == MemoAiJobStatus.SUCCEEDED:
            tasks = [self._convert_payload_to_ai_task(payload) for payload in snapshot.tasks]
            self.memos_state.set_generated_tasks(memo_id, tasks)
            self.memos_state.set_ai_status_override(memo_id, AiSuggestionStatus.AVAILABLE)
            self.controller.refresh_memo(memo_id)
            logger.debug(f"AI job succeeded: job_id={snapshot.job_id} memo_id={memo_id} tasks={len(snapshot.tasks)}")
            self.show_success_snackbar("AI提案タスクを取得しました")
        elif snapshot.status == MemoAiJobStatus.FAILED:
            self.memos_state.set_ai_status_override(memo_id, AiSuggestionStatus.FAILED)
            self.controller.refresh_memo(memo_id)
            self.notify_error("AIタスク生成に失敗しました", details=snapshot.error_message)
            logger.debug(f"AI job failed: job_id={snapshot.job_id} memo_id={memo_id} error={snapshot.error_message}")
        self._refresh()

    def _convert_payload_to_ai_task(self, payload: GeneratedTaskPayload) -> AiSuggestedTask:
        due: datetime | None = None
        if payload.due_date:
            try:
                raw = payload.due_date
                if raw.endswith("Z"):
                    raw = raw.replace("Z", "+00:00")
                due = datetime.fromisoformat(raw)
            except ValueError:
                due = None
        return AiSuggestedTask(
            task_id=str(payload.task_id),
            title=payload.title,
            description=payload.description or "",
            tags=payload.tags,
            due_date=due,
            route=payload.route,
            status=payload.status,
        )

    def _get_memo_by_id(self, memo_id: UUID) -> MemoRead | None:
        """内部インデックスからメモを検索する。"""
        return self.memos_state.memo_by_id(memo_id)

    def _handle_edit_memo(self, _: ft.ControlEvent) -> None:
        """メモ編集ハンドラー。編集ダイアログを表示し、保存時に Controller 経由で更新する。

        Args:
            _: ft.ControlEvent (未使用)
        """
        selected_memo = self.controller.current_selection()
        if selected_memo is None:
            return

        # ダイアログの入力コントロールを構築
        title_field = ft.TextField(value=selected_memo.title or "", label="タイトル", expand=True)
        content_field = ft.TextField(
            value=selected_memo.content or "", label="内容", multiline=True, min_lines=6, expand=True
        )

        def _on_save(_: ft.ControlEvent | None = None) -> None:
            title = (title_field.value or "").strip() or "無題のメモ"
            content = (content_field.value or "").strip()
            if not content:
                self.show_snack_bar("内容を入力してください", bgcolor=get_error_color())
                return

            def _save() -> None:
                try:
                    updated = self.controller.update_memo(
                        selected_memo.id,
                        title=title,
                        content=content,
                        status=selected_memo.status,
                    )
                except Exception as exc:  # Application層の例外をUIに伝える
                    self.notify_error("メモの更新に失敗しました", details=f"{type(exc).__name__}: {exc}")
                    raise

                logger.info(f"Memo updated via edit dialog: id={updated.id}")
                self.show_success_snackbar("メモを更新しました")
                # ダイアログを閉じて表示を更新
                try:
                    dlg.open = False
                    dlg.update()
                except Exception:
                    logger.exception("Failed to close edit dialog")
                self._refresh()

            self.with_loading(_save, user_error_message="メモの更新に失敗しました")

        # ダイアログ定義
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("メモを編集"),
            content=ft.Column(controls=[title_field, content_field], spacing=12),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda _: _close()),
                ft.ElevatedButton("保存", on_click=_on_save),
            ],
        )

        def _close(_: ft.ControlEvent | None = None) -> None:
            try:
                dlg.open = False
                dlg.update()
            except Exception:
                logger.exception("Failed to close edit dialog")

        # 表示
        try:
            self.page.open(dlg)
        except Exception:
            dlg.open = True
            dlg.update()

    def _handle_delete_memo(self, _: ft.ControlEvent) -> None:
        """メモ削除ハンドラー。確認ダイアログ表示のうえ Controller 経由で削除する。"""
        selected_memo = self.controller.current_selection()
        if selected_memo is None:
            return

        def _confirm_delete(_: ft.ControlEvent | None = None) -> None:
            def _do_delete() -> None:
                try:
                    self.controller.delete_memo(selected_memo.id)
                except Exception as exc:
                    self.notify_error("メモの削除に失敗しました", details=f"{type(exc).__name__}: {exc}")
                    raise

                logger.info(f"Memo deleted: id={selected_memo.id}")
                self.show_success_snackbar("メモを削除しました")
                try:
                    confirm_dlg.open = False
                    confirm_dlg.update()
                except Exception:
                    logger.exception("Failed to close edit dialog")
                self._refresh()

            self.with_loading(_do_delete, user_error_message="メモの削除に失敗しました")

        def _cancel(_: ft.ControlEvent | None = None) -> None:
            try:
                confirm_dlg.open = False
                confirm_dlg.update()
            except Exception:
                logger.exception("Failed to close edit dialog")

        confirm_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("メモを削除しますか？"),
            content=ft.Text("この操作は取り消せません。よろしいですか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=_cancel),
                ft.ElevatedButton("削除", bgcolor=get_error_color(), on_click=_confirm_delete),
            ],
        )

        try:
            self.page.open(confirm_dlg)
        except Exception:
            confirm_dlg.open = True
            confirm_dlg.update()

    def _update_detail_panel(self) -> None:
        """詳細パネルを更新。"""
        if hasattr(self, "_detail_panel") and self._detail_panel:
            new_detail_panel = self._build_detail_panel()
            presenter.update_detail_panel_content(self._detail_panel, new_detail_panel)

    def _refresh(self) -> None:
        """ビューの差分更新を一括適用する。"""
        self._update_memo_list()
        self._update_detail_panel()


# ユーティリティ関数


def create_memos_view(props: BaseViewProps) -> MemosView:
    """メモビューを作成。

    Args:
        props: View共通プロパティ

    Returns:
        作成されたメモビュー
    """
    return MemosView(props)
