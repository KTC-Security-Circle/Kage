"""メモ一覧表示セクションコンポーネントモジュール."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import MemoRead


class MemoListSection(ft.Column):
    """メモ一覧表示セクションコンポーネント.

    メモのリストを表示するUIセクション。
    """

    def __init__(
        self,
        memos: list[MemoRead],
        on_delete_memo: Callable[[str], None],
        on_view_detail: Callable[[str], None] | None = None,
    ) -> None:
        """MemoListSectionの初期化.

        Args:
            memos: 表示するメモのリスト
            on_delete_memo: メモ削除時のコールバック関数
            on_view_detail: メモ詳細表示時のコールバック関数
        """
        super().__init__()
        self._memos = memos
        self._on_delete_memo = on_delete_memo
        self._on_view_detail = on_view_detail
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
                                ft.Row(
                                    [
                                        *(
                                            [
                                                ft.IconButton(
                                                    icon=ft.Icons.VISIBILITY,
                                                    icon_color=ft.Colors.BLUE_400,
                                                    tooltip="詳細",
                                                    on_click=lambda _, memo_id=str(memo.id): (
                                                        self._handle_detail_click(memo_id)
                                                    ),
                                                )
                                            ]
                                            if self._on_view_detail
                                            else []
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_400,
                                            tooltip="削除",
                                            on_click=lambda _, memo_id=str(memo.id): self._handle_delete_click(memo_id),
                                        ),
                                    ],
                                    spacing=0,
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

    def _handle_detail_click(self, memo_id: str) -> None:
        """詳細ボタンクリック処理

        Args:
            memo_id: 詳細を表示するメモのID
        """
        if self._on_view_detail:
            self._on_view_detail(memo_id)

    def update_memos(self, memos: list[MemoRead]) -> None:
        """メモリストを更新

        Args:
            memos: 新しいメモリスト
        """
        self._memos = memos
        self._build_components()

        with contextlib.suppress(Exception):
            self.update()
