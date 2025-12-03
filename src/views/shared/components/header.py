"""汎用アクションバーコンポーネント

【責務】
- 整形済みデータ（HeaderData）を受け取り、UIを構築する
- アクションバーのレイアウト、スタイリング
- 検索入力、アクションボタンのイベント委譲

【責務外】
- 検索クエリのバリデーション（各ビューのPresenterで実行）
- データのフォーマット（各ビューのPresenterで実行）
- 状態管理（各ビューのStateで管理）

【設計上の特徴】
- HeaderDataを受け取る汎用設計
- 複数のアクションボタンをサポート
- 検索フィールドの参照を保持（外部から操作可能）
- Memos/Tags/Tasks/Projectsなど様々なビューで再利用可能

【使用例】
```python
from views.shared.components.header import Header, HeaderData, HeaderButtonData

data = HeaderData(
    title="メモ",
    subtitle="思考とアイデアを記録",
    search_placeholder="メモを検索...",
    on_search=search_handler,
    action_buttons=[
        HeaderButtonData(
            label="新しいメモ",
            icon=ft.Icons.ADD,
            on_click=create_handler,
            is_primary=True,
        ),
    ],
)
action_bar = Header(data=data)
```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from views.theme import get_outline_color, get_surface_color, get_text_secondary_color

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# Header専用定数
# ========================================

MIN_SEARCH_LENGTH: Final[int] = 2
"""検索クエリの最小文字数（汎用Header専用）"""

DEFAULT_SEARCH_PLACEHOLDER: Final[str] = "検索..."
"""検索フィールドのデフォルトプレースホルダー（汎用Header専用）"""

HEADER_PADDING: Final[int] = 20
"""アクションバーのパディング（汎用Header専用）"""


# ========================================
# Header専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class HeaderButtonData:
    """アクションボタン表示用データ

    Attributes:
        label: ボタンのラベルテキスト
        on_click: クリック時のコールバック
        icon: ボタンのアイコン（オプション）
        is_primary: プライマリスタイル（強調表示）を使用するか
        tooltip: ツールチップテキスト（オプション）
        button_id: ボタンの識別子（enable/disableで使用、オプション）
        disabled: 初期状態で無効化するか
        is_outlined: アウトラインスタイルを使用するか
    """

    label: str
    on_click: Callable[[], None]
    icon: str | None = None
    is_primary: bool = True
    tooltip: str | None = None
    button_id: str | None = None
    disabled: bool = False
    is_outlined: bool = False


@dataclass(frozen=True, slots=True)
class HeaderData:
    """アクションバー表示用データ（汎用）

    Attributes:
        title: メインタイトル（例: "メモ"）
        subtitle: サブタイトル（例: "思考とアイデアを記録し、AIでタスクに変換"）
        search_placeholder: 検索フィールドのプレースホルダー
        on_search: 検索入力のコールバック（オプション）
        action_buttons: 右側のアクションボタンのリスト（オプション）
        leading_buttons: 左側のボタンのリスト（戻るボタン等、オプション）
        show_search: 検索フィールドを表示するか
    """

    title: str
    subtitle: str
    search_placeholder: str = DEFAULT_SEARCH_PLACEHOLDER
    on_search: Callable[[str], None] | None = None
    action_buttons: list[HeaderButtonData] | None = None
    leading_buttons: list[HeaderButtonData] | None = None
    show_search: bool = True


# ========================================
# コンポーネント本体
# ========================================


class Header(ft.Container):
    """汎用アクションバー

    整形済みのHeaderDataを受け取り、視覚的なバーUIを構築する。
    様々なビュー（Memos/Tags/Tasks/Projects等）で再利用可能。
    """

    def __init__(self, data: HeaderData) -> None:
        """汎用アクションバーを初期化。

        Args:
            data: 表示用データ（整形済み）
        """
        self._action_bar_data = data
        self._search_field: ft.TextField | None = None
        self._buttons: dict[str, ft.Control] = {}  # button_id -> button参照

        super().__init__(
            content=self._build_action_bar(),
            padding=ft.padding.all(HEADER_PADDING),
            bgcolor=get_surface_color(),
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=get_outline_color())),
        )

    def _build_action_bar(self) -> ft.Control:
        """アクションバーを構築（純粋なUI組み立て）。

        Returns:
            構築されたコントロール
        """
        # 左側: leading_buttons + タイトル
        left_controls = []
        if self._action_bar_data.leading_buttons:
            for button_data in self._action_bar_data.leading_buttons:
                button = self._create_action_button(button_data)
                left_controls.append(button)

        title_section = ft.Column(
            controls=[
                ft.Text(
                    self._action_bar_data.title,
                    theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    self._action_bar_data.subtitle,
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=get_text_secondary_color(),
                ),
            ],
            spacing=4,
            tight=True,
        )
        left_controls.append(title_section)

        left_section = ft.Row(
            controls=left_controls,
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        action_section = self._build_action_section()

        return ft.Row(
            controls=[left_section, action_section],
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
        if self._action_bar_data.show_search and self._action_bar_data.on_search:
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

        # アクションボタン群
        if self._action_bar_data.action_buttons:
            for button_data in self._action_bar_data.action_buttons:
                button = self._create_action_button(button_data)
                controls.append(button)

        return ft.Row(controls=controls, spacing=12)

    def _create_action_button(self, button_data: HeaderButtonData) -> ft.Control:
        """アクションボタンを作成。

        Args:
            button_data: ボタンデータ

        Returns:
            ボタンコントロール
        """
        button_content = []

        if button_data.icon:
            button_content.append(ft.Icon(button_data.icon, size=18))

        button_content.append(ft.Text(button_data.label))

        style = None
        if button_data.is_primary:
            style = ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY,
            )

        # ボタンタイプを選択
        if button_data.is_outlined:
            button = ft.OutlinedButton(
                content=ft.Row(
                    controls=button_content,
                    spacing=8,
                    tight=True,
                ),
                on_click=lambda _: button_data.on_click(),
                tooltip=button_data.tooltip,
                disabled=button_data.disabled,
            )
        elif button_data.is_primary:
            button = ft.FilledButton(
                content=ft.Row(
                    controls=button_content,
                    spacing=8,
                    tight=True,
                ),
                on_click=lambda _: button_data.on_click(),
                tooltip=button_data.tooltip,
                disabled=button_data.disabled,
            )
        else:
            button = ft.ElevatedButton(
                content=ft.Row(
                    controls=button_content,
                    spacing=8,
                    tight=True,
                ),
                on_click=lambda _: button_data.on_click(),
                style=style,
                tooltip=button_data.tooltip,
                disabled=button_data.disabled,
            )

        # button_idが指定されていれば参照を保持
        if button_data.button_id:
            self._buttons[button_data.button_id] = button

        return button

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

    def clear_search(self) -> None:
        """検索フィールドをクリア（外部から操作）。"""
        if self._search_field:
            self._search_field.value = ""
            try:
                self._search_field.update()
            except Exception as e:
                # ページ未追加時のエラーを無視
                from loguru import logger

                logger.debug(f"検索フィールドの更新失敗: {e}")

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
            try:
                self._search_field.update()
            except Exception as e:
                # ページ未追加時のエラーを無視
                from loguru import logger

                logger.debug(f"検索クエリの設定失敗: {e}")

    def enable_button(self, button_id: str) -> None:
        """指定IDのボタンを有効化（外部から操作）。

        Args:
            button_id: ボタンの識別子
        """
        if button_id in self._buttons:
            self._buttons[button_id].disabled = False
            try:
                self._buttons[button_id].update()
            except Exception as e:
                from loguru import logger

                logger.debug(f"ボタン有効化失敗: {e}")

    def disable_button(self, button_id: str) -> None:
        """指定IDのボタンを無効化（外部から操作）。

        Args:
            button_id: ボタンの識別子
        """
        if button_id in self._buttons:
            self._buttons[button_id].disabled = True
            try:
                self._buttons[button_id].update()
            except Exception as e:
                from loguru import logger

                logger.debug(f"ボタン無効化失敗: {e}")
