"""タスクカードコンポーネント

共通Cardコンポーネントを利用し、TaskCardDataをCardDataに変換して表示する。
親コンポーネントは TaskCardData を生成して本コンポーネントへ渡す。
"""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from views.shared.components.card import Card, CardActionData, CardBadgeData, CardData, CardMetadataData
from views.tasks.components.shared.constants import TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# TaskCard 専用定数
# ========================================

DEFAULT_EMPTY_TITLE: Final[str] = "(無題)"


# ========================================
# TaskCard 専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class TaskCardData:
    """タスクカード表示用データ。

    Attributes:
        task_id: タスクID（イベントハンドリング用）
        title: 表示用タイトル
        subtitle: 補助テキスト（更新日など）
        status: 内部ステータスキー（例: "progress"）
        status_label: 表示用ラベル（例: "進行中"）
        is_selected: 選択状態
        on_click: クリック時のコールバック
    """

    task_id: str
    title: str
    subtitle: str
    status: str
    status_label: str | None = None
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class TaskCard(Card):
    """タスクカード表示コンポーネント。

    共通Cardコンポーネントを継承し、TaskCardDataをCardDataに変換して表示する。
    """

    def __init__(self, data: TaskCardData) -> None:
        from views.theme import get_primary_color

        self._task_data = data

        # ステータスラベルを取得
        status_text = data.status_label or TASK_STATUS_LABELS.get(data.status, data.status)

        # バッジデータ作成
        badge = CardBadgeData(text=status_text, color=get_primary_color()) if status_text else None

        # メタデータ（期限または更新日時）
        metadata_items: list[CardMetadataData] = []
        if hasattr(data, "due_date") and data.due_date:
            metadata_items.append(CardMetadataData(icon=ft.Icons.CALENDAR_TODAY, text=f"期限: {data.due_date}"))
        elif hasattr(data, "status_timestamp") and data.status_timestamp:
            metadata_items.append(CardMetadataData(icon=ft.Icons.UPDATE, text=f"更新: {data.status_timestamp}"))

        # アクション（選択インジケータ）
        actions: list[CardActionData] = []
        if data.is_selected:
            actions.append(
                CardActionData(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    tooltip="選択中",
                    on_click=lambda _: None,
                )
            )

        # CardDataに変換
        card_data = CardData(
            title=data.title or DEFAULT_EMPTY_TITLE,
            description=data.subtitle,
            badge=badge,
            metadata=metadata_items,
            actions=actions,
            is_selected=data.is_selected,
            on_click=data.on_click,
        )

        super().__init__(card_data)
