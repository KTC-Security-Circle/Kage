"""タグカードコンポーネント (Props駆動)。

タグの要約を表示するカード。名称チップクリックで選択、右上のアイコンで編集/削除をトリガ。
`ft.Card` を内包する `ft.Container` サブクラスで構築し、`set_props()` による差分更新に対応。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TagCardProps:
    """タグカードの表示データとイベント。"""

    tag: dict[str, str]
    selected: bool
    on_edit: Callable[[ft.ControlEvent, dict[str, str]], None]
    on_delete: Callable[[ft.ControlEvent, dict[str, str]], None]
    on_select: Callable[[ft.ControlEvent, dict[str, str]], None]


class TagCard(ft.Container):
    """Propsで駆動されるタグカード。"""

    def __init__(self, props: TagCardProps) -> None:
        super().__init__()
        self._props = props
        self.content = self._build(props)

    def _build(self, props: TagCardProps) -> ft.Control:
        tag = props.tag
        chip = ft.Container(
            content=ft.Text(
                tag["name"],
                style=ft.TextThemeStyle.LABEL_MEDIUM,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=tag["color"],
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=ft.border_radius.all(16),
            on_click=lambda e, t=tag: props.on_select(e, t),
            tooltip="選択",
        )

        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        chip,
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    tag["description"],
                                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                    ],
                                    spacing=12,
                                    expand=True,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_OUTLINED,
                                            tooltip="編集",
                                            icon_size=20,
                                            on_click=lambda e, t=tag: props.on_edit(e, t),
                                            icon_color=ft.Colors.GREY_600,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            tooltip="削除",
                                            icon_size=20,
                                            on_click=lambda e, t=tag: props.on_delete(e, t),
                                            icon_color=ft.Colors.RED,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Divider(height=1, color=ft.Colors.GREY_300),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.TASK_ALT, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(
                                            f"{tag['task_count']} タスク",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(
                                            tag["created_at"],
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        tag["color"].upper(),
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                        color=ft.Colors.GREY_600,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                    border_radius=ft.border_radius.all(4),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=16,
                ),
                padding=20,
            ),
            elevation=2,
        )

        if props.selected:
            card.elevation = 6
            card.shadow_color = ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY)
        return card

    def set_props(self, props: TagCardProps) -> None:
        """Propsを反映し直し、必要時のみ再構築する。"""
        self._props = props
        try:
            self.content = self._build(props)
            self.update()
        except Exception as exc:
            logger.warning(f"TagCard.set_props skipped: {exc}")


def create_tag_card(
    tag: dict[str, str],
    on_edit: Callable[[ft.ControlEvent, dict[str, str]], None],
    on_delete: Callable[[ft.ControlEvent, dict[str, str]], None],
) -> ft.Control:
    """後方互換API: クラス版を返す。"""
    props = TagCardProps(tag=tag, selected=False, on_edit=on_edit, on_delete=on_delete, on_select=lambda *_: None)
    return TagCard(props)
