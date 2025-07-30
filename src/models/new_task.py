"""新しいTaskモデルの定義"""

import uuid
from datetime import date
from enum import Enum

from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    """タスクのステータス（GTDシステムに基づく）"""

    INBOX = "inbox"
    NEXT_ACTION = "next_action"
    WAITING_FOR = "waiting_for"
    SOMEDAY_MAYBE = "someday_maybe"
    DELEGATED = "delegated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(SQLModel):
    """タスクの基本モデル

    タスクの基本情報を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        user_id (uuid.UUID): タスクを所有するユーザーのID。
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        parent_id (uuid.UUID | None): 親タスクのID。サブタスクの場合に使用。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        status (TaskStatus): タスクのステータス。デフォルトはINBOX。
        due_date (date | None): タスクの締め切り日。設定されていない場合はNone。
    """

    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    project_id: uuid.UUID | None = Field(default=None, foreign_key="project.id", index=True)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="task.id", index=True)
    title: str = Field(index=True)
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.INBOX, index=True)
    due_date: date | None = Field(default=None, index=True)


class Task(TaskBase, table=True):
    """新しいタスクモデル

    タスクの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID | None): タスクのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        user_id (uuid.UUID): タスクを所有するユーザーのID。
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        parent_id (uuid.UUID | None): 親タスクのID。サブタスクの場合に使用。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        status (TaskStatus): タスクのステータス。デフォルトはINBOX。
        due_date (date | None): タスクの締め切り日。設定されていない場合はNone。
    """

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class TaskCreate(TaskBase):
    """新しいタスク作成用モデル

    タスクを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        user_id (uuid.UUID): タスクを所有するユーザーのID。
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        parent_id (uuid.UUID | None): 親タスクのID。サブタスクの場合に使用。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        status (TaskStatus): タスクのステータス。デフォルトはINBOX。
        due_date (date | None): タスクの締め切り日。設定されていない場合はNone。
    """


class TaskRead(TaskBase):
    """新しいタスク読み取り用モデル

    タスクの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): タスクのID。
        user_id (uuid.UUID): タスクを所有するユーザーのID。
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        parent_id (uuid.UUID | None): 親タスクのID。サブタスクの場合に使用。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細説明。デフォルトは空文字列。
        status (TaskStatus): タスクのステータス。デフォルトはINBOX。
        due_date (date | None): タスクの締め切り日。設定されていない場合はNone。
    """

    id: uuid.UUID


class TaskUpdate(SQLModel):
    """新しいタスク更新用モデル

    タスクの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。Noneの場合は更新しない。
        parent_id (uuid.UUID | None): 親タスクのID。Noneの場合は更新しない。
        title (str | None): タスクのタイトル。Noneの場合は更新しない。
        description (str | None): タスクの詳細説明。Noneの場合は更新しない。
        status (TaskStatus | None): タスクのステータス。Noneの場合は更新しない。
        due_date (date | None): タスクの締め切り日。Noneの場合は更新しない。
    """

    project_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
