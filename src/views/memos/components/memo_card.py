"""メモカードコンポーネント

【責務】
- 整形済みデータ（MemoCardData）を受け取り、UIを構築する
- カード内のレイアウト、スタイリング、視覚的表現
- クリックイベントをコールバックに委譲
- 選択状態の視覚的フィードバック

【責務外】
- データ変換・フォーマット（Presenterで実行）
- ビジネスロジック（Controllerで実行）
- 状態管理（Stateで管理）

【設計上の特徴】
- MemoCardDataを受け取る設計（データと表示の完全分離）
- このファイル内でデータクラスと専用定数を定義（凝集度向上）
- 内部状態は最小限（表示に必要なデータのみ）
- 純粋な表示コンポーネント（副作用なし）

【使用例】
```python
from views.memos.components.memo_card import MemoCard, MemoCardData
from views.memos.presenter import create_memo_card_data

# Presenterでデータ生成
card_data = create_memo_card_data(memo, is_selected=True, on_click=handler)

# コンポーネントに渡して表示
card = MemoCard(data=card_data)
```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from views.theme import (
    get_outline_color,
    get_primary_color,
    get_text_secondary_color,
)

from .shared.constants import CARD_BORDER_RADIUS

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID


# ========================================
# MemoCard専用定数
# ========================================

MAX_CONTENT_PREVIEW_LENGTH: Final[int] = 200
"""メモコンテンツのプレビュー最大文字数（MemoCard専用）"""

MAX_CONTENT_LINES: Final[int] = 3
"""メモカードに表示する最大行数（MemoCard専用）"""

DEFAULT_MEMO_TITLE: Final[str] = "無題のメモ"
"""タイトルが空の場合のデフォルト値（MemoCard専用）"""


# ========================================
# MemoCard専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class StatusBadgeData:
    """ステータスバッジ表示用データ（MemoCard専用）

    Attributes:
        text: バッジに表示するテキスト（例: "新規", "AI提案済み"）
        color: バッジの背景色（Fletカラー文字列）
        icon: アイコン名（オプション、例: "fiber_new"）
    """

    text: str
    color: str
    icon: str | None = None


@dataclass(frozen=True, slots=True)
class MemoCardData:
    """メモカード表示用データ（MemoCard専用）

    Presenterで整形済みのデータをコンポーネントに渡す。
    コンポーネントはこのデータをそのまま表示するだけ。

    Attributes:
        memo_id: メモのID（イベントハンドリング用）
        title: 表示用タイトル（空の場合はDEFAULT_MEMO_TITLEが設定済み）
        content_preview: 切り詰め済みのコンテンツプレビュー（"..."付き）
        formatted_date: フォーマット済み日付文字列（例: "2025/01/15"）
        badge_data: ステータスバッジ情報（オプション）
        is_selected: 選択状態
        on_click: クリック時のコールバック（オプション）
    """

    memo_id: UUID
    title: str
    content_preview: str
    formatted_date: str
    badge_data: StatusBadgeData | None = None
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class MemoCard(ft.Container):
    """メモカード表示コンポーネント

    整形済みのMemoCardDataを受け取り、視覚的なカードUIを構築する。
    データ変換やフォーマットはPresenterで完了している前提。
    """

    def __init__(
        self,
        data: MemoCardData,
        *,
        max_content_lines: int = MAX_CONTENT_LINES,
    ) -> None:
        """メモカードを初期化。

        Args:
            data: 表示用データ（整形済み）
            max_content_lines: コンテンツの最大表示行数
        """
        self._card_data = data
        self.max_content_lines = max_content_lines

        super().__init__(
            content=ft.Card(
                content=ft.Container(
                    content=self._build_card_content(),
                    padding=ft.padding.all(16),
                ),
                elevation=1 if data.is_selected else 0,
            ),
            margin=ft.margin.symmetric(vertical=4, horizontal=8),
            border_radius=CARD_BORDER_RADIUS,
            border=ft.border.all(
                width=2 if data.is_selected else 0,
                color=get_primary_color() if data.is_selected else get_outline_color(),
            ),
            on_click=self._handle_click if data.on_click else None,
            ink=True,
            key=str(data.memo_id),
        )

    def _build_card_content(self) -> ft.Control:
        """カードの内容を構築（純粋なUI組み立て）。

        Returns:
            構築されたコントロール
        """
        # ヘッダー（タイトル + 選択インジケーター）
        header_controls: list[ft.Control] = [
            ft.Text(
                self._card_data.title,
                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                weight=ft.FontWeight.W_500,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True,
            ),
        ]

        if self._card_data.is_selected:
            header_controls.append(
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=get_primary_color(), size=20),
            )

        header = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # コンテンツ（既に切り詰め済み）
        content_text = ft.Text(
            self._card_data.content_preview,
            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
            color=get_text_secondary_color(),
            max_lines=self.max_content_lines,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        # Divider
        divider = ft.Divider(height=1, color=get_outline_color())

        # フッター（日付 + バッジ）
        footer_controls: list[ft.Control] = [
            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CALENDAR_TODAY,
                        size=16,
                        color=get_text_secondary_color(),
                    ),
                    ft.Text(
                        self._card_data.formatted_date,
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=get_text_secondary_color(),
                    ),
                ],
                spacing=4,
            ),
        ]

        if self._card_data.badge_data:
            footer_controls.append(ft.Container(expand=True))
            footer_controls.append(self._build_status_badge())

        footer = ft.Row(
            controls=footer_controls,
            alignment=ft.MainAxisAlignment.START,
            spacing=8,
        )

        return ft.Column(
            controls=[header, content_text, divider, footer],
            spacing=12,
            tight=True,
        )

    def _build_status_badge(self) -> ft.Container:
        """ステータスバッジを構築（データから生成）。

        Returns:
            バッジコンテナ
        """
        if not self._card_data.badge_data:
            return ft.Container()

        badge = self._card_data.badge_data

        from views.theme import get_on_primary_color

        content: ft.Control
        if badge.icon:
            content = ft.Row(
                controls=[
                    ft.Icon(badge.icon, size=14, color=get_on_primary_color()),
                    ft.Text(
                        badge.text,
                        theme_style=ft.TextThemeStyle.LABEL_SMALL,
                        color=get_on_primary_color(),
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=4,
                tight=True,
            )
        else:
            content = ft.Text(
                badge.text,
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                color=get_on_primary_color(),
                weight=ft.FontWeight.W_500,
            )

        return ft.Container(
            content=content,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=badge.color,
            border_radius=12,
        )

    def _handle_click(self, _: ft.ControlEvent) -> None:
        """クリックイベントをコールバックに委譲。

        Args:
            _: Fletのイベントオブジェクト（未使用）
        """
        if self._card_data.on_click:
            self._card_data.on_click()
