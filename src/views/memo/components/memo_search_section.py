"""メモ検索セクションコンポーネントモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


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
