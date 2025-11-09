"""メモビュー

メモ管理のメインハブビュー。
Reactテンプレートを参考に、4つのステータス（Inbox、Active、Idea、Archive）
タブでのメモ管理機能を提供。
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime

import flet as ft
from loguru import logger

from logic.application.apps import ApplicationServices
from models import MemoRead, MemoStatus
from views.shared.base_view import BaseView

from .components import MemoActionBar, MemoCardList, MemoFilters, MemoStatusTabs


@dataclass(slots=True)
class MemosViewData:
    """MemosView 専用の状態データ。

    BaseView.state (loading / error_message) とは分離し、ドメイン表示用の状態のみを保持する。
    """

    current_tab: str = "inbox"
    search_query: str = ""
    all_memos: list[MemoRead] = field(default_factory=list)
    selected_memo: MemoRead | None = None


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

    def __init__(self, page: ft.Page) -> None:
        """メモビューを初期化。

        Args:
            page: Fletページオブジェクト
        """
        super().__init__(page)

        # View 専用状態 (BaseView.state は loading / error_message 用)
        self.view_data: MemosViewData = MemosViewData()

        # UIコンポーネント
        self._action_bar: MemoActionBar | None = None
        self._status_tabs: MemoStatusTabs | None = None
        self._memo_list: MemoCardList | None = None
        self._memo_filters: MemoFilters | None = None
        self._detail_panel: ft.Container | None = None

        # 旧仕様互換: コンストラクタで did_mount を呼ぶ
        self.did_mount()
        # Application Services コンテナから取得
        apps = ApplicationServices.create()
        self.memo_app = apps.memo
        # 初期メモ読み込み (loading 状態表示)
        self.with_loading(self._load_initial_memos, user_error_message="メモの読み込みに失敗しました")

    def did_mount(self) -> None:
        """マウント時の初期化処理。"""
        super().did_mount()
        logger.info("MemosView mounted")

    def build_content(self) -> ft.Control:  # BaseView.build が呼ぶ
        """メモビューのUIを構築。"""
        # アクションバー
        self._action_bar = MemoActionBar(
            on_create_memo=self._handle_create_memo,
            on_search=self._handle_search,
        )

        # ステータスタブ
        self._status_tabs = MemoStatusTabs(
            on_tab_change=self._handle_tab_change,
            active_tab=self.view_data.current_tab,
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
            selected_memo_id=(str(self.view_data.selected_memo.id) if self.view_data.selected_memo else None),
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
        if not self.view_data.selected_memo:
            return ft.Container(content=self._build_empty_detail_panel())
        memo = self.view_data.selected_memo

        # 日付表示の安全な整形（Noneや欠損に対応）
        created_val = getattr(memo, "created_at", None)
        created_text = created_val.strftime("%Y年%m月%d日 %H:%M") if isinstance(created_val, datetime) else "—"
        updated_val = getattr(memo, "updated_at", None)
        updated_text = updated_val.strftime("%Y年%m月%d日 %H:%M") if isinstance(updated_val, datetime) else "—"

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
                                        ft.Text(created_text, style=ft.TextThemeStyle.BODY_SMALL),
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
                                        ft.Text(updated_text, style=ft.TextThemeStyle.BODY_SMALL),
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
        # all_memos を基準に集計（検索や表示状態に依存しない）
        inbox = sum(1 for m in self.view_data.all_memos if m.status == MemoStatus.INBOX)
        active = sum(1 for m in self.view_data.all_memos if m.status == MemoStatus.ACTIVE)
        idea = sum(1 for m in self.view_data.all_memos if m.status == MemoStatus.IDEA)
        archive = sum(1 for m in self.view_data.all_memos if m.status == MemoStatus.ARCHIVE)
        return {
            "inbox": inbox,
            "active": active,
            "idea": idea,
            "archive": archive,
        }

    def _get_current_tab_memos(self) -> list[MemoRead]:
        """現在のタブと検索クエリに基づいてメモ一覧を算出する(派生データ)。

        派生データは state に永続化せず、その都度計算する。
        """
        tab_status = self._status_from_tab_id(self.view_data.current_tab)
        query = (self.view_data.search_query or "").strip()

        if query:
            try:
                return self.memo_app.search(query, with_details=False, status=tab_status)
            except Exception as e:
                # 表示側では空配列を返し、上位で通知する
                logger.error(f"Search failed: {type(e).__name__}: {e}")
                return []

        # 検索なし: all_memos からタブで絞り込み
        base = self.view_data.all_memos
        if tab_status is None:
            return list(base)
        return [m for m in base if m.status == tab_status]

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
        return messages.get(self.view_data.current_tab, "メモはありません")

    def _load_initial_memos(self) -> None:
        """DB から初期メモ一覧を読み込む (Inbox を優先)。"""
        try:
            # まず全件取得（軽量化が必要なら pagination 導入予定）
            all_memos = self.memo_app.get_all_memos(with_details=False)
            # 状態別に並べ替え: INBOX 優先、その後 ACTIVE, IDEA, ARCHIVE
            order = {MemoStatus.INBOX: 0, MemoStatus.ACTIVE: 1, MemoStatus.IDEA: 2, MemoStatus.ARCHIVE: 3}
            ordered: list[MemoRead] = sorted(all_memos, key=lambda m: order.get(m.status, 99))
            self.view_data = replace(self.view_data, all_memos=ordered)
            self._update_memo_list()
            logger.info(f"Loaded {len(self._get_current_tab_memos())} memos from DB")
        except Exception as e:
            self.notify_error("メモの読み込みに失敗しました", details=f"{type(e).__name__}: {e}")

    def _update_memo_list(self) -> None:
        """メモリストを更新。"""
        if self._memo_list:
            current_memos = self._get_current_tab_memos()
            try:
                self._memo_list.update_memos(
                    current_memos,
                    selected_memo_id=(str(self.view_data.selected_memo.id) if self.view_data.selected_memo else None),
                )
            except AssertionError as e:
                if "Control must be added to the page first" in str(e):
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
        # 不変更新: 検索クエリ更新
        self.view_data = replace(self.view_data, search_query=query)
        # 現在の派生リストに選択中メモが含まれない場合は解除
        current = self._get_current_tab_memos()
        if self.view_data.selected_memo and all(self.view_data.selected_memo.id != m.id for m in current):
            self.view_data = replace(self.view_data, selected_memo=None)
        # 再描画
        try:
            self._update_memo_list()
        except Exception as e:
            self.notify_error("検索に失敗しました", details=f"{type(e).__name__}: {e}")
        logger.debug(f"Search query: '{query}' (tab={self.view_data.current_tab})")

    def _handle_tab_change(self, tab_id: str) -> None:
        """タブ変更ハンドラー。

        Args:
            tab_id: 選択されたタブID
        """
        # 不変更新: タブ変更と選択解除
        self.view_data = replace(self.view_data, current_tab=tab_id, selected_memo=None)
        try:
            self._update_memo_list()
        except Exception as e:
            self.notify_error("タブ切替に失敗しました", details=f"{type(e).__name__}: {e}")
        self._update_detail_panel()
        logger.debug(f"Tab changed to: {tab_id}")

    # ------------------------------------------------------------
    # フィルタ適用ロジック（タブ + 検索）
    # ------------------------------------------------------------
    def _status_from_tab_id(self, tab_id: str) -> MemoStatus | None:
        if tab_id == MemoStatus.INBOX.value:
            return MemoStatus.INBOX
        if tab_id == MemoStatus.ACTIVE.value:
            return MemoStatus.ACTIVE
        if tab_id == MemoStatus.IDEA.value:
            return MemoStatus.IDEA
        if tab_id == MemoStatus.ARCHIVE.value:
            return MemoStatus.ARCHIVE
        return None

    # 以前の _apply_filters は派生データを state に保持していたため削除

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
        # 選択状態を不変更新
        self.view_data = replace(self.view_data, selected_memo=memo)
        # リストの選択ハイライトを更新（詳細パネルと同時に切り替える）
        if self._memo_list:
            try:
                self._memo_list.set_selected_memo(str(memo.id))
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
        if self.view_data.selected_memo:
            logger.info(f"Edit memo requested: {self.view_data.selected_memo.id}")
            # TODO: メモ編集ダイアログまたは画面遷移を実装
            self.show_info_snackbar("メモ編集機能は統合フェーズで実装予定です")

    def _handle_delete_memo(self, _: ft.ControlEvent) -> None:
        """メモ削除ハンドラー。"""
        if self.view_data.selected_memo:
            logger.info(f"Delete memo requested: {self.view_data.selected_memo.id}")
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
