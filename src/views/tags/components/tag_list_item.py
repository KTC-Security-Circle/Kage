"""タグリストアイテムコンポーネント (Props駆動)

共通Cardコンポーネントを利用し、TagListItemPropsをCardDataに変換して表示する。
選択可能で、カラー円形アイコン、名前、カウント情報を表示する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.shared.components.card import Card, CardBadgeData, CardData, CardMetadataData

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TagListItemProps:
    """タグリストアイテムの表示データとイベント"""

    tag_id: str
    name: str
    color: str
    total_count: int
    memo_count: int
    task_count: int
    selected: bool
    on_click: Callable[[ft.ControlEvent, str], None]


class TagListItem(Card):
    """Propsで駆動されるタグリストアイテム。共通Cardコンポーネントを継承。"""

    def __init__(self, props: TagListItemProps) -> None:
        from views.theme import get_primary_color

        self._props = props
        self._color_dot = ft.Container(
            width=16,
            height=16,
            border_radius=8,
            bgcolor=props.color,
        )

        # バッジ: トータルカウント
        badge = CardBadgeData(text=str(props.total_count), color=get_primary_color())

        # メタデータ: メモ・タスクカウント
        metadata_items = [
            CardMetadataData(icon=ft.Icons.DESCRIPTION_OUTLINED, text=f"{props.memo_count} メモ"),
            CardMetadataData(icon=ft.Icons.TASK_ALT, text=f"{props.task_count} タスク"),
        ]

        card_data = CardData(
            title=props.name,
            description="",  # タグには説明なし
            badge=badge,
            metadata=metadata_items,
            actions=[],  # アクションなし
            is_selected=props.selected,
            on_click=lambda: props.on_click(None, props.tag_id),  # type: ignore[arg-type]
        )

        super().__init__(card_data)

        # カラードットをヘッダーに追加
        self._inject_color_dot()

    def _inject_color_dot(self) -> None:
        """カラードットをタイトルの前に挿入する"""
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
                                # タイトルテキストをRowでラップし、color_dotを前置
                                title_text = title_column.controls[0]
                                title_column.controls[0] = ft.Row(
                                    controls=[self._color_dot, title_text],
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                )
        except (AttributeError, IndexError) as exc:
            logger.warning(f"Failed to inject color dot: {exc}")

    def set_props(self, props: TagListItemProps) -> None:
        """Propsを反映し直す（再構築）"""
        from views.theme import get_primary_color

        self._props = props
        self._color_dot = ft.Container(
            width=16,
            height=16,
            border_radius=8,
            bgcolor=props.color,
        )

        # 再構築
        try:
            badge = CardBadgeData(text=str(props.total_count), color=get_primary_color())

            metadata_items = [
                CardMetadataData(icon=ft.Icons.DESCRIPTION_OUTLINED, text=f"{props.memo_count} メモ"),
                CardMetadataData(icon=ft.Icons.TASK_ALT, text=f"{props.task_count} タスク"),
            ]

            card_data = CardData(
                title=props.name,
                description="",
                badge=badge,
                metadata=metadata_items,
                actions=[],
                is_selected=props.selected,
                on_click=lambda: props.on_click(None, props.tag_id),  # type: ignore[arg-type]
            )

            # 親Cardの内容を更新
            temp_card = Card(card_data)
            self.content = temp_card.content
            # ft.Cardの属性として直接設定
            if hasattr(temp_card, "elevation"):
                self.elevation = temp_card.elevation  # type: ignore[attr-defined]
            self.on_click = temp_card.on_click

            # カラードットを再注入
            self._inject_color_dot()

            self.update()
        except (AttributeError, RuntimeError) as exc:
            logger.warning(f"TagListItem.set_props skipped: {exc}")
