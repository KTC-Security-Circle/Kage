from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

import flet as ft

if TYPE_CHECKING:
    from models.task import Task


@dataclass
class TaskCardCallbacks:
    on_title_change: Callable[[Any], None] | None = None
    on_desc_change: Callable[[Any], None] | None = None
    on_toggle_done: Callable[[Any], None] | None = None
    on_edit: Callable[[Any], None] | None = None
    on_edit_save: Callable[[Any], None] | None = None
    on_edit_cancel: Callable[[Any], None] | None = None
    on_delete: Callable[[Any], None] | None = None


def task_card(
    task: Task,
    editing_values: dict[str, str] | None = None,  # 編集中の値
    callbacks: TaskCardCallbacks | None = None,  # コールバック群
    *,
    is_editing: bool = False,  # 編集モードかどうか（キーワード専用引数）
) -> ft.Card:
    # デフォルト値を設定
    if editing_values is None:
        editing_values = {}
    if callbacks is None:
        callbacks = TaskCardCallbacks()
    # タスク1件分の表示・編集UI(インライン編集対応)
    if is_editing:
        title_field = ft.TextField(
            value=editing_values.get("title", task.title),
            width=200,
            autofocus=True,
            on_change=callbacks.on_title_change,
        )
        desc_field = ft.TextField(
            value=editing_values.get("description", task.description),
            width=200,
            on_change=callbacks.on_desc_change,
        )
        content = ft.Row(
            [
                ft.Checkbox(
                    value=task.is_done,
                    on_change=callbacks.on_toggle_done,
                    tooltip="完了/未完了",
                ),
                ft.Column([title_field, desc_field], expand=True),
                ft.IconButton(
                    icon=ft.Icons.CHECK,
                    tooltip="保存",
                    on_click=callbacks.on_edit_save,
                    icon_color=ft.Colors.GREEN,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="キャンセル",
                    on_click=callbacks.on_edit_cancel,
                    icon_color=ft.Colors.RED,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="削除",
                    on_click=callbacks.on_delete,
                    icon_color=ft.Colors.RED,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    else:
        content = ft.Row(
            [
                ft.Checkbox(
                    value=task.is_done,
                    on_change=callbacks.on_toggle_done,
                    tooltip="完了/未完了",
                ),
                ft.Column(
                    [
                        ft.Text(task.title, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(task.description, size=14, color=ft.Colors.GREY),
                    ],
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="編集",
                    on_click=callbacks.on_edit,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="削除",
                    on_click=callbacks.on_delete,
                    icon_color=ft.Colors.RED,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    return ft.Card(
        content=ft.Container(
            content=content,
            padding=10,
        ),
        elevation=2,
        margin=ft.margin.only(bottom=8),
    )
