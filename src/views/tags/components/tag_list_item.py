"""タグリストアイテムコンポーネント (Props駆動)

TagsScreen.tsx のリストアイテムスタイルを参考に実装。
選択可能で、カラー円形アイコン、名前、カウント情報を表示する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.theme import (
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_text_secondary_color,
)

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
        """コンテンツを構築する（プロジェクトカードパターン準拠）"""
        # カラー円形インジケータ
        color_dot = ft.Container(
            width=16,
            height=16,
            border_radius=8,
            bgcolor=props.color,
        )

        # トータルカウントバッジ
        count_badge = ft.Container(
            content=ft.Text(
                str(props.total_count),
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                weight=ft.FontWeight.W_500,
                color=get_on_primary_color(),
            ),
            bgcolor=get_primary_color(),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=12,
        )

        # ヘッダー行（タグ名 + カウントバッジ）
        header = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        color_dot,
                        ft.Text(
                            props.name,
                            theme_style=ft.TextThemeStyle.TITLE_SMALL,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    spacing=8,
                    expand=True,
                ),
                count_badge,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Divider
        divider = ft.Divider(height=1, color=get_outline_color())

        # フッター（メモ・タスクカウント）
        footer = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            size=16,
                            color=get_text_secondary_color(),
                        ),
                        ft.Text(
                            f"{props.memo_count} メモ",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=get_text_secondary_color(),
                        ),
                    ],
                    spacing=4,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.TASK_ALT,
                            size=16,
                            color=get_text_secondary_color(),
                        ),
                        ft.Text(
                            f"{props.task_count} タスク",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=get_text_secondary_color(),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            spacing=16,
        )

        # Card本体(プロジェクトカードパターン)
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[header, divider, footer],
                    spacing=16,
                ),
                padding=20,
            ),
            elevation=1 if not props.selected else 3,
        )
        self.margin = ft.margin.symmetric(vertical=4, horizontal=8)
        self.border_radius = 8
        self.on_click = lambda e: props.on_click(e, props.tag_id)
        self.ink = True

    def set_props(self, props: TagListItemProps) -> None:
        """Propsを反映し直す"""
        self._props = props
        try:
            self._build_content(props)
            self.update()
        except (AttributeError, RuntimeError) as exc:
            logger.warning(f"TagListItem.set_props skipped: {exc}")
