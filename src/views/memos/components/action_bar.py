"""メモアクションバーコンポーネント

メモの操作（作成、検索、フィルタ等）のためのアクションバー。
Reactテンプレートのヘッダー機能を参考に実装。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


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
        if self.on_search and self._search_field:
            self.on_search(self._search_field.value or "")

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


class MemoStatusTabs(ft.Container):
    """メモステータスタブコンポーネント。

    Inbox、Active、Idea、Archiveの4つのステータスタブを提供。
    テンプレートのTabsListを参考に実装。
    """

    def __init__(
        self,
        *,
        on_tab_change: Callable[[str], None] | None = None,
        active_tab: str = "inbox",
        tab_counts: dict[str, int] | None = None,
    ) -> None:
        """メモステータスタブを初期化。

        Args:
            on_tab_change: タブ変更時のコールバック
            active_tab: アクティブなタブ
            tab_counts: 各タブのメモ数
        """
        self.on_tab_change = on_tab_change
        self.active_tab = active_tab
        self.tab_counts = tab_counts or {}
        self._tab_buttons: dict[str, ft.Control] = {}

        super().__init__(
            content=self._build_tabs(),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_tabs(self) -> ft.Control:
        """タブを構築。

        Returns:
            構築されたタブコントロール
        """
        tab_definitions = [
            ("inbox", "Inbox", ft.Icons.INBOX),
            ("active", "アクティブ", ft.Icons.AUTO_AWESOME),
            ("idea", "アイデア", ft.Icons.LIGHTBULB),
            ("archive", "アーカイブ", ft.Icons.ARCHIVE),
        ]

        tab_controls = []
        for tab_id, label, icon in tab_definitions:
            tab_button = self._create_tab_button(tab_id, label, icon)
            self._tab_buttons[tab_id] = tab_button
            tab_controls.append(tab_button)

        return ft.Row(
            controls=tab_controls,
            spacing=0,
            expand=True,
        )

    def _create_tab_button(self, tab_id: str, label: str, icon: str) -> ft.Control:
        """タブボタンを作成。

        Args:
            tab_id: タブID
            label: タブラベル
            icon: タブアイコン

        Returns:
            作成されたタブボタン
        """
        is_active = tab_id == self.active_tab
        count = self.tab_counts.get(tab_id, 0)

        # タブボタンの内容
        content_controls = [
            ft.Icon(icon, size=18),
            ft.Text(label, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL),
        ]

        # カウントバッジを追加
        if count > 0:
            content_controls.append(
                ft.Container(
                    content=ft.Text(
                        str(count),
                        size=12,
                        color=ft.Colors.ON_SECONDARY,
                        weight=ft.FontWeight.BOLD,
                    ),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=ft.Colors.SECONDARY,
                    border_radius=10,
                ),
            )

        return ft.Container(
            content=ft.Row(
                controls=content_controls,
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT,
            border_radius=8,
            ink=True,
            on_click=lambda _, tid=tab_id: self._handle_tab_click(tid),
            expand=True,
        )

    def _handle_tab_click(self, tab_id: str) -> None:
        """タブクリック時のハンドラー。

        Args:
            tab_id: クリックされたタブのID
        """
        if tab_id != self.active_tab:
            self.active_tab = tab_id
            self._update_tab_styles()
            if self.on_tab_change:
                self.on_tab_change(tab_id)

    def _update_tab_styles(self) -> None:
        """タブのスタイルを更新。"""
        self.content = self._build_tabs()
        if hasattr(self, "page") and self.page:
            self.update()

    def update_counts(self, tab_counts: dict[str, int]) -> None:
        """タブのカウントを更新。

        Args:
            tab_counts: 新しいタブカウント
        """
        self.tab_counts = tab_counts
        self._update_tab_styles()

    def set_active_tab(self, tab_id: str) -> None:
        """アクティブタブを設定。

        Args:
            tab_id: アクティブにするタブのID
        """
        if tab_id != self.active_tab:
            self.active_tab = tab_id
            self._update_tab_styles()
