"""メモカードコンポーネント

【責務】
- 整形済みデータ（MemoCardData）を受け取り、UIを構築する
- 共通Cardコンポーネントを利用してメモ表示
- クリックイベントをコールバックに委譲
- 選択状態の視覚的フィードバック

【責務外】
- データ変換・フォーマット（Presenterで実行）
- ビジネスロジック（Controllerで実行）
- 状態管理（Stateで管理）

【設計上の特徴】
- MemoCardDataを受け取り、CardDataに変換して共通Cardコンポーネントを使用
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

from views.shared.components.card import Card, CardBadgeData, CardData, CardMetadataData

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


class MemoCard(Card):
    """メモカード表示コンポーネント

    共通Cardコンポーネントを継承し、MemoCardDataをCardDataに変換して表示する。
    タグバッジを含む統一されたレイアウトを提供。
    """

    def __init__(
        self,
        data: MemoCardData,
    ) -> None:
        """メモカードを初期化。

        Args:
            data: 表示用データ（整形済み）
        """
        self._memo_data = data

        # ステータスバッジをCardBadgeDataに変換
        badge = None
        if data.badge_data:
            badge = CardBadgeData(text=data.badge_data.text, color=data.badge_data.color)

        # メタデータ（更新日時）
        metadata_items = [
            CardMetadataData(icon=ft.Icons.UPDATE, text=data.formatted_date),
        ]

        # CardDataに変換
        card_data = CardData(
            title=data.title,
            description=data.content_preview,
            badge=badge,
            tag_badges=data.tag_badges,
            metadata=metadata_items,
            actions=[],
            is_selected=data.is_selected,
            on_click=data.on_click,
        )

        super().__init__(card_data)
        self.key = str(data.memo_id)
