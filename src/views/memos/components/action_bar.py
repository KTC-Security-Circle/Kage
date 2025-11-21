"""メモアクションバーコンポーネント

【責務】
- 整形済みデータ（ActionBarData）を受け取り、UIを構築する
- アクションバーのレイアウト、スタイリング
- 検索入力、新規作成ボタンのイベント委譲

【責務外】
- 検索クエリのバリデーション（Presenterで            self._search_field = ft.TextField(
                hint_text=self._action_bar_data.search_placeholder,
                width=300,
                prefix_icon=ft.Icons.SEARCH,
                border_radius=20,
                filled=True,
                content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_change=self._handle_search_change,
                on_submit=self._handle_search_submit,
            )
            controls.append(self._search_field)

        if self._action_bar_data.on_create_memo:
            create_button = ft.ElevatedButton(ーマット（Presenterで実行）
- 状態管理（Stateで管理）

【設計上の特徴】
- ActionBarDataを受け取る設計
- このファイル内でデータクラスと専用定数を定義（凝集度向上）
- 検索フィールドの参照を保持（外部から操作可能）

【使用例】
```python
from views.memos.components.action_bar import MemoActionBar, ActionBarData
from views.memos.presenter import create_action_bar_data

data = create_action_bar_data(on_create_memo=handler, on_search=search_handler)
action_bar = MemoActionBar(data=data)
```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from .shared.constants import ACTION_BAR_PADDING

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# MemoActionBar専用定数
# ========================================

MIN_SEARCH_LENGTH: Final[int] = 2
"""検索クエリの最小文字数（MemoActionBar専用）"""

DEFAULT_SEARCH_PLACEHOLDER: Final[str] = "メモを検索..."
"""検索フィールドのデフォルトプレースホルダー（MemoActionBar専用）"""


# ========================================
# MemoActionBar専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class ActionBarData:
    """アクションバー表示用データ（MemoActionBar専用）

    Attributes:
        title: メインタイトル（例: "メモ"）
        subtitle: サブタイトル（例: "思考とアイデアを記録し、AIでタスクに変換"）
        search_placeholder: 検索フィールドのプレースホルダー
        on_create_memo: 新規作成ボタンのコールバック（オプション）
        on_search: 検索入力のコールバック（オプション）
    """

    title: str
    subtitle: str
    search_placeholder: str
    on_create_memo: Callable[[], None] | None = None
    on_search: Callable[[str], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class MemoActionBar(ft.Container):
    """メモ操作用のアクションバー

    整形済みのActionBarDataを受け取り、視覚的なバーUIを構築する。
    """

    def __init__(self, data: ActionBarData) -> None:
        """メモアクションバーを初期化。

        Args:
            data: 表示用データ（整形済み）
        """
        self._action_bar_data = data
        self._search_field: ft.TextField | None = None

        super().__init__(
            content=self._build_action_bar(),
            padding=ft.padding.all(ACTION_BAR_PADDING),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_action_bar(self) -> ft.Control:
        """アクションバーを構築（純粋なUI組み立て）。

        Returns:
            構築されたコントロール
        """
        title_section = ft.Column(
            controls=[
                ft.Text(
                    self._action_bar_data.title,
                    style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    self._action_bar_data.subtitle,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=4,
            tight=True,
        )

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

        if self._action_bar_data.on_search:
            self._search_field = ft.TextField(
                hint_text=self._action_bar_data.search_placeholder,
                width=300,
                prefix_icon=ft.Icons.SEARCH,
                border_radius=20,
                filled=True,
                content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_change=self._handle_search_change,
                on_submit=self._handle_search_submit,
            )
            controls.append(self._search_field)

        if self._action_bar_data.on_create_memo:
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

        return ft.Row(controls=controls, spacing=12)

    def _handle_search_change(self, _: ft.ControlEvent) -> None:
        """検索フィールド変更時のハンドラー（イベント委譲）。

        Args:
            _: Fletのイベントオブジェクト（未使用）
        """
        if not (self._action_bar_data.on_search and self._search_field):
            return

        query = (self._search_field.value or "").strip()

        if not query:
            self._action_bar_data.on_search("")
            return

        if len(query) < MIN_SEARCH_LENGTH:
            return

        self._action_bar_data.on_search(query)

    def _handle_search_submit(self, _: ft.ControlEvent) -> None:
        """検索フィールド送信時のハンドラー（イベント委譲）。

        Args:
            _: Fletのイベントオブジェクト（未使用）
        """
        if self._action_bar_data.on_search and self._search_field:
            self._action_bar_data.on_search(self._search_field.value or "")

    def _handle_create_memo(self, _: ft.ControlEvent) -> None:
        """新規作成ボタンクリック時のハンドラー（イベント委譲）。

        Args:
            _: Fletのイベントオブジェクト（未使用）
        """
        if self._action_bar_data.on_create_memo:
            self._action_bar_data.on_create_memo()

    def clear_search(self) -> None:
        """検索フィールドをクリア（外部から操作）。"""
        if self._search_field:
            self._search_field.value = ""
            self._search_field.update()

    def get_search_query(self) -> str:
        """現在の検索クエリを取得（外部から参照）。

        Returns:
            検索クエリ文字列
        """
        return self._search_field.value or "" if self._search_field else ""

    def set_search_query(self, query: str) -> None:
        """検索クエリを設定（外部から操作）。

        Args:
            query: 設定する検索クエリ
        """
        if self._search_field:
            self._search_field.value = query
            self._search_field.update()
