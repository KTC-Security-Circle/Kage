"""空の状態コンポーネント (Props駆動)。

タグが存在しない場合のプレースホルダー。`set_props()` に対応。
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
class EmptyTagsStateProps:
    """空状態のProps。"""

    on_create: Callable[[ft.ControlEvent], None]


class EmptyTagsState(ft.Container):
    """空状態のUI。"""

    def __init__(self, props: EmptyTagsStateProps) -> None:
        super().__init__()
        self._props = props
        self.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.LABEL_OUTLINE, size=64, color=get_outline_color()),
                ft.Text(
                    "タグがありません",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=get_text_secondary_color(),
                ),
                ft.Text(
                    "新規タグを作成してタスクを分類しましょう",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=get_text_secondary_color(),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.ElevatedButton(
                    text="最初のタグを作成",
                    icon=ft.Icons.ADD,
                    on_click=props.on_create,
                    bgcolor=get_primary_color(),
                    color=get_on_primary_color(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        )
        self.alignment = ft.alignment.center
        self.expand = True

    def set_props(self, props: EmptyTagsStateProps) -> None:
        self._props = props
        try:
            # ボタンのハンドラのみ差し替え
            column = self.content
            if column and hasattr(column, "controls"):
                # 型チェッカー回避のためインデックスアクセス時に ignore
                btn = column.controls[-1]  # type: ignore[index]
                btn.on_click = props.on_create
            self.update()
        except (AttributeError, IndexError) as exc:
            logger.warning(f"EmptyTagsState.set_props skipped: {exc}")


def create_empty_state(on_create: Callable[[ft.ControlEvent], None]) -> ft.Control:
    """後方互換API: クラス版を返す。"""
    return EmptyTagsState(EmptyTagsStateProps(on_create=on_create))
