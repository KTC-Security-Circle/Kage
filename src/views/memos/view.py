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
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import flet as ft
from loguru import logger

from logic.application.memo_application_service import MemoApplicationService
from models import AiSuggestionStatus, MemoRead, MemoStatus
from views.shared.base_view import BaseView, BaseViewProps

from . import presenter
from .components import MemoActionBar, MemoCardList, MemoFilters, MemoStatusTabs
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
        self._action_bar: MemoActionBar | None = None
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
        action_bar_data = presenter.create_action_bar_data(
            on_create_memo=self._handle_create_memo,
            on_search=self._handle_search,
        )
        self._action_bar = MemoActionBar(action_bar_data)

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
                self._action_bar,
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
                        border=ft.border.only(right=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
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
            on_ai_suggestion=self._handle_ai_suggestion,
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

    def _handle_tab_change(self, status: MemoStatus) -> None:
        """タブ変更ハンドラー。

        Args:
            status: 選択されたタブのステータス
        """
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
        """MemoToTaskAgentによるタスク生成を擬似的に開始する。"""
        ai_state = self.memos_state.ai_flow_state_for(memo.id)
        ai_state.editing_task_id = None
        ai_state.is_generating = True
        self.memos_state.set_ai_status_override(memo.id, AiSuggestionStatus.PENDING)
        memo.ai_suggestion_status = AiSuggestionStatus.PENDING
        if memo.status == MemoStatus.INBOX:
            memo.status = MemoStatus.ACTIVE
        self._refresh()
        try:
            self.page.run_task(self._simulate_ai_generation, memo.id)
        except Exception:  # page.run_task未サポート時のフォールバック
            task = asyncio.create_task(self._simulate_ai_generation(memo.id))
            self._pending_async_tasks.append(task)

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
        memo.status = MemoStatus.IDEA
        memo.ai_suggestion_status = AiSuggestionStatus.NOT_REQUESTED
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
        if ai_state.editing_task_id == task_id:
            ai_state.editing_task_id = None
        self.show_success_snackbar("タスク内容を更新しました")
        self._refresh()

    def _handle_delete_ai_task(self, memo_id: UUID, task_id: str) -> None:
        """AI提案タスクを削除する。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.generated_tasks = [task for task in ai_state.generated_tasks if task.task_id != task_id]
        ai_state.selected_task_ids.discard(task_id)
        if ai_state.editing_task_id == task_id:
            ai_state.editing_task_id = None
        self._refresh()

    def _handle_add_ai_task(self, memo_id: UUID) -> None:
        """AI提案リストに空のタスクを追加する。"""
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        task = AiSuggestedTask(
            task_id=f"temp-{uuid4().hex}",
            title="新しいタスク",
            description="",
            tags=(),
            due_date=datetime.now() + timedelta(days=7),
        )
        ai_state.generated_tasks.append(task)
        ai_state.editing_task_id = task.task_id
        ai_state.selected_task_ids.add(task.task_id)
        self._refresh()

    def _handle_approve_ai_tasks(self, memo: MemoRead) -> None:
        """選択されたAI提案タスクを承認済みとして扱う。"""
        ai_state = self.memos_state.ai_flow_state_for(memo.id)
        if not ai_state.selected_task_ids:
            self.show_snack_bar("承認するタスクを選択してください", bgcolor=ft.Colors.ERROR)
            return
        ai_state.status_override = AiSuggestionStatus.REVIEWED
        memo.ai_suggestion_status = AiSuggestionStatus.REVIEWED
        memo.status = MemoStatus.ARCHIVE
        self.show_success_snackbar("タスクを承認し、メモをアーカイブしました")
        self._refresh()

    async def _simulate_ai_generation(self, memo_id: UUID) -> None:
        """AI提案生成処理を擬似的に遅延させる。"""
        await asyncio.sleep(2)
        self._complete_ai_generation(memo_id)

    def _complete_ai_generation(self, memo_id: UUID) -> None:
        """モックのAI生成完了処理を行う。"""
        memo = self._get_memo_by_id(memo_id)
        if memo is None:
            return
        tasks = self._generate_mock_tasks(memo)
        self.memos_state.set_generated_tasks(memo_id, tasks)
        ai_state = self.memos_state.ai_flow_state_for(memo_id)
        ai_state.status_override = AiSuggestionStatus.AVAILABLE
        ai_state.is_generating = False
        memo.ai_suggestion_status = AiSuggestionStatus.AVAILABLE
        memo.status = MemoStatus.ACTIVE
        self.show_success_snackbar("AI提案タスクを取得しました")
        self._refresh()

    def _generate_mock_tasks(self, memo: MemoRead) -> list[AiSuggestedTask]:
        """UIデモ用のモックタスクを生成する。"""
        base_title = memo.title or "メモ"
        now = datetime.now()
        templates = [
            (
                f"{base_title}の要件整理",
                "メモの内容を整理し、MemoToTaskAgentで扱いやすい形にまとめる",
                ("planning",),
                3,
            ),
            (
                "実装ステップの洗い出し",
                "必要なタスクを分解し、優先度付きで並べる",
                ("execution", "priority"),
                5,
            ),
            (
                "承認準備",
                "生成されたタスクをユーザーに提示できる形に整える",
                ("review",),
                7,
            ),
        ]
        generated: list[AiSuggestedTask] = []
        for idx, (title, description, tags, offset_days) in enumerate(templates, start=1):
            generated.append(
                AiSuggestedTask(
                    task_id=f"temp-{memo.id}-{idx}-{uuid4().hex[:6]}",
                    title=title,
                    description=description,
                    tags=tuple(tags),
                    due_date=now + timedelta(days=offset_days),
                )
            )
        return generated

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
                self.show_snack_bar("内容を入力してください", bgcolor=ft.Colors.ERROR)
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
                ft.ElevatedButton("削除", bgcolor=ft.Colors.ERROR, on_click=_confirm_delete),
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
