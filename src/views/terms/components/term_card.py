"""用語カードコンポーネント。

【責務】
    用語リストの個別カード表示を担当。
    - Props駆動の不変データ受信
    - カードUI構築（タイトル、キー、説明プレビュー、同義語、ステータスバッジ）
    - 選択状態の視覚的フィードバック
    - クリックイベントのコールバック

【非責務】
    - データ取得・変換 → Presenter
    - 状態管理 → State/Controller
    - ビジネスロジック → Controller
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from models import TermStatus
from views.theme import (
    get_on_surface_color,
    get_outline_color,
    get_primary_color,
    get_surface_variant_color,
    get_text_secondary_color,
)

from .shared.constants import (
    CARD_PADDING,
    MAX_DESCRIPTION_LINES,
    MAX_SYNONYMS_DISPLAY,
)

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# TermCard 専用定数
# ========================================

CARD_BORDER_RADIUS: Final[int] = 8
DEFAULT_BORDER_WIDTH: Final[float] = 1.0
SELECTED_BORDER_WIDTH: Final[float] = 2.0
DEFAULT_EMPTY_TITLE: Final[str] = "(無題)"


# ========================================
# TermCard 専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class TermCardData:
    """用語カード表示用データ。

    Attributes:
        term_id: 用語ID（イベントハンドリング用）
        title: 表示用タイトル
        key: 用語キー
        description: 説明プレビュー
        synonyms: 同義語タプル（不変）
        status: 内部ステータス
        status_text: 表示用ステータステキスト
        is_selected: 選択状態
        on_click: クリック時のコールバック
    """

    term_id: str
    title: str
    key: str
    description: str
    synonyms: tuple[str, ...]
    status: TermStatus
    status_text: str
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class TermCard(ft.Container):
    """用語カード表示コンポーネント。

    Presenter や View 側で整形済みの TermCardData を受け取り、純粋に描画する。
    """

    def __init__(self, data: TermCardData) -> None:
        """Initialize term card.

        Args:
            data: 表示用データ
        """
        self._data = data
        super().__init__(
            content=self._build_card_content(),
            padding=ft.padding.all(CARD_PADDING),
            margin=ft.margin.symmetric(vertical=4),
            border_radius=CARD_BORDER_RADIUS,
            border=ft.border.all(
                width=SELECTED_BORDER_WIDTH if data.is_selected else DEFAULT_BORDER_WIDTH,
                color=get_primary_color() if data.is_selected else get_outline_color(),
            ),
            bgcolor=get_surface_variant_color() if data.is_selected else None,
            on_click=self._handle_click if data.on_click else None,
            ink=True,
            key=data.term_id,
        )

    def _build_card_content(self) -> ft.Control:
        """カードコンテンツを構築する。

        Returns:
            カードコンテンツコントロール
        """
        # Header: Status icon + Title + Status badge
        status_icon = self._get_status_icon()
        title_column = ft.Column(
            controls=[
                ft.Text(
                    self._data.title or DEFAULT_EMPTY_TITLE,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    f"キー: {self._data.key}",
                    size=12,
                    color=get_outline_color(),
                ),
            ],
            spacing=2,
            tight=True,
        )

        header = ft.Row(
            controls=[
                ft.Row(
                    controls=[status_icon, title_column],
                    spacing=8,
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Description preview
        description = ft.Text(
            self._data.description,
            size=14,
            color=get_text_secondary_color(),
            max_lines=MAX_DESCRIPTION_LINES,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        # Synonyms chips
        synonyms_row = self._build_synonyms_display()

        return ft.Column(
            controls=[
                header,
                description,
                synonyms_row,
            ],
            spacing=8,
            tight=True,
        )

    def _get_status_icon(self) -> ft.Control:
        """ステータスアイコンを取得する。

        Returns:
            ステータスアイコンコントロール
        """
        icon_map = {
            TermStatus.APPROVED: ft.Icons.CHECK_CIRCLE,
            TermStatus.DRAFT: ft.Icons.HELP_OUTLINE,
            TermStatus.DEPRECATED: ft.Icons.CANCEL,
        }

        return ft.Icon(
            icon_map.get(self._data.status, ft.Icons.HELP_OUTLINE),
            size=20,
            color=get_on_surface_color(),
        )

    def _build_synonyms_display(self) -> ft.Control:
        """同義語表示を構築する。

        Returns:
            同義語表示コントロール
        """
        if not self._data.synonyms:
            return ft.Container()

        visible_synonyms = self._data.synonyms[:MAX_SYNONYMS_DISPLAY]

        synonym_chips: list[ft.Control] = [
            ft.Container(
                content=ft.Text(
                    synonym,
                    size=12,
                    color=get_on_surface_color(),
                ),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=get_surface_variant_color(),
                border_radius=12,
            )
            for synonym in visible_synonyms
        ]

        if len(self._data.synonyms) > MAX_SYNONYMS_DISPLAY:
            synonym_chips.append(
                ft.Container(
                    content=ft.Text(
                        f"+{len(self._data.synonyms) - MAX_SYNONYMS_DISPLAY}",
                        size=12,
                        color=get_on_surface_color(),
                    ),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=get_surface_variant_color(),
                    border_radius=12,
                )
            )

        return ft.Row(
            controls=synonym_chips,
            spacing=4,
            wrap=True,
        )

    def _handle_click(self, _: ft.ControlEvent) -> None:
        """クリックイベントをハンドリングする。"""
        if self._data.on_click:
            self._data.on_click()
