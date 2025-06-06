# model/task.py
# SQLModelとSQLiteを使ったタスク管理モデル
from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Session, SQLModel, desc, select

from config import engine


class Task(SQLModel, table=True):
    """タスクモデル

    タスク情報を表すモデルクラス。SQLModelを使用してデータベースと連携します。
    """

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed: bool = Field(default=False)


def check_task_id(task_id: int | None) -> int:
    """タスクIDのチェック

    task.idがPylanceの警告を回避するための関数

    Args:
        task_id: チェックするタスクのID

    Returns:
        int: 有効なタスクID

    Raises:
        ValueError: タスクIDがNoneまたは0の場合
    """
    if task_id is None or task_id <= 0:
        e_msg = "タスクIDが指定されていません、または無効です"
        raise ValueError(e_msg)
    return task_id


def create_task(title: str, description: str | None = None) -> Task:
    """新しいタスクを作成する

    Args:
        title: タスクのタイトル
        description: タスクの説明（オプション）

    Returns:
        Task: 作成されたタスクオブジェクト

    Raises:
        ValueError: タイトルが空の場合
    """
    if not title:
        e_msg = "タスクのタイトルは必須です"
        raise ValueError(e_msg)

    # 説明が空でないことを確認
    if description is None:
        description = ""

    # 新しいタスクインスタンスを作成
    task = Task(title=title, description=description)

    # データベースに保存
    with Session(engine) as session:
        session.add(task)
        session.commit()
        # 新しく割り当てられたIDを取得するために再読み込み
        session.refresh(task)

    return task


def get_all_tasks() -> list[Task]:
    """すべてのタスクを取得する

    Returns:
        list[Task]: タスクのリスト
    """
    with Session(engine) as session:
        statement = select(Task).order_by(desc(Task.created_at))
        return list(session.exec(statement).all())


def get_task(task_id: int) -> Task | None:
    """指定されたIDのタスクを取得する

    Args:
        task_id: 取得するタスクのID

    Returns:
        Task | None: 見つかったタスク、存在しない場合はNone
    """
    with Session(engine) as session:
        return session.get(Task, task_id)


def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    is_done: bool | None = None,
) -> Task | None:
    """指定されたIDのタスクを更新する

    Args:
        task_id: 更新するタスクのID
        title: 新しいタイトル（指定がなければ変更なし）
        description: 新しい説明（指定がなければ変更なし）
        is_done: 新しい完了状態（指定がなければ変更なし）

    Returns:
        Task | None: 更新されたタスク、存在しない場合はNone
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if not task:
            return None

        # 指定された値がある場合のみ更新
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if is_done is not None:
            task.completed = is_done

        # 更新日時を現在時刻に更新
        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task


def delete_task(task_id: int) -> bool:
    """指定されたIDのタスクを削除する

    Args:
        task_id: 削除するタスクのID

    Returns:
        bool: 削除が成功したかどうか
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if not task:
            return False

        session.delete(task)
        session.commit()

        return True


def update_task_status(task_id: int, *, completed: bool) -> Task | None:
    """タスクの完了状態のみを更新する

    Args:
        task_id: 更新するタスクのID
        completed: 新しい完了状態

    Returns:
        Task | None: 更新されたタスク、存在しない場合はNone
    """
    return update_task(task_id, is_done=completed)


def get_completed_tasks() -> list[Task]:
    """完了済みのタスクのみを取得する

    Returns:
        list[Task]: 完了済みタスクのリスト
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.completed is True).order_by(desc(Task.updated_at))
        return list(session.exec(statement).all())


def get_pending_tasks() -> list[Task]:
    """未完了のタスクのみを取得する

    Returns:
        list[Task]: 未完了タスクのリスト
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.completed is False).order_by(desc(Task.created_at))
        return list(session.exec(statement).all())
