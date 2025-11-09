"""メモアクションバーコンポーネント

メモの操作（作成、検索、フィルタ等）のためのアクションバー。
Reactテンプレートのヘッダー機能を参考に実装。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


_MIN_SEARCH_LEN = 2


class MemoActionBar(ft.Container):
    """メモ操作用のアクションバー。

    検索、新規作成、フィルタ等の操作機能を提供。
    テンプレートのMemosScreenヘッダー部分を参考に実装。
    """

    def __init__(
        self,
        *,
        on_create_memo: Callable[[], None] | None = None,
        on_search: Callable[[str], None] | None = None,
        search_placeholder: str = "メモを検索...",
        title: str = "メモ",
        subtitle: str = "思考とアイデアを記録し、AIでタスクに変換",
    ) -> None:
        """メモアクションバーを初期化。

        Args:
            on_create_memo: 新規作成ボタンのコールバック
            on_search: 検索入力のコールバック
            search_placeholder: 検索欄のプレースホルダー
            title: タイトルテキスト
            subtitle: サブタイトルテキスト
        """
        self.on_create_memo = on_create_memo
        self.on_search = on_search
        self.search_placeholder = search_placeholder
        self.title = title
        self.subtitle = subtitle
        self._search_field: ft.TextField | None = None

        super().__init__(
            content=self._build_action_bar(),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_action_bar(self) -> ft.Control:
        """アクションバーを構築。

        Returns:
            構築されたコントロール
        """
        # 左側：タイトル部分
        title_section = ft.Column(
            controls=[
                ft.Text(
                    self.title,
                    style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    self.subtitle,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=4,
            tight=True,
        )

        # 右側：操作部分
        action_section = self._build_action_section()

        return ft.Row(
            controls=[title_section, action_section],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_action_section(self) -> ft.Control:
        """操作セクションを構築。

        Returns:
            構築されたコントロール
        """
        controls = []

        # 検索フィールド
        if self.on_search:
            self._search_field = ft.TextField(
                hint_text=self.search_placeholder,
                width=300,
                prefix_icon=ft.Icons.SEARCH,
                border_radius=20,
                filled=True,
                content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_change=self._handle_search_change,
                on_submit=self._handle_search_submit,
            )
            controls.append(self._search_field)

        # 新規作成ボタン
        if self.on_create_memo:
            create_button = ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=18),
                        ft.Text("新しいメモ"),
                    ],
                    spacing=8,
                    tight=True,
                ),
                on_click=self._handle_create_memo,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                ),
            )
            controls.append(create_button)

        return ft.Row(
            controls=controls,
            spacing=12,
        )

    def _handle_search_change(self, _: ft.ControlEvent) -> None:
        """検索フィールド変更時のハンドラー."""
        if not (self.on_search and self._search_field):
            return
        query = (self._search_field.value or "").strip()
        # 入力が空: 検索解除を即時反映
        if not query:
            self.on_search("")
            return
        # 入力が短すぎる場合はノイズを抑制（ライブサーチは2文字以上）
        if len(query) < _MIN_SEARCH_LEN:
            return
        self.on_search(query)

    def _handle_search_submit(self, _: ft.ControlEvent) -> None:
        """検索フィールド送信時のハンドラー."""
        if self.on_search and self._search_field:
            self.on_search(self._search_field.value or "")

    def _handle_create_memo(self, _: ft.ControlEvent) -> None:
        """新規作成ボタンクリック時のハンドラー。"""
        if self.on_create_memo:
            self.on_create_memo()

    def clear_search(self) -> None:
        """検索フィールドをクリア。"""
        if self._search_field:
            self._search_field.value = ""
            self._search_field.update()

    def get_search_query(self) -> str:
        """現在の検索クエリを取得。

        Returns:
            検索クエリ
        """
        return self._search_field.value or "" if self._search_field else ""

    def set_search_query(self, query: str) -> None:
        """検索クエリを設定。

        Args:
            query: 設定する検索クエリ
        """
        if self._search_field:
            self._search_field.value = query
            self._search_field.update()
