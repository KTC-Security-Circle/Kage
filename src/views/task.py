# view/task.py
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import flet as ft

from controllers.task_controller import edit_task, fetch_tasks, remove_task
from views.components import TaskCardCallbacks, task_card

if TYPE_CHECKING:
    from models.task import Task


def check_task_id(task_id: int | None) -> int:
    """タスクIDの存在確認"""
    if task_id is None:
        msg = "タスクIDが指定されていません"
        raise ValueError(msg)
    return task_id


class TaskListView:
    """タスク一覧・編集・削除・完了切り替えを管理するクラス"""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.editing: dict[int, bool] = {}
        self.edit_values: dict[int, dict[str, str]] = {}
        self.task_list = ft.Column(spacing=0)
        self.refresh()

    def build_task_row(self, task: Task) -> ft.Control:
        """タスク1件分のUIを生成"""
        tid = check_task_id(task.id)
        is_editing = self.editing.get(tid, False)
        values = self.edit_values.get(tid, {"title": task.title, "description": task.description})

        callbacks = TaskCardCallbacks(
            on_title_change=self.on_title_change_factory(tid),
            on_desc_change=self.on_desc_change_factory(tid),
            on_toggle_done=lambda e: self.on_toggle_done(task, e.control.value),
            on_edit=lambda _: self.on_edit(task),
            on_edit_save=lambda _: self.on_edit_save(task),
            on_edit_cancel=lambda _: self.on_edit_cancel(task),
            on_delete=lambda _: self.on_delete(tid),
        )

        return task_card(
            task=task,
            editing_values=values,
            callbacks=callbacks,
            is_editing=is_editing,
        )

    def on_title_change_factory(self, tid: int) -> Callable[[ft.ControlEvent], None]:
        """タスクのタイトル変更時のコールバックを生成"""

        def _on_title_change(e: ft.ControlEvent) -> None:
            self.edit_values.setdefault(tid, {})
            self.edit_values[tid]["title"] = e.control.value

        return _on_title_change

    def on_desc_change_factory(self, tid: int) -> Callable[[ft.ControlEvent], None]:
        """タスクの説明変更時のコールバックを生成"""

        def _on_desc_change(e: ft.ControlEvent) -> None:
            self.edit_values.setdefault(tid, {})
            self.edit_values[tid]["description"] = e.control.value

        return _on_desc_change

    def on_delete(self, task_id: int) -> None:
        """タスク削除時のコールバック"""
        remove_task(task_id)
        self.refresh_and_update()

    def on_toggle_done(self, task: Task, value: bool | None) -> None:
        """タスク完了切り替え時のコールバック"""
        edit_task(check_task_id(task.id), is_done=bool(value))
        self.refresh_and_update()

    def on_edit(self, task: Task) -> None:
        """タスク編集時のコールバック"""
        tid = check_task_id(task.id)
        self.editing[tid] = True
        self.edit_values[tid] = {"title": task.title, "description": task.description}
        self.refresh_and_update()

    def on_edit_save(self, task: Task) -> None:
        """タスク編集保存時のコールバック"""
        tid = check_task_id(task.id)
        values = self.edit_values.get(tid, {"title": task.title, "description": task.description})
        edit_task(tid, title=values["title"], description=values["description"])
        self.editing[tid] = False
        self.refresh()
        self.task_list.update()

    def on_edit_cancel(self, task: Task) -> None:
        """タスク編集キャンセル時のコールバック"""
        self.editing[check_task_id(task.id)] = False
        self.refresh()
        self.task_list.update()

    def refresh(self) -> None:
        """タスクリストを再構築"""
        tasks = fetch_tasks()
        self.task_list.controls.clear()
        if not tasks:
            self.task_list.controls.append(ft.Text("タスクがありません", color=ft.Colors.GREY))
        else:
            for task in tasks:
                self.task_list.controls.append(self.build_task_row(task))


def task_view(page: ft.Page) -> ft.Container:
    """タスク一覧画面のルートコンテナ"""
    task_list_view = TaskListView(page)
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("タスク一覧", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("ホームへ戻る", icon=ft.Icons.HOME, on_click=lambda _: page.go("/")),
                ft.Divider(),
                task_list_view.task_list,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=30,
        alignment=ft.alignment.top_center,
        expand=True,
    )
