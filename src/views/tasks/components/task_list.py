"""Task List component.

ft.UserControl でタスク一覧を表示し、アイテムクリックをコールバックで通知する。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.tasks.components.task_card import TaskCardData


@dataclass(frozen=True)
class TaskListProps:
    """初期プロパティ。

    Attributes:
        on_item_click: アイテムクリック時に呼ばれる (TaskCardVM を引数にとる)
    """

    on_item_click: Callable[[str], None] | None = None


class TaskList:
    """タスクの一覧表示コンポーネント (非継承)。"""

    def __init__(self, props: TaskListProps) -> None:
        self._props = props
        self._items: list[ft.Control] = []
        self._list = ft.ListView(expand=True, spacing=8, padding=ft.padding.only(top=8))

    @property
    def control(self) -> ft.Control:
        return self._list

    # Public API
    def set_items(self, items: list[object]) -> None:
        """一覧を差し替えて再描画する。

        Args:
            items: TaskCardVM のリスト
        """
        # 後方互換: TaskCardVM/辞書を渡された場合は ListTile で表示
        self._list.controls = []
        for vm in items:
            # vm は dataclass TaskCardVM or dict を想定
            title = getattr(vm, "title", None) or (vm.get("title") if isinstance(vm, dict) else "") or ""
            description = (
                getattr(vm, "description", None) or (vm.get("description") if isinstance(vm, dict) else "") or ""
            )
            subtitle = (
                description
                or getattr(vm, "subtitle", None)
                or (vm.get("subtitle") if isinstance(vm, dict) else "")
                or ""
            )
            task_id = getattr(vm, "id", None) or (vm.get("id") if isinstance(vm, dict) else "") or ""

            def _handle_click(_e: ft.ControlEvent, tid: str = str(task_id)) -> None:
                if self._props.on_item_click:
                    self._props.on_item_click(tid)

            self._list.controls.append(
                ft.ListTile(
                    title=ft.Text(str(title)),
                    subtitle=ft.Text(str(subtitle)),
                    data=str(task_id),
                    on_click=_handle_click if self._props.on_item_click else None,
                )
            )
        # 変更を即時反映
        with contextlib.suppress(AssertionError):
            self._list.update()
        # TODO: 大量件数対応で差分更新 (DOM diff) や仮想スクロールを導入。現在は全件再描画。
        # TODO: 複数選択 (shift/ctrl) やドラッグ&ドロップ並び替えにも対応できる設計へ拡張。

    # ListView は親にぶら下がっているため、親側で update する
    def set_cards(self, cards: list[TaskCardData]) -> None:
        """TaskCardData リストを受け取り、TaskCard を描画する正式経路。"""
        from views.tasks.components.task_card import TaskCard  # 局所 import で循環回避

        self._items = []
        self._list.controls = []
        for data in cards:
            card = TaskCard(data)
            self._list.controls.append(card)
        # 変更を即時反映
        with contextlib.suppress(AssertionError):
            self._list.update()
        # TODO: 選択状態の差分適用 (前後の選択ID比較) で再描画コストを削減。
        # TODO: カード幅/レイアウトをレスポンシブに調整する仕組み (列数変更) が必要なら Grid 化を検討。
