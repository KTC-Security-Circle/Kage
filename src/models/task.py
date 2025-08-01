"""Taskモデルの定義"""

from datetime import datetime

from sqlmodel import Field, SQLModel
from typing_extensions import deprecated


class OldTaskBase(SQLModel):
    """タスクの基本モデル

    タスクの基本情報を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        created_at (datetime): タスクの作成日時。デフォルトは現在の日時。
        updated_at (datetime): タスクの更新日時。デフォルトは現在の日時。
        completed (bool): タスクの完了状態。デフォルトはFalse（未完了）。
    """

    title: str = Field(index=True)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed: bool = Field(default=False)


class OldTask(OldTaskBase, table=True):
    """タスクモデル

    タスクの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (int | None): タスクのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        created_at (datetime): タスクの作成日時。デフォルトは現在の日時。
        updated_at (datetime): タスクの更新日時。デフォルトは現在の日時。
        completed (bool): タスクの完了状態。デフォルトはFalse（未完了）。
    """

    id: int | None = Field(default=None, primary_key=True)


class OldTaskCreate(OldTaskBase):
    """タスク作成用モデル

    タスクを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        created_at (datetime): タスクの作成日時。デフォルトは現在の日時。
        updated_at (datetime): タスクの更新日時。デフォルトは現在の日時。
        completed (bool): タスクの完了状態。デフォルトはFalse（未完了）。
    """


class OldTaskRead(OldTaskBase):
    """タスク読み取り用モデル

    タスクの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (int): タスクのID。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        created_at (datetime): タスクの作成日時。デフォルトは現在の日時。
        updated_at (datetime): タスクの更新日時。デフォルトは現在の日時。
        completed (bool): タスクの完了状態。デフォルトはFalse（未完了）。
    """

    id: int


class OldTaskUpdate(SQLModel):
    """タスク更新用モデル

    タスクの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:no
        title (str | None): タスクのタイトル。Noneの場合は更新しない。
        description (str | None): タスクの詳細説明。Noneの場合は更新しない。
        completed (bool | None): タスクの完了状態。Noneの場合は更新しない。
    """

    title: str | None = None
    description: str | None = None
    completed: bool | None = None


@deprecated(
    "validate_task_idは非推奨です。TaskRead.idを直接使用してください。",
)
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
