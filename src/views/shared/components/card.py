"""汎用カードコンポーネント

【責務】
- 整形済みデータ（CardData）を受け取り、統一されたカードUIを構築する
- カードのレイアウト、スタイリング（ヘッダー、Divider、フッター）
- 選択状態の視覚的表現（elevation変更）
- アクションボタンのイベント委譲

【責務外】
- データのフォーマット（各ビューのPresenterで実行）
- 状態管理（各ビューのStateで管理）
- ビジネスロジック

【設計上の特徴】
- CardDataを受け取る汎用設計
- ヘッダー（タイトル+バッジ）、Divider、フッター（メタデータ+アクション）の3層構造
- Projects/Tags/Terms/Memosなど様々なビューで再利用可能
- Material Design 3準拠（elevation、spacing、padding）

【使用例】
```python
from views.shared.components.card import Card, CardData, CardBadgeData, CardMetadataData, CardActionData

data = CardData(
    title="プロジェクト名",
    description="プロジェクトの説明文",
    badge=CardBadgeData(
        text="進行中",
        color=get_primary_color(),
    ),
    metadata=[
        CardMetadataData(
            icon=ft.Icons.TASK_ALT,
            text="5 タスク",
        ),
        CardMetadataData(
            icon=ft.Icons.CALENDAR_TODAY,
            text="2024-12-04",
        ),
    ],
    actions=[
        CardActionData(
            icon=ft.Icons.EDIT_OUTLINED,
            tooltip="編集",
            on_click=edit_handler,
        ),
        CardActionData(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="削除",
            on_click=delete_handler,
            icon_color=get_error_color(),
        ),
    ],
    on_click=select_handler,
    is_selected=False,
)
card = Card(data=data)
```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

import flet as ft

from views.theme import (
    get_on_primary_color,
    get_outline_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# Card専用定数
# ========================================

CARD_PADDING: Final[int] = 20
"""カード内部のパディング"""

CARD_SPACING: Final[int] = 16
"""カード内部の要素間スペーシング"""

CARD_ELEVATION_DEFAULT: Final[int] = 1
"""デフォルトのelevation値"""

CARD_ELEVATION_SELECTED: Final[int] = 3
"""選択時のelevation値"""

CARD_BORDER_RADIUS: Final[int] = 8
"""カードの角丸半径"""

BADGE_HORIZONTAL_PADDING: Final[int] = 8
"""バッジの水平パディング"""

BADGE_VERTICAL_PADDING: Final[int] = 4
"""バッジの垂直パディング"""

BADGE_BORDER_RADIUS: Final[int] = 12
"""バッジの角丸半径"""

METADATA_ICON_SIZE: Final[int] = 16
"""メタデータアイコンのサイズ"""

METADATA_SPACING: Final[int] = 4
"""メタデータアイコンとテキストのスペーシング"""

METADATA_ROW_SPACING: Final[int] = 16
"""メタデータ行間のスペーシング"""

ACTION_ICON_SIZE: Final[int] = 20
"""アクションアイコンのサイズ"""

ACTION_BUTTON_SPACING: Final[int] = 0
"""アクションボタン間のスペーシング"""


# ========================================
# Card専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class CardBadgeData:
    """カードバッジの表示データ

    Attributes:
        text: バッジテキスト
        color: バッジ背景色
    """

    text: str
    color: str


@dataclass(frozen=True, slots=True)
class CardMetadataData:
    """カードメタデータの表示データ

    Attributes:
        icon: アイコン（ft.Icons）
        text: 表示テキスト
    """

    icon: str
    text: str


@dataclass(frozen=True, slots=True)
class CardActionData:
    """カードアクションボタンの表示データ

    Attributes:
        icon: アイコン（ft.Icons）
        tooltip: ツールチップ
        on_click: クリック時のコールバック
        icon_color: アイコン色（省略時はtext_secondary_color）
    """

    icon: str
    tooltip: str
    on_click: Callable[[ft.ControlEvent], None]
    icon_color: str | None = None


@dataclass(frozen=True, slots=True)
class CardData:
    """カードの表示データとイベント

    Attributes:
        title: カードタイトル
        description: 説明文
        badge: バッジデータ（省略可）
        metadata: メタデータリスト
        actions: アクションボタンリスト
        on_click: カードクリック時のコールバック（省略可）
        is_selected: 選択状態フラグ
    """

    title: str
    description: str
    badge: CardBadgeData | None = None
    metadata: list[CardMetadataData] = field(default_factory=list)
    actions: list[CardActionData] = field(default_factory=list)
    on_click: Callable[[], None] | None = None
    is_selected: bool = False


# ========================================
# コンポーネント本体
# ========================================


class Card(ft.Container):
    """汎用カードコンポーネント

    整形済みのCardDataを受け取り、統一されたカードUIを構築する。
    Material Design 3準拠のレイアウト（ヘッダー、Divider、フッター）。
    """

    def __init__(self, data: CardData) -> None:
        """カードを初期化する

        Args:
            data: カード表示データ
        """
        self._data = data
        super().__init__()
        self._build_card()

    def _build_card(self) -> None:
        """カードUIを構築する"""
        # ヘッダー（タイトル + 説明 + バッジ）
        header = self._build_header()

        # Divider
        divider = ft.Divider(height=1, color=get_outline_color())

        # フッター（メタデータ + アクション）
        footer = self._build_footer()

        # Card本体
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[header, divider, footer],
                    spacing=CARD_SPACING,
                ),
                padding=CARD_PADDING,
            ),
            elevation=CARD_ELEVATION_SELECTED if self._data.is_selected else CARD_ELEVATION_DEFAULT,
        )
        self.margin = ft.margin.symmetric(vertical=4, horizontal=8)
        self.border_radius = CARD_BORDER_RADIUS
        if self._data.on_click:
            self.on_click = lambda _: self._data.on_click()  # type: ignore[misc]
            self.ink = True

    def _build_header(self) -> ft.Control:
        """ヘッダー（タイトル + 説明 + バッジ）を構築する

        Returns:
            ヘッダーコントロール
        """
        # タイトルと説明
        title_column = ft.Column(
            controls=[
                ft.Text(
                    self._data.title,
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    self._data.description,
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=get_text_secondary_color(),
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=8,
            expand=True,
        )

        # バッジ（存在する場合）
        controls: list[ft.Control] = [title_column]
        if self._data.badge:
            badge = ft.Container(
                content=ft.Text(
                    self._data.badge.text,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    color=get_on_primary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                bgcolor=self._data.badge.color,
                padding=ft.padding.symmetric(
                    horizontal=BADGE_HORIZONTAL_PADDING,
                    vertical=BADGE_VERTICAL_PADDING,
                ),
                border_radius=BADGE_BORDER_RADIUS,
            )
            controls.append(badge)

        return ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _build_footer(self) -> ft.Control:
        """フッター（メタデータ + アクション）を構築する

        Returns:
            フッターコントロール
        """
        footer_controls: list[ft.Control] = []

        # メタデータ
        footer_controls.extend(
            ft.Row(
                controls=[
                    ft.Icon(
                        meta.icon,
                        size=METADATA_ICON_SIZE,
                        color=get_text_secondary_color(),
                    ),
                    ft.Text(
                        meta.text,
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=get_text_secondary_color(),
                    ),
                ],
                spacing=METADATA_SPACING,
            )
            for meta in self._data.metadata
        )

        # スペーサー（アクションがある場合）
        if self._data.actions:
            footer_controls.append(ft.Container(expand=True))

        # アクション
        if self._data.actions:
            action_buttons = []
            for action in self._data.actions:
                icon_color = action.icon_color or get_text_secondary_color()
                action_buttons.append(
                    ft.IconButton(
                        icon=action.icon,
                        tooltip=action.tooltip,
                        icon_size=ACTION_ICON_SIZE,
                        on_click=action.on_click,
                        icon_color=icon_color,
                    )
                )

            footer_controls.append(
                ft.Row(
                    controls=action_buttons,
                    spacing=ACTION_BUTTON_SPACING,
                )
            )

        return ft.Row(
            controls=footer_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=METADATA_ROW_SPACING,
        )
