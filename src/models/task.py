# model/task.py
# SQLModelとSQLiteを使ったタスク管理モデル
from __future__ import annotations

from sqlmodel import Field, Session, SQLModel, select

from config import engine


class Task(SQLModel, table=True):
    """タスクモデル

    Args:
        id (int): タスクID
        title (str): タスクタイトル
        description (str): タスク説明
        is_done (bool): タスク完了フラグ
    """

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    is_done: bool = False


def create_task(title: str, description: str | None = None) -> Task:
    """新しいタスクを作成しDBに保存"""
    if description is None:
        description = ""
    task = Task(title=title, description=description)
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
    return task


def get_tasks() -> list[Task]:
    """全タスクを取得"""
    with Session(engine) as session:
        # 明示的にlist()でリストに変換
        return list(session.exec(select(Task)).all())


def get_task(task_id: int) -> Task | None:
    """IDでタスクを取得"""
    with Session(engine) as session:
        return session.get(Task, task_id)


def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    is_done: bool | None = None,
) -> Task | None:
    """タスクを更新"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return None
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if is_done is not None:
            task.is_done = is_done
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def delete_task(task_id: int) -> bool:
    """タスクを削除"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return False
        session.delete(task)
        session.commit()
        return True
