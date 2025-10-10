"""新しいTaskモデルの定義"""

import uuid
from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from models.memo import Memo
from models.project import Project
from models.tag import Tag
from models.task_tag import TaskTagLink


class TaskStatus(Enum):
    """タスクのステータス（GTDシステムに基づく）

    Attributes:
        INBOX: 新規タスク。未処理の状態。
        TODO: これから取り組むべきタスク。
        TODAYS: 今日中に完了させるべきタスク。
        PROGRESS: 現在進行中のタスク。
        WAITING: 他のタスクの完了を待っているタスク。
        COMPLETED: 完了したタスク。
        CANCELED: キャンセルされたタスク。
        OVERDUE: 期限が過ぎたタスク。
    """

    TODO = "todo"
    TODAYS = "todays"
    PROGRESS = "progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELED = "canceled"
    OVERDUE = "overdue"


class TaskBase(SQLModel):
    """タスクの基本モデル

    Attributes:
        id: タスクを一意に識別するID。
        title: タスクのタイトル。
        description: タスクの詳細な説明。
        status: タスクの状態。
        due_date: タスクの期限日。
        completed_at: タスクの完了日時。
        project_id: このタスクが属するプロジェクトのID。
        memo_id: このタスクの生成元となったメモのID。
        is_recurring: 繰り返しタスクかどうかを示すフラグ。
        recurrence_rule: 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。
        created_at: タスクの作成日時。
        updated_at: タスクの最終更新日時。
        project: このタスクが属するプロジェクトのオブジェクト。
        memo: このタスクの生成元となったメモのオブジェクト。
        tags: このタスクに付けられたタグのリスト。
    """

    title: str = Field(index=True)
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    due_date: date | None = Field(default=None, index=True)
    completed_at: datetime | None = None
    project_id: int | None = Field(default=None, foreign_key="projects.id", nullable=True, index=True)
    memo_id: int | None = Field(default=None, foreign_key="memos.id", nullable=True)
    is_recurring: bool = Field(default=False)
    recurrence_rule: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=False,
    )

    project: Project | None = Relationship(back_populates="tasks")
    memo: Memo | None = Relationship(back_populates="tasks")
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTagLink)


class Task(TaskBase, table=True):
    """新しいタスクモデル

    タスクの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID | None): タスクのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細な説明。
        status (TaskStatus): タスクの状態。デフォルトはTODO。
        due_date (date | None): タスクの期限日。設定されていない場合はNone。
        completed_at (datetime | None): タスクの完了日時。設定されていない場合はNone。
        project_id (int | None): このタスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        memo_id (int | None): このタスクの生成元となったメモのID。メモから生成されていないタスクの場合はNone。
        is_recurring (bool): 繰り返しタスクかどうかを示すフラグ。デフォルトはFalse。
        recurrence_rule (str | None): 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。
                                        設定されていない場合はNone。
        created_at (datetime): タスクの作成日時。デフォルトは現在のUTC日時。
        updated_at (datetime): タスクの最終更新日時。デフォルトは現在のUTC日時で、更新時に自動的に更新されます。
        project (Project | None): このタスクが属するプロジェクトのオブジェクト。
                                    プロジェクトに属さないタスクの場合はNone。
        memo (Memo | None): このタスクの生成元となったメモのオブジェクト。メモから生成されていないタスクの場合はNone。
        tags (list[Tag]): このタスクに付けられたタグのリスト。
    """

    __tablename__ = "tasks"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class TaskCreate(TaskBase):
    """新しいタスク作成用モデル

    タスクを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str | None): タスクの詳細な説明。
        status (TaskStatus): タスクの状態。デフォルトはTODO。
        due_date (date | None): タスクの期限日。設定されていない場合はNone。
        completed_at (datetime | None): タスクの完了日時。設定されていない場合はNone。
        project_id (int | None): このタスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        memo_id (int | None): このタスクの生成元となったメモのID。メモから生成されていないタスクの場合はNone。
        is_recurring (bool): 繰り返しタスクかどうかを示すフラグ。デフォルトはFalse。
        recurrence_rule (str | None): 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。
                                        設定されていない場合はNone。
    """


class TaskRead(TaskBase):
    """新しいタスク読み取り用モデル

    タスクの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): タスクのID。
        title (str): タスクのタイトル。インデックスが設定されており、検索に使用されます。
        description (str): タスクの詳細な説明。
        status (TaskStatus): タスクの状態。デフォルトはTODO。
        due_date (date | None): タスクの期限日。設定されていない場合はNone。
        completed_at (datetime | None): タスクの完了日時。設定されていない場合はNone。
        project_id (int | None): このタスクが属するプロジェクトのID。プロジェクトに属さないタスクの場合はNone。
        memo_id (int | None): このタスクの生成元となったメモのID。メモから生成されていないタスクの場合はNone。
        is_recurring (bool): 繰り返しタスクかどうかを示すフラグ。デフォルトはFalse。
        recurrence_rule (str | None): 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。
                                        設定されていない場合はNone。
        created_at (datetime): タスクの作成日時。
        updated_at (datetime): タスクの最終更新日時。
        project (Project | None): このタスクが属するプロジェクトのオブジェクト。
                                    プロジェクトに属さないタスクの場合はNone。
        memo (Memo | None): このタスクの生成元となったメモのオブジェクト。メモから生成されていないタスクの場合はNone。
        tags (list[Tag]): このタスクに付けられたタグのリスト。
    """

    id: uuid.UUID


class TaskUpdate(SQLModel):
    """タスク更新用モデル

    タスクの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str | None): タスクのタイトル。Noneの場合は更新しない。
        description (str | None): タスクの詳細説明。Noneの場合は更新しない。
        status (TaskStatus | None): タスクのステータス。Noneの場合は更新しない。
        due_date (date | None): タスクの締め切り日。Noneの場合は更新しない。
        completed_at (datetime | None): タスクの完了日時。Noneの場合は更新しない。
        project_id (uuid.UUID | None): タスクが属するプロジェクトのID。Noneの場合は更新しない。
        memo_id (uuid.UUID | None): タスクの生成元となったメモのID。Noneの場合は更新しない。
        is_recurring (bool | None): 繰り返しタスクかどうかを示すフラグ。Noneの場合は更新しない。
        recurrence_rule (str | None): 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。Noneの場合は更新しない。
    """

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    project_id: uuid.UUID | None = None
    memo_id: uuid.UUID | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None
