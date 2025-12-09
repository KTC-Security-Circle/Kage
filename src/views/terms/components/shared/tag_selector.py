"""タグ選択UIヘルパー

CreateTermDialogとEditTermDialogで共有されるタグ選択ロジック。
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, Protocol

import flet as ft

from views.theme import get_grey_color, get_on_primary_color

if TYPE_CHECKING:
    from collections.abc import Callable

    class _TagSelectorHost(Protocol):
        """TagSelectorMixinを使用するクラスが実装すべきプロトコル"""

        _selected_tag_ids: set[str]
        _tag_dropdown: ft.Dropdown | None
        _selected_tags_container: ft.Row | None
        _props: Any  # all_tags属性を持つPropsオブジェクト

        def _update_selected_tags_display(self) -> None:
            """選択中タグのバッジ表示を更新（Mixin内で実装される）"""
            ...


class TagSelectorMixin:
    """タグ選択UIの共通処理を提供するMixin

    CreateTermDialogとEditTermDialogで使用される、タグ選択ドロップダウンと
    選択済みタグバッジの表示・更新ロジックを集約する。

    使用するクラスは_TagSelectorHostプロトコルを実装する必要がある。
    """

    def _on_tag_select(self: _TagSelectorHost, e: ft.ControlEvent) -> None:
        """タグ選択時のハンドラ

        ドロップダウンで選択されたタグを_selected_tag_idsに追加し、
        バッジ表示を更新する。

        Args:
            e: イベント
        """
        if e.control.value and e.control.value not in self._selected_tag_ids:
            self._selected_tag_ids.add(e.control.value)
            self._update_selected_tags_display()
            if self._tag_dropdown:
                self._tag_dropdown.value = None
                with suppress(AssertionError):
                    self._tag_dropdown.update()

    def _update_selected_tags_display(self: _TagSelectorHost) -> None:
        """選択中タグのバッジ表示を更新

        _selected_tag_idsに基づいて、_selected_tags_container内のバッジUIを再構築する。
        各バッジには削除ボタンが付き、クリックで選択解除できる。
        """
        if not self._selected_tags_container or not self._props.all_tags:
            return

        self._selected_tags_container.controls.clear()

        for tag_name in sorted(self._selected_tag_ids):
            tag = next((t for t in self._props.all_tags if t.name == tag_name), None)
            if tag is None:
                continue

            color = tag.color or get_grey_color(600)

            def make_remove_handler(name: str) -> Callable[[ft.ControlEvent], None]:
                def handler(_: ft.ControlEvent) -> None:
                    self._selected_tag_ids.discard(name)
                    self._update_selected_tags_display()

                return handler

            badge = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(tag_name, size=12, color=get_on_primary_color()),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=14,
                            icon_color=get_on_primary_color(),
                            on_click=make_remove_handler(tag_name),
                            tooltip=f"{tag_name}を削除",
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=color,
                border_radius=12,
                padding=ft.padding.only(left=12, right=4, top=4, bottom=4),
            )
            self._selected_tags_container.controls.append(badge)

        with suppress(AssertionError):
            self._selected_tags_container.update()
