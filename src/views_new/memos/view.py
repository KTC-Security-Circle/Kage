"""メモビュー

メモ管理のメインハブビュー。
Reactテンプレートを参考に、4つのステータス（Inbox、Active、Idea、Archive）
タブでのメモ管理機能を提供。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views_new.shared.base_view import BaseView, ErrorHandlingMixin

from .components import MemoActionBar, MemoCardList, MemoFilters, MemoStatusTabs

if TYPE_CHECKING:
    from views_new.sample import SampleMemo


class MemosView(BaseView, ErrorHandlingMixin):
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

    def __init__(self, page: ft.Page) -> None:
        """メモビューを初期化。

        Args:
            page: Fletページオブジェクト
        """
        super().__init__(page)

        # TODO: 依存性注入を統合フェーズで実装
        # 理由: MemoApplicationServiceとの連携が未実装のため
        # 置換先: self.memo_app_service = container.get_service(MemoApplicationService)

        # 状態管理
        self.current_tab = "inbox"
        self.search_query = ""
        self.memos: list[SampleMemo] = []
        self.filtered_memos: list[SampleMemo] = []
        self.selected_memo: SampleMemo | None = None

        # UIコンポーネント
        self._action_bar: MemoActionBar | None = None
        self._status_tabs: MemoStatusTabs | None = None
        self._memo_list: MemoCardList | None = None
        self._memo_filters: MemoFilters | None = None
        self._detail_panel: ft.Container | None = None

        self.did_mount()

    def did_mount(self) -> None:
        """マウント時の初期化処理。"""
        super().did_mount()
        logger.info("MemosView mounted")

    def build(self) -> ft.Control:
        """メモビューのUIを構築。

        Returns:
            構築されたUIコントロール
        """
        # アクションバー
        self._action_bar = MemoActionBar(
            on_create_memo=self._handle_create_memo,
            on_search=self._handle_search,
        )

        # ステータスタブ
        self._status_tabs = MemoStatusTabs(
            on_tab_change=self._handle_tab_change,
            active_tab=self.current_tab,
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
        current_memos = self._get_current_tab_memos()
        self._memo_list = MemoCardList(
            memos=current_memos,
            on_memo_select=self._handle_memo_select,
            empty_message=self._get_empty_message(),
        )

        # 詳細パネル
        self._detail_panel = self._build_detail_panel()

        # レスポンシブレイアウト
        layout = ft.Container(
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

        # 初期データを読み込み（コンポーネントが構築済みの状態で）
        self._load_memos()

        return layout

    def _build_detail_panel(self) -> ft.Container:
        """詳細パネルを構築。

        Returns:
            詳細パネルコントロール
        """
        if not self.selected_memo:
            return ft.Container(content=self._build_empty_detail_panel())

        memo = self.selected_memo

        # メモ詳細カード
        detail_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # ヘッダー
                        ft.Row(
                            controls=[
                                ft.Text(
                                    memo.title or "無題のメモ",
                                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                                # TODO: AI提案バッジを統合フェーズで実装
                                self._build_memo_status_badge(),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # 内容
                        ft.Container(
                            content=ft.Text(
                                memo.content,
                                style=ft.TextThemeStyle.BODY_MEDIUM,
                                selectable=True,
                            ),
                            padding=ft.padding.all(16),
                            bgcolor=ft.Colors.SECONDARY_CONTAINER,
                            border_radius=8,
                        ),
                        # メタデータ
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "作成日",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            memo.created_at.strftime("%Y年%m月%d日 %H:%M"),
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "更新日",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            memo.updated_at.strftime("%Y年%m月%d日 %H:%M"),
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=32,
                        ),
                        # アクションボタン
                        self._build_detail_actions(),
                    ],
                    spacing=16,
                ),
                padding=ft.padding.all(20),
            ),
        )

        return ft.Container(
            content=ft.Column(
                controls=[detail_card],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        )

    def _build_empty_detail_panel(self) -> ft.Control:
        """空の詳細パネルを構築。

        Returns:
            空の詳細パネルコントロール
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.DESCRIPTION, size=64, color=ft.Colors.OUTLINE),
                    ft.Text(
                        "メモを選択して詳細を表示",
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "左側のリストからメモを選択すると、\nここに詳細が表示されます。",
                        style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _build_memo_status_badge(self) -> ft.Container:
        """メモステータスバッジを構築。

        Returns:
            ステータスバッジコントロール
        """
        # TODO: 実際のメモステータスに基づいた実装に変更
        return ft.Container(
            content=ft.Text(
                "新規",
                size=12,
                color=ft.Colors.ON_PRIMARY,
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
            bgcolor=ft.Colors.PRIMARY,
            border_radius=12,
        )

    def _build_detail_actions(self) -> ft.Control:
        """詳細パネルのアクションボタンを構築。

        Returns:
            アクションボタンコントロール
        """
        return ft.Column(
            controls=[
                # TODO: AI提案機能を統合フェーズで実装
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.AUTO_AWESOME, size=16),
                                    ft.Text("AIでタスクを生成"),
                                ],
                                spacing=8,
                                tight=True,
                            ),
                            on_click=self._handle_ai_suggestion,
                            expand=True,
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        ft.OutlinedButton(
                            "編集",
                            icon=ft.Icons.EDIT,
                            on_click=self._handle_edit_memo,
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            "削除",
                            icon=ft.Icons.DELETE,
                            on_click=self._handle_delete_memo,
                            expand=True,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        )

    def _get_tab_counts(self) -> dict[str, int]:
        """各タブのメモ数を取得。

        Returns:
            タブ別メモ数辞書
        """
        # TODO: 実際のメモステータスに基づいた実装に変更
        # 現在は仮の実装
        return {
            "inbox": len([m for m in self.memos if True]),  # 全てのメモをInboxとして扱う
            "active": 0,
            "idea": 0,
            "archive": 0,
        }

    def _get_current_tab_memos(self) -> list[SampleMemo]:
        """現在のタブのメモを取得。

        Returns:
            現在のタブのメモリスト
        """
        # TODO: 実際のメモステータスフィルタリングを実装
        # 現在は検索フィルタのみ適用
        if self.search_query:
            return [
                memo
                for memo in self.memos
                if self.search_query.lower() in memo.content.lower()
                or (memo.title and self.search_query.lower() in memo.title.lower())
            ]
        return self.memos

    def _get_empty_message(self) -> str:
        """空のメッセージを取得。

        Returns:
            現在のタブに応じた空メッセージ
        """
        messages = {
            "inbox": "Inboxメモはありません",
            "active": "アクティブなメモはありません",
            "idea": "アイデアメモはありません",
            "archive": "アーカイブされたメモはありません",
        }
        return messages.get(self.current_tab, "メモはありません")

    def _load_memos(self) -> None:
        """メモデータを読み込み。"""
        try:
            # Load sample data for demonstration
            from views_new.sample import get_sample_memos

            self.memos = get_sample_memos()
            self._update_memo_list()
            logger.info(f"Loaded {len(self.memos)} memos")
        except Exception as e:
            logger.error(f"Failed to load memos: {e}")
            if self.page:
                self.handle_exception_with_snackbar(
                    self.page,
                    e,
                    "メモの読み込みに失敗しました",
                )

    def _update_memo_list(self) -> None:
        """メモリストを更新。"""
        if self._memo_list:
            current_memos = self._get_current_tab_memos()
            # Check if component is properly initialized before updating
            try:
                self._memo_list.update_memos(current_memos)
            except AssertionError as e:
                if "Control must be added to the page first" in str(e):
                    # Component not yet added to page, skip update
                    logger.warning(f"Skipping memo list update: {e}")
                else:
                    raise

        if self._status_tabs:
            try:
                self._status_tabs.update_counts(self._get_tab_counts())
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
        self.search_query = query
        self._update_memo_list()
        logger.debug(f"Search query: '{query}'")

    def _handle_tab_change(self, tab_id: str) -> None:
        """タブ変更ハンドラー。

        Args:
            tab_id: 選択されたタブID
        """
        self.current_tab = tab_id
        self.selected_memo = None
        self._update_memo_list()
        self._update_detail_panel()
        logger.debug(f"Tab changed to: {tab_id}")

    def _handle_filter_change(self, filter_data: dict[str, object]) -> None:
        """フィルタ変更ハンドラー。

        Args:
            filter_data: フィルタデータ
        """
        # TODO: フィルタリングロジックを実装
        logger.debug(f"Filter changed: {filter_data}")
        self._update_memo_list()

    def _handle_memo_select(self, memo: SampleMemo) -> None:
        """メモ選択ハンドラー。

        Args:
            memo: 選択されたメモ
        """
        self.selected_memo = memo
        self._update_detail_panel()
        logger.debug(f"Memo selected: {memo.id}")

    def _handle_ai_suggestion(self, _: ft.ControlEvent) -> None:
        """AI提案ハンドラー。"""
        logger.info("AI suggestion requested")
        # TODO: AI提案機能を実装
        self.show_info_snackbar("AI提案機能は統合フェーズで実装予定です")

    def _handle_edit_memo(self, _: ft.ControlEvent) -> None:
        """メモ編集ハンドラー。"""
        if self.selected_memo:
            logger.info(f"Edit memo requested: {self.selected_memo.id}")
            # TODO: メモ編集ダイアログまたは画面遷移を実装
            self.show_info_snackbar("メモ編集機能は統合フェーズで実装予定です")

    def _handle_delete_memo(self, _: ft.ControlEvent) -> None:
        """メモ削除ハンドラー。"""
        if self.selected_memo:
            logger.info(f"Delete memo requested: {self.selected_memo.id}")
            # TODO: 削除確認ダイアログと実際の削除処理を実装
            self.show_info_snackbar("メモ削除機能は統合フェーズで実装予定です")

    def _update_detail_panel(self) -> None:
        """詳細パネルを更新。"""
        if hasattr(self, "_detail_panel") and self._detail_panel:
            new_detail_panel = self._build_detail_panel()
            self._detail_panel.content = new_detail_panel.content
            self._detail_panel.update()


# ユーティリティ関数


def create_memos_view(page: ft.Page) -> MemosView:
    """メモビューを作成。

    Args:
        page: Fletページオブジェクト

    Returns:
        作成されたメモビュー
    """
    return MemosView(page)
