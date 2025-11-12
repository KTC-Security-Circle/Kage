"""Task Detail Panel component.

選択中タスクの詳細表示とステータス変更 UI を提供する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.tasks.components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.tasks.presenter import TaskCardVM, TaskDetailVM


@dataclass(frozen=True)
class DetailPanelProps:
    """初期プロパティ。"""

    on_status_change: Callable[[str, str], None]


class TaskDetailPanel:
    """右ペインの詳細表示コンポーネント (非継承)。"""

    def __init__(self, props: DetailPanelProps) -> None:
        self._props = props
        # TaskDetailVM 優先。後方互換で TaskCardVM も許容
        self._vm: TaskDetailVM | TaskCardVM | None = None
        self._status_dd: ft.Dropdown | None = None
        self._root: ft.Control | None = None

    @property
    def control(self) -> ft.Control:
        return self._root or self._placeholder()

    def set_item(self, vm: TaskDetailVM | TaskCardVM | None) -> None:
        """詳細対象を切り替えて再描画。"""
        self._vm = vm
        if not vm:
            self._root = self._placeholder()
            # 親側で update される想定
            return

        # Flet Option は key/text を指定可能。value は key が使われる。
        status_options = [ft.dropdown.Option(key=s, text=TASK_STATUS_LABELS.get(s, s)) for s in STATUS_ORDER]
        self._status_dd = ft.Dropdown(
            label="ステータス",
            value=vm.status or "",
            options=status_options,
            on_change=lambda e: self._handle_status_change(str(e.control.value or "")),  # type: ignore[arg-type]
            width=220,
        )

        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("タスク詳細", weight=ft.FontWeight.BOLD, size=18),
                        ft.Text(vm.title, size=16),
                        ft.Text(getattr(vm, "description", "") or "説明なし", color=ft.colors.GREY_700),
                        ft.Divider(),
                        ft.Row([ft.Text("ステータス:"), self._status_dd]),
                        ft.Row([ft.Text("更新日:"), ft.Text(getattr(vm, "subtitle", ""))]),
                        ft.Row([ft.Text("優先度:"), ft.Text(str(getattr(vm, "priority", "")) or "-")]),
                    ],
                    spacing=8,
                ),
                padding=16,
            )
        )
        self._root = card

    # Internal
    def _placeholder(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [ft.Text("タスクを選択して詳細を表示", color=ft.colors.GREY_600)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
        )

    def _handle_status_change(self, new_status: str) -> None:
        if not self._vm:
            return
        self._props.on_status_change(str(self._vm.id), new_status)
