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

import flet as ft
from loguru import logger

from logic.application.apps import ApplicationServices
from models import MemoRead, MemoStatus
from views.shared.base_view import BaseView, BaseViewProps

from . import presenter
from .components import MemoActionBar, MemoCardList, MemoFilters, MemoStatusTabs
from .controller import MemoApplicationPort, MemosController
from .state import MemosViewState


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
            apps = ApplicationServices.create()
            memo_app = apps.memo
        self.controller = MemosController(memo_app=memo_app, state=self.memos_state)

        # UIコンポーネント
        self._action_bar: MemoActionBar | None = None
        self._status_tabs: MemoStatusTabs | None = None
        self._memo_list: MemoCardList | None = None
        self._memo_filters: MemoFilters | None = None
        self._detail_panel: ft.Container | None = None

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

        return presenter.build_detail_panel(
            selected_memo,
            on_ai_suggestion=self._handle_ai_suggestion,
            on_edit=self._handle_edit_memo,
            on_delete=self._handle_delete_memo,
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
        # TODO: メモ作成ダイアログまたは画面遷移を実装
        self.show_info_snackbar("メモ作成機能は統合フェーズで実装予定です")

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

    def _handle_edit_memo(self, _: ft.ControlEvent) -> None:
        """メモ編集ハンドラー。"""
        selected_memo = self.controller.current_selection()
        if selected_memo:
            logger.info(f"Edit memo requested: {selected_memo.id}")
            # TODO: メモ編集ダイアログまたは画面遷移を実装
            self.show_info_snackbar("メモ編集機能は統合フェーズで実装予定です")

    def _handle_delete_memo(self, _: ft.ControlEvent) -> None:
        """メモ削除ハンドラー。"""
        selected_memo = self.controller.current_selection()
        if selected_memo:
            logger.info(f"Delete memo requested: {selected_memo.id}")
            # TODO: 削除確認ダイアログと実際の削除処理を実装
            self.show_info_snackbar("メモ削除機能は統合フェーズで実装予定です")

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
