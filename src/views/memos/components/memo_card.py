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
- 共通TagBadgeData（views.shared.components.card）を使用
- このファイル内でデータクラスと専用定数を定義（凝集度向上）
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

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from views.shared.components import TagBadgeData


# ========================================
# MemoCard専用定数
# ========================================

MAX_CONTENT_PREVIEW_LENGTH: Final[int] = 200
"""メモコンテンツのプレビュー最大文字数（MemoCard専用）"""

MAX_CONTENT_LINES: Final[int] = 3
"""メモカードに表示する最大行数（MemoCard専用）"""

DEFAULT_MEMO_TITLE: Final[str] = "無題のメモ"
"""タイトルが空の場合のデフォルト値（MemoCard専用）"""

LINE_HEIGHT_PX: Final[int] = 20
"""Markdownコンテンツの1行あたりの高さ（ピクセル単位、MemoCard専用）"""

MAX_CONTENT_HEIGHT_PX: Final[int] = 80
"""Markdownコンテンツ表示の最大高さ（ピクセル単位、MemoCard専用）"""


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
        tag_badges: タグバッジのリスト（オプション）
        is_selected: 選択状態
        on_click: クリック時のコールバック（オプション）
    """

    memo_id: UUID
    title: str
    content_preview: str
    formatted_date: str
    badge_data: StatusBadgeData | None = None
    tag_badges: tuple[TagBadgeData, ...] = ()
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class MemoCard(ft.Container):
    """メモカード表示コンポーネント

    整形済みのMemoCardDataを受け取り、視覚的なカードUIを構築する。
    タグバッジを含む独自レイアウトを提供。
    """

    def __init__(
        self,
        data: MemoCardData,
    ) -> None:
        """メモカードを初期化。

        Args:
            data: 表示用データ（整形済み）
        """
        from views.theme import (
            get_on_primary_color,
            get_outline_color,
            get_primary_color,
            get_surface_color,
            get_text_secondary_color,
        )

        # タイトルと説明
        title_text = ft.Text(
            data.title,
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            weight=ft.FontWeight.W_500,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        )

        description_text = ft.Text(
            data.content_preview,
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            color=get_text_secondary_color(),
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=2,
        )

        # バッジとタグの行
        badges_row_controls = []
        if data.badge_data:
            status_badge = ft.Container(
                content=ft.Text(
                    data.badge_data.text,
                    size=11,
                    color=get_on_primary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=data.badge_data.color,
                border_radius=12,
            )
            badges_row_controls.append(status_badge)

        for tag_badge in data.tag_badges:
            tag_container = ft.Container(
                content=ft.Text(
                    tag_badge.name,
                    size=11,
                    color=get_on_primary_color(),
                    weight=ft.FontWeight.W_400,
                ),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=tag_badge.color,
                border_radius=12,
            )
            badges_row_controls.append(tag_container)

        # 日付
        date_text = ft.Text(
            data.formatted_date,
            size=11,
            color=get_text_secondary_color(),
        )

        # メタデータ行（バッジとタグ + 日付）
        metadata_row = ft.Row(
            controls=[
                *badges_row_controls,
                ft.Container(expand=True),  # スペーサー
                date_text,
            ],
            spacing=8,
            wrap=False,
            alignment=ft.MainAxisAlignment.START,
        )

        # カードの内容
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    title_text,
                    description_text,
                    metadata_row,
                ],
                spacing=8,
                tight=True,
            ),
            padding=ft.padding.all(16),
        )

        # 選択状態に応じた境界線
        border_color = get_primary_color() if data.is_selected else get_outline_color()
        border_width = 2 if data.is_selected else 1

        # コンテナ初期化
        super().__init__(
            content=card_content,
            bgcolor=get_surface_color(),
            border=ft.border.all(border_width, border_color),
            border_radius=8,
            on_click=lambda _: data.on_click() if data.on_click else None,
            ink=True,
        )
        self.key = str(data.memo_id)
