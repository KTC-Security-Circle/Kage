"""用語カードコンポーネント。

【責務】
    用語リストの個別カード表示を担当。共通Cardコンポーネントを利用。
    - Props駆動の不変データ受信
    - TermCardDataをCardDataに変換
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
from views.shared.components.card import Card, CardBadgeData, CardData, CardMetadataData, TagBadgeData
from views.theme import get_primary_color

from .shared.constants import MAX_SYNONYMS_DISPLAY

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# TermCard 専用定数
# ========================================

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
        tag_badges: タグバッジデータのタプル（不変）
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
    tag_badges: tuple[TagBadgeData, ...] = ()
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class TermCard(Card):
    """用語カード表示コンポーネント。

    共通Cardコンポーネントを継承し、TermCardDataをCardDataに変換して表示する。
    """

    def __init__(self, data: TermCardData) -> None:
        """Initialize term card.

        Args:
            data: 表示用データ
        """
        self._term_data = data
        self._status_icon = self._get_status_icon(data.status)

        # ステータスバッジ（ボーダー付き）
        badge = CardBadgeData(text=data.status_text, color=get_primary_color())

        # メタデータ: キー + 同義語
        metadata_items = [
            CardMetadataData(icon=ft.Icons.KEY, text=f"キー: {data.key}"),
        ]

        # 同義語をメタデータとして追加
        if data.synonyms:
            synonyms_text = self._format_synonyms(data.synonyms)
            metadata_items.append(CardMetadataData(icon=ft.Icons.LABEL_OUTLINE, text=synonyms_text))

        # CardDataに変換
        card_data = CardData(
            title=data.title or DEFAULT_EMPTY_TITLE,
            description=data.description,
            badge=badge,
            metadata=metadata_items,
            tag_badges=data.tag_badges,
            actions=[],
            is_selected=data.is_selected,
            on_click=data.on_click,
        )

        super().__init__(card_data)

        # ステータスアイコンをタイトルの前に追加
        self._inject_status_icon()

    def _get_status_icon(self, status: TermStatus) -> ft.Icon:
        """ステータスアイコンを取得する。

        Args:
            status: 用語ステータス

        Returns:
            ステータスアイコン
        """
        icon_map = {
            TermStatus.APPROVED: ft.Icons.CHECK_CIRCLE,
            TermStatus.DRAFT: ft.Icons.HELP_OUTLINE,
            TermStatus.DEPRECATED: ft.Icons.CANCEL,
        }

        return ft.Icon(
            icon_map.get(status, ft.Icons.HELP_OUTLINE),
            size=20,
            color=get_primary_color(),
        )

    def _format_synonyms(self, synonyms: tuple[str, ...]) -> str:
        """同義語を文字列にフォーマットする。

        Args:
            synonyms: 同義語タプル

        Returns:
            フォーマットされた同義語文字列
        """
        visible_synonyms = synonyms[:MAX_SYNONYMS_DISPLAY]
        result = ", ".join(visible_synonyms)

        if len(synonyms) > MAX_SYNONYMS_DISPLAY:
            result += f" +{len(synonyms) - MAX_SYNONYMS_DISPLAY}"

        return f"同義語: {result}"

    def _inject_status_icon(self) -> None:
        """ステータスアイコンをタイトルの前に挿入する"""
        try:
            card_content = self.content
            if isinstance(card_content, ft.Card):
                container = card_content.content
                if isinstance(container, ft.Container):
                    column = container.content
                    if isinstance(column, ft.Column) and len(column.controls) > 0:
                        header_row = column.controls[0]
                        if isinstance(header_row, ft.Row) and len(header_row.controls) > 0:
                            title_column = header_row.controls[0]
                            if isinstance(title_column, ft.Column) and len(title_column.controls) > 0:
                                # タイトルテキストをRowでラップし、status_iconを前置
                                title_text = title_column.controls[0]
                                title_column.controls[0] = ft.Row(
                                    controls=[self._status_icon, title_text],
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                )
        except (AttributeError, IndexError):
            pass  # エラーは無視（デフォルト表示のまま）
