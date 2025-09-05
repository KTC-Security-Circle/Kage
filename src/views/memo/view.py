"""メモ画面のビューモジュール."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.commands.memo_commands import DeleteMemoCommand
from logic.queries.memo_queries import GetAllMemosQuery, SearchMemosQuery
from views.memo.components import MemoListSection, MemoSearchSection
from views.shared import BaseView, ErrorHandlingMixin

if TYPE_CHECKING:
    from logic.application.memo_application_service import MemoApplicationService
    from models import MemoRead


class MemoView(BaseView, ErrorHandlingMixin):
    """メモ画面のメインビューコンポーネント

    メモの一覧表示、検索、新規追加機能を提供する。
    """

    def __init__(self, page: ft.Page) -> None:
        """MemoViewの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__(page)

        # 依存性注入
        self.memo_app_service: MemoApplicationService = self.container.get_memo_application_service()

        # 状態管理
        self.memos: list[MemoRead] = []
        self.filtered_memos: list[MemoRead] = []

        # UIコンポーネント
        self.search_section: MemoSearchSection | None = None
        self.memo_list_section: MemoListSection | None = None

    def mount(self) -> None:
        """コンポーネントのマウント処理をオーバーライド"""
        # [AI GENERATED] 親クラスのマウント処理を実行
        super().mount()

        # [AI GENERATED] マウント完了後にメモデータを読み込み
        self._load_memos()

    def build_content(self) -> ft.Control:
        """メモ画面のコンテンツを構築

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        # コンポーネント初期化
        self.search_section = MemoSearchSection(
            on_search=self._handle_search,
        )

        self.memo_list_section = MemoListSection(
            memos=[],  # [AI GENERATED] 初期は空のリスト
            on_delete_memo=self._handle_delete_memo,
        )

        # [AI GENERATED] データ読み込みはmount()で実行するため、ここでは呼ばない

        # レイアウト構築
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "メモ",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.PRIMARY,
                            ),
                            ft.ElevatedButton(
                                text="新規作成",
                                icon=ft.Icons.ADD,
                                on_click=self._handle_navigate_to_create,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.BLUE_600,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.Divider(),
                self.search_section,
                ft.Divider(),
                self.memo_list_section,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=10,
            expand=True,
        )

    def _load_memos(self) -> None:
        """メモデータを読み込み"""
        try:
            query = GetAllMemosQuery()
            self.memos = self.memo_app_service.get_all_memos(query)
            self.filtered_memos = self.memos.copy()

            # [AI GENERATED] UI更新
            if self.memo_list_section:
                self.memo_list_section.update_memos(self.filtered_memos)

        except Exception as e:
            logger.exception("メモの読み込みに失敗しました")
            self.show_error("メモの読み込みに失敗しました", str(e))

    def _handle_navigate_to_create(self, _: ft.ControlEvent) -> None:
        """新規作成画面への遷移処理

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/memo/create")

    def _handle_delete_memo(self, memo_id: str) -> None:
        """メモ削除処理

        Args:
            memo_id: 削除するメモのID
        """
        try:
            command = DeleteMemoCommand(memo_id=uuid.UUID(memo_id))
            self.memo_app_service.delete_memo(command)

            # [AI GENERATED] リストを再読み込み
            self._load_memos()
            self.show_success("メモを削除しました")

        except Exception as e:
            logger.exception("メモの削除に失敗しました")
            self.show_error("メモの削除に失敗しました", str(e))

    def _handle_search(self, query: str) -> None:
        """検索処理

        Args:
            query: 検索クエリ
        """
        try:
            if query.strip():
                search_query = SearchMemosQuery(query=query)
                self.filtered_memos = self.memo_app_service.search_memos(search_query)
            else:
                # [AI GENERATED] 空の検索は全件表示
                self.filtered_memos = self.memos.copy()

            # [AI GENERATED] UI更新
            if self.memo_list_section:
                self.memo_list_section.update_memos(self.filtered_memos)

        except Exception as e:
            logger.exception("メモの検索に失敗しました")
            self.show_error("メモの検索に失敗しました", str(e))


def create_memo_view(page: ft.Page) -> ft.Container:
    """メモ画面ビューを作成する関数

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Container: 構築されたメモ画面ビュー
    """
    memo_view = MemoView(page)
    memo_view.mount()  # コンテンツを構築
    return memo_view
