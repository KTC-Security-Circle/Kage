"""メモ画面のコンポーネントモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.application.memo_application_service import MemoApplicationService
    from models import MemoRead


class MainMemoSection(ft.Column):
    """メインメモセクションコンポーネント.

    新規メモ作成ボタンと統計情報を表示するセクション。
    """

    def __init__(self, page: ft.Page, memo_app_service: MemoApplicationService) -> None:
        """MainMemoSectionの初期化.

        Args:
            page: Fletのページオブジェクト
            memo_app_service: メモアプリケーションサービスインスタンス
        """
        super().__init__()
        self._page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.memo_app_service = memo_app_service

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.ElevatedButton(
                text="新規メモ作成",
                icon=ft.Icons.ADD,
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16),
                ),
                on_click=self._show_new_memo_dialog,
            ),
            MemoStatsCard(memo_count=self.get_total_memo_count()),
        ]

    def _show_new_memo_dialog(self, _: ft.ControlEvent) -> None:
        """新規メモ作成ダイアログを表示.

        Args:
            _: イベントオブジェクト
        """
        # [AI GENERATED] 新規メモ作成ダイアログの実装
        # 今後、ダイアログまたは専用画面で実装予定
        msg = "新規メモ作成ダイアログは未実装です"
        raise NotImplementedError(msg)

    def get_total_memo_count(self) -> int:
        """総メモ件数を取得.

        Returns:
            総メモ件数
        """
        from logic.queries.memo_queries import GetAllMemosQuery

        query = GetAllMemosQuery()
        memos = self.memo_app_service.get_all_memos(query)
        return len(memos)


class MemoStatsCard(ft.Container):
    """メモ統計情報カードコンポーネント.

    総メモ件数などの統計情報を表示するカード。
    """

    def __init__(self, memo_count: int = 0) -> None:
        """MemoStatsCardの初期化.

        Args:
            memo_count: メモ件数
        """
        super().__init__()
        self.memo_count = memo_count
        self.width = 200

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "総メモ数",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{self.memo_count}件",
                            size=24,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            elevation=2,
        )

    def update_memo_count(self, count: int) -> None:
        """メモ件数を更新.

        Args:
            count: 新しいメモ件数
        """
        self.memo_count = count
        self._build_card()
        self.update()


class MemoSearchSection(ft.Column):
    """メモ検索セクションコンポーネント.

    メモの検索機能を提供するUIセクション。
    """

    def __init__(self, on_search: Callable[[str], None]) -> None:
        """MemoSearchSectionの初期化.

        Args:
            on_search: 検索実行時のコールバック関数
        """
        super().__init__()
        self._on_search = on_search
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.spacing = 10

        # UIコンポーネント
        self.search_field = ft.TextField(
            label="メモを検索",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._handle_search_change,
            hint_text="検索キーワードを入力...",
        )

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.Text(
                "検索",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            self.search_field,
        ]

    def _handle_search_change(self, _: ft.ControlEvent) -> None:
        """検索フィールド変更処理

        Args:
            _: イベントオブジェクト
        """
        query = self.search_field.value or ""
        self._on_search(query)


class MemoListSection(ft.Column):
    """メモ一覧表示セクションコンポーネント.

    メモのリストを表示するUIセクション。
    """

    def __init__(
        self,
        memos: list[MemoRead],
        on_delete_memo: Callable[[str], None],
    ) -> None:
        """MemoListSectionの初期化.

        Args:
            memos: 表示するメモのリスト
            on_delete_memo: メモ削除時のコールバック関数
        """
        super().__init__()
        self._memos = memos
        self._on_delete_memo = on_delete_memo
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.spacing = 10
        self.expand = True

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.Text(
                f"メモ一覧 ({len(self._memos)}件)",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            self._create_memo_list(),
        ]

    def _create_memo_list(self) -> ft.Column:
        """メモリストを作成

        Returns:
            ft.Column: メモリストコンポーネント
        """
        if not self._memos:
            return ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            "メモがありません",
                            size=16,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        padding=20,
                    )
                ]
            )

        memo_items = [self._create_memo_item(memo) for memo in self._memos]

        return ft.Column(
            memo_items,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_memo_item(self, memo: MemoRead) -> ft.Card:
        """個別メモアイテムを作成

        Args:
            memo: メモオブジェクト

        Returns:
            ft.Card: メモアイテムカード
        """
        # [AI GENERATED] メモ内容のプレビュー文字数の定数
        preview_max_length = 100

        # [AI GENERATED] メモ内容のプレビュー（最初の100文字）
        content_preview = memo.content
        if len(content_preview) > preview_max_length:
            content_preview = content_preview[:preview_max_length] + "..."

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    f"ID: {str(memo.id)[:8]}...",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="削除",
                                    on_click=lambda _, memo_id=str(memo.id): self._handle_delete_click(memo_id),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            content_preview,
                            size=14,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=3,
                        ),
                    ],
                    spacing=5,
                ),
                padding=15,
            ),
            elevation=2,
        )

    def _handle_delete_click(self, memo_id: str) -> None:
        """削除ボタンクリック処理

        Args:
            memo_id: 削除するメモのID
        """
        self._on_delete_memo(memo_id)

    def update_memos(self, memos: list[MemoRead]) -> None:
        """メモリストを更新

        Args:
            memos: 新しいメモリスト
        """
        self._memos = memos
        self._build_components()
        # [AI GENERATED] 安全にupdateを実行
        import contextlib

        with contextlib.suppress(Exception):
            self.update()


class MemoActionCard(ft.Container):
    """メモアクション用のカードコンポーネント.

    メモ画面で使用する再利用可能なアクションカード。
    """

    def __init__(
        self,
        title: str,
        icon: str,
        description: str,
        on_click_handler: Callable | None = None,
    ) -> None:
        """MemoActionCardの初期化.

        Args:
            title: カードのタイトル
            icon: 表示するアイコン
            description: カードの説明文
            on_click_handler: クリック時のハンドラー関数
        """
        super().__init__()
        self.title = title
        self.icon = icon
        self.description = description
        self.on_click = on_click_handler

        # カードコンテンツを構築
        self._build_card()

    def _build_card(self) -> None:
        """カードのコンテンツを構築."""
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=self.icon,
                            size=40,
                        ),
                        ft.Text(
                            self.title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            self.description,
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=20,
                width=150,
                height=120,
            ),
            elevation=2,
        )


def create_memo_welcome_message() -> ft.Container:
    """メモ用ウェルカムメッセージを作成.

    Returns:
        ウェルカムメッセージのContainerコンポーネント
    """
    return ft.Container(
        content=ft.Text(
            "メモでアイデアを整理しよう！",
            size=18,
        ),
        alignment=ft.alignment.center,
    )
