# model/task.py
# SQLModelとSQLiteを使ったタスク管理モデル
from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


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


def validate_task_id(task_id: int | None) -> int:
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
