# controller/task_controller.py
from __future__ import annotations

from models.task import Task, create_task, delete_task, get_task, get_tasks, update_task


# コントローラー層でCRUDをラップ(UIから呼びやすくするため)
def add_task(title: str, description: str = "") -> Task:
    return create_task(title, description)


def fetch_tasks() -> list[Task]:
    return get_tasks()


def fetch_task(task_id: int) -> Task | None:
    return get_task(task_id)


def edit_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    is_done: bool | None = None,
) -> Task | None:
    return update_task(task_id, title, description, is_done)


def remove_task(task_id: int) -> bool:
    return delete_task(task_id)
