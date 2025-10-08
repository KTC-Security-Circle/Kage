"""メモ画面のビューモジュール."""

from __future__ import annotations

import contextlib
import uuid
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.application.memo_application_service import MemoApplicationService
from logic.application.task_application_service import TaskApplicationService
from logic.commands.memo_commands import CreateMemoCommand, DeleteMemoCommand
from logic.queries.memo_queries import GetAllMemosQuery, SearchMemosQuery
from logic.queries.task_queries import GetAllTasksByStatusDictQuery
from views.memo.components import MemoListSection, MemoSearchSection
from views.shared import BaseView, ErrorHandlingMixin

if TYPE_CHECKING:
    from models import MemoRead, TaskRead


class MemoCreateView(BaseView, ErrorHandlingMixin):
    """メモ新規作成画面のメインビューコンポーネント

    タスク選択とメモ内容入力機能を提供する。
    """

    def __init__(self, page: ft.Page) -> None:
        """MemoCreateViewの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__(page)

        # 依存性注入
        self.memo_app_service: MemoApplicationService = self.container.get_service(MemoApplicationService)
        self.task_app_service: TaskApplicationService = self.container.get_service(TaskApplicationService)

        # 状態管理
        self.tasks: list[TaskRead] = []
        self.selected_task_id: uuid.UUID | None = None

        # UIコンポーネント
        self.task_dropdown: ft.Dropdown | None = None
        self.content_field: ft.TextField | None = None

    def mount(self) -> None:
        """コンポーネントのマウント処理をオーバーライド"""
        # [AI GENERATED] 親クラスのマウント処理を実行
        super().mount()

        # [AI GENERATED] Dropdownのupdateは自動的にbuild_content内で設定されるため、
        # ここでは追加の処理は不要

    def build_content(self) -> ft.Control:
        """メモ新規作成画面のコンテンツを構築

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        # タスクデータを読み込み
        self._load_tasks()

        # タスク選択ドロップダウン
        self.task_dropdown = ft.Dropdown(
            label="関連するタスクを選択",
            hint_text="メモを関連付けるタスクを選択してください",
            options=self._get_task_options(),
            on_change=self._handle_task_selection,
            expand=True,
        )

        # メモ内容入力フィールド
        self.content_field = ft.TextField(
            label="メモ内容",
            multiline=True,
            min_lines=10,
            max_lines=20,
            hint_text="メモの内容を入力してください...",
            expand=True,
        )

        # ボタン群
        button_row = ft.Row(
            [
                ft.ElevatedButton(
                    text="キャンセル",
                    icon=ft.Icons.CANCEL,
                    on_click=self._handle_cancel,
                    style=ft.ButtonStyle(
                        color=ft.Colors.GREY_700,
                    ),
                ),
                ft.ElevatedButton(
                    text="メモを作成",
                    icon=ft.Icons.SAVE,
                    on_click=self._handle_create,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
        )

        return ft.Column(
            [
                ft.Text(
                    "新規メモ作成",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY,
                ),
                ft.Divider(),
                self.task_dropdown,
                ft.Container(height=10),  # スペーサー
                self.content_field,
                ft.Container(height=20),  # スペーサー
                button_row,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def _load_tasks(self) -> None:
        """タスクデータを読み込み"""
        try:
            query = GetAllTasksByStatusDictQuery()
            tasks_by_status = self.task_app_service.get_all_tasks_by_status_dict(query)

            # [AI GENERATED] 全ステータスのタスクを一つのリストに統合
            self.tasks = []
            for status_tasks in tasks_by_status.values():
                self.tasks.extend(status_tasks)

            logger.debug(f"タスクを読み込みました: {len(self.tasks)}件")

        except Exception as e:
            logger.exception("タスクの読み込みに失敗しました")
            self.show_error("タスクの読み込みに失敗しました", str(e))

    def _get_task_options(self) -> list[ft.dropdown.Option]:
        """タスクドロップダウンのオプションを取得

        Returns:
            list[ft.dropdown.Option]: ドロップダウンオプションのリスト
        """
        options = []
        for task in self.tasks:
            # [AI GENERATED] タスクのタイトルとステータスを表示
            option_text = f"{task.title} ({task.status.value})"
            options.append(ft.dropdown.Option(key=str(task.id), text=option_text))
        return options

    def _handle_task_selection(self, _: ft.ControlEvent) -> None:
        """タスク選択処理

        Args:
            _: イベントオブジェクト
        """
        if self.task_dropdown and self.task_dropdown.value:
            self.selected_task_id = uuid.UUID(self.task_dropdown.value)
            logger.debug(f"タスクが選択されました: {self.selected_task_id}")

    def _handle_cancel(self, _: ft.ControlEvent) -> None:
        """キャンセル処理

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/memo")

    def _handle_create(self, _: ft.ControlEvent) -> None:
        """メモ作成処理

        Args:
            _: イベントオブジェクト
        """
        try:
            # [AI GENERATED] バリデーション
            if not self.content_field or not self.content_field.value or not self.content_field.value.strip():
                self.show_error("メモ内容を入力してください", "")
                return

            if not self.selected_task_id:
                self.show_error("タスクを選択してください", "")
                return

            # [AI GENERATED] メモ作成コマンドを実行
            command = CreateMemoCommand(
                content=self.content_field.value.strip(),
                task_id=self.selected_task_id,
            )

            created_memo = self.memo_app_service.create_memo(command)
            logger.info(f"メモを作成しました: ID {created_memo.id}")

            self.show_success("メモを作成しました")

            # [AI GENERATED] メモ一覧画面に戻る
            self.page.go("/memo")

        except Exception as e:
            logger.exception("メモの作成に失敗しました")
            self.show_error("メモの作成に失敗しました", str(e))


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
        self.memo_app_service: MemoApplicationService = self.container.get_service(MemoApplicationService)

        # 状態管理
        self.memos: list[MemoRead] = []
        self.filtered_memos: list[MemoRead] = []

        # UIコンポーネント
        self.search_section: MemoSearchSection | None = None
        self.memo_list_section: MemoListSection | None = None

    def mount(self) -> None:
        """コンポーネントのマウント処理をオーバーライド"""
        # [AI GENERATED] 親クラスのマウント処理を実行（build_contentが呼ばれる）
        super().mount()

        # [AI GENERATED] マウント完了後にメモデータを読み込み
        self._load_memos()

        # [AI GENERATED] ページに追加された後で初期表示を実行
        if self.memo_list_section and self.filtered_memos:
            # [AI GENERATED] コンポーネントが確実にページに追加されてから更新
            self.page.update()  # ページの状態を同期

            with contextlib.suppress(Exception):
                self.memo_list_section.update_memos(self.filtered_memos)

    def refresh(self) -> None:
        """ビューの再読み込み

        メモデータを再読み込みして一覧を更新する。
        """
        logger.info("MemoView リフレッシュ - データを再読み込み")
        self._load_memos()

        # [AI GENERATED] データ読み込み後に表示を更新
        if self.memo_list_section and self.filtered_memos:

            with contextlib.suppress(Exception):
                self.memo_list_section.update_memos(self.filtered_memos)

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
            memos=[],  # [AI GENERATED] 初期は空のリスト（後でmountで更新）
            on_delete_memo=self._handle_delete_memo,
            on_view_detail=self._handle_view_detail,
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

            # [AI GENERATED] UI更新は_handle_searchで行うため、ここでは実行しない

        except Exception as e:
            logger.exception("メモの読み込みに失敗しました")
            self.show_error("メモの読み込みに失敗しました", str(e))

    def _handle_navigate_to_create(self, _: ft.ControlEvent) -> None:
        """新規作成画面への遷移処理

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/memo/create")

    def _handle_view_detail(self, memo_id: str) -> None:
        """メモ詳細表示処理

        Args:
            memo_id: 表示するメモのID
        """
        self.page.go(f"/memo/detail?id={memo_id}")

    def _handle_delete_memo(self, memo_id: str) -> None:
        """メモ削除処理

        Args:
            memo_id: 削除するメモのID
        """
        try:
            command = DeleteMemoCommand(memo_id=uuid.UUID(memo_id))
            self.memo_app_service.delete_memo(command)

            # [AI GENERATED] リストを再読み込みして表示を更新
            self._load_memos()
            if self.memo_list_section:
                import contextlib

                with contextlib.suppress(Exception):
                    self.memo_list_section.update_memos(self.filtered_memos)
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
                # [AI GENERATED] 検索クエリがある場合は検索を実行
                search_query = SearchMemosQuery(query=query)
                self.filtered_memos = self.memo_app_service.search_memos(search_query)
            else:
                # [AI GENERATED] 空の検索は全件表示
                self.filtered_memos = self.memos.copy()

            # [AI GENERATED] UI更新
            if self.memo_list_section:
                import contextlib

                with contextlib.suppress(Exception):
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


def create_memo_create_view(page: ft.Page) -> ft.Container:
    """メモ新規作成画面ビューを作成する関数

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Container: 構築されたメモ新規作成画面ビュー
    """
    memo_create_view = MemoCreateView(page)
    memo_create_view.mount()  # コンテンツを構築
    return memo_create_view
