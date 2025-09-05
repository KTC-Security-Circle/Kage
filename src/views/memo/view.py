"""メモ画面のビューモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.commands.memo_commands import CreateMemoCommand, DeleteMemoCommand
from logic.queries.memo_queries import GetAllMemosQuery, SearchMemosQuery
from views.memo.components import MemoListSection, MemoSearchSection, NewMemoSection
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

    def build_content(self) -> ft.Control:
        """メモ画面のコンテンツを構築

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        # 新規追加セクション
        new_memo_section = NewMemoSection(on_create_memo=self._handle_create_memo)

        # 検索セクション
        self.search_section = MemoSearchSection(on_search=self._handle_search)

        # メモ一覧セクション
        self.memo_list_section = MemoListSection(memos=self.filtered_memos, on_delete_memo=self._handle_delete_memo)

        # 初期データを読み込み
        self._load_memos()

        return ft.Column(
            [
                new_memo_section,
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

    def _handle_create_memo(self, content: str) -> None:
        """メモ作成処理

        Args:
            content: メモ内容
        """
        try:
            # [AI GENERATED] 現在はダミーのタスクIDを使用（将来的にはオプションに変更予定）
            import uuid

            dummy_task_id = uuid.uuid4()

            command = CreateMemoCommand(
                content=content,
                task_id=dummy_task_id,
            )
            self.memo_app_service.create_memo(command)

            # [AI GENERATED] リストを再読み込み
            self._load_memos()
            self.show_success("メモを作成しました")

        except Exception as e:
            logger.exception("メモの作成に失敗しました")
            self.show_error("メモの作成に失敗しました", str(e))

    def _handle_delete_memo(self, memo_id: str) -> None:
        """メモ削除処理

        Args:
            memo_id: 削除するメモのID
        """
        try:
            import uuid

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
