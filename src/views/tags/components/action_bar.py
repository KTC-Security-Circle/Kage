"""アクションバーコンポーネント (Props駆動)。

新規作成、検索、更新の最小セットを提供。`ft.Container` を継承し、
`set_props()` による差分更新APIを備える。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.theme import get_primary_color

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TagsActionBarProps:
    """アクションバーに必要な表示・イベント情報。"""

    search_placeholder: str
    on_create: Callable[[ft.ControlEvent], None]
    on_search: Callable[[ft.ControlEvent], None]
    on_refresh: Callable[[ft.ControlEvent], None]


class TagsActionBar(ft.Container):
    """Props駆動のアクションバー。"""

    def __init__(self, props: TagsActionBarProps) -> None:
        import flet as ft

        super().__init__()
        self._props = props
        self._search = ft.TextField(
            hint_text=props.search_placeholder,
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            on_change=props.on_search,
        )
        self.content = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="新規タグ",
                    icon=ft.Icons.ADD,
                    on_click=props.on_create,
                    bgcolor=get_primary_color(),
                    color=ft.Colors.WHITE,
                ),
                ft.Container(expand=True),
                self._search,
                ft.IconButton(icon=ft.Icons.REFRESH, tooltip="更新", on_click=props.on_refresh),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def set_props(self, props: TagsActionBarProps) -> None:
        """Props差し替えで差分更新する。"""
        self._props = props
        try:
            self._search.hint_text = props.search_placeholder
            self._search.on_change = props.on_search
            # ボタンのハンドラ更新
            row = self.content  # type: ignore[assignment]
            if row and hasattr(row, "controls"):
                # 左端ボタンと右端更新ボタンを更新
                left_btn, _, _search, refresh_btn = row.controls  # type: ignore[misc]
                left_btn.on_click = props.on_create
                refresh_btn.on_click = props.on_refresh
            self.update()
        except Exception as exc:
            # まだページに未追加の可能性があるため握りつぶさず記録のみ
            logger.warning(f"TagsActionBar.set_props update skipped: {exc}")


def create_action_bar(
    on_create: Callable[[ft.ControlEvent], None],
    on_search: Callable[[ft.ControlEvent], None],
    _on_color_filter: Callable[[ft.ControlEvent], None],
    on_refresh: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """従来ファクトリの後方互換API。クラス版を返す。"""
    props = TagsActionBarProps(
        search_placeholder="タグを検索…",
        on_create=on_create,
        on_search=on_search,
        on_refresh=on_refresh,
    )
    return TagsActionBar(props)
