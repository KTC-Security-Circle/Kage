"""タグリストアイテムコンポーネント (Props駆動)

TagsScreen.tsx のリストアイテムスタイルを参考に実装。
選択可能で、カラー円形アイコン、名前、カウント情報を表示する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.theme import get_grey_color, get_primary_color

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


class TagListItem(ft.Container):
    """Propsで駆動されるタグリストアイテム"""

    def __init__(self, props: TagListItemProps) -> None:
        super().__init__()
        self._props = props
        self._build_content(props)

    def _build_content(self, props: TagListItemProps) -> None:
        """コンテンツを構築する"""
        # カラー円形インジケータ
        color_dot = ft.Container(
            width=16,
            height=16,
            border_radius=ft.border_radius.all(8),
            bgcolor=props.color,
        )

        # トータルカウントバッジ
        count_badge = ft.Container(
            content=ft.Text(
                str(props.total_count),
                size=12,
                weight=ft.FontWeight.W_500,
                color=get_grey_color(700),
            ),
            bgcolor=get_grey_color(200),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=ft.border_radius.all(12),
        )

        # メモ・タスクカウント
        detail_counts = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FILE_PRESENT, size=14, color=get_grey_color(600)),
                        ft.Text(
                            f"{props.memo_count} メモ",
                            size=11,
                            color=get_grey_color(600),
                        ),
                    ],
                    spacing=4,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=14, color=get_grey_color(600)),
                        ft.Text(
                            f"{props.task_count} タスク",
                            size=11,
                            color=get_grey_color(600),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            spacing=16,
        )

        # カードコンテンツ
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    color_dot,
                                    ft.Text(
                                        props.name,
                                        style=ft.TextThemeStyle.TITLE_SMALL,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=8,
                                expand=True,
                            ),
                            count_badge,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    detail_counts,
                ],
                spacing=12,
            ),
            padding=16,
        )

        # 選択状態に応じたスタイル（MD3準拠: 選択時はelevation 1→2）
        border_color = get_primary_color() if props.selected else get_grey_color(300)
        border_width = 2 if props.selected else 1
        elevation = 2 if props.selected else 1

        self.content = ft.Card(
            content=card_content,
            elevation=elevation,
        )
        self.border = ft.border.all(border_width, border_color)
        self.border_radius = ft.border_radius.all(8)
        self.on_click = lambda e: props.on_click(e, props.tag_id)
        self.ink = True

    def set_props(self, props: TagListItemProps) -> None:
        """Propsを反映し直す"""
        self._props = props
        try:
            self._build_content(props)
            self.update()
        except Exception as exc:
            logger.warning(f"TagListItem.set_props skipped: {exc}")
