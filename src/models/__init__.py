from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class MemoStatus(str, Enum):
    """メモの状態を表す列挙型

    Attributes:
        INBOX: タスクになる前の整理をされていないメモ
        ACTIVE: Inboxのメモからタスクが生成された際にこのステータスになる
        IDEA: タスクにもプロジェクトにもならなかったメモ
        ARCHIVE: タスクがCompletedかCanceledになった際にそのタスクに紐づいたメモが行き着く先
                 メモに対して複数タスクが紐づいている場合は紐づいているタスクすべてが先ほどのステータスになっている必要がある
    """

    INBOX = "inbox"
    ACTIVE = "active"
    IDEA = "idea"
    ARCHIVE = "archive"


class AiSuggestionStatus(str, Enum):
    """AI提案の状態を表す列挙型

    Attributes:
        NOT_REQUESTED: AI提案がまだリクエストされていない状態
        PENDING: AI提案がリクエストされ、処理中の状態
        AVAILABLE: AI提案が利用可能な状態
        REVIEWED: AI提案がユーザーによって確認された状態
        FAILED: AI提案のリクエストが失敗した状態
    """

    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    AVAILABLE = "available"
    REVIEWED = "reviewed"
    FAILED = "failed"


class ProjectStatus(str, Enum):
    """プロジェクトのステータス

    Attributes:
        ACTIVE: プロジェクトが進行中であることを示します。
        ON_HOLD: プロジェクトが一時停止中であることを示します。
        COMPLETED: プロジェクトが完了したことを示します。
        CANCELLED: プロジェクトがキャンセルされたことを示します。
    """

    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
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


class MemoTagLinkBase(SQLModel):
    """メモとタグの中間テーブルモデル。

    Attributes:
        memo_id: 関連するメモのID。
        tag_id: 関連するタグのID。
    """


class MemoTagLink(MemoTagLinkBase, table=True):
    """メモとタグの関連モデル

    メモとタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        memo_id (uuid.UUID): メモのID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """

    __tablename__ = "memo_tag"  # pyright: ignore[reportAssignmentType]

    memo_id: uuid.UUID | None = Field(default=None, foreign_key="memos.id", primary_key=True)
    tag_id: uuid.UUID | None = Field(default=None, foreign_key="tags.id", primary_key=True)


class MemoTagLinkCreate(MemoTagLinkBase):
    """メモとタグの関連作成用モデル

    メモとタグの関連を新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        memo_id (uuid.UUID): メモのID。
        tag_id (uuid.UUID): タグのID。
    """


class MemoTagLinkRead(MemoTagLinkBase):
    """メモとタグの関連読み取り用モデル

    メモとタグの関連情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        memo_id (uuid.UUID): メモのID。
        tag_id (uuid.UUID): タグのID。
    """

    memo_id: uuid.UUID
    tag_id: uuid.UUID


class TaskTagLinkBase(SQLModel):
    """タスクとタグの中間テーブルモデル。

    Attributes:
        task_id: 関連するタスクのID。
        tag_id: 関連するタグのID。
    """


class TaskTagLink(TaskTagLinkBase, table=True):
    """タスクとタグの関連モデル

    タスクとタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """

    __tablename__ = "task_tag"  # pyright: ignore[reportAssignmentType]

    task_id: uuid.UUID | None = Field(default=None, foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID | None = Field(default=None, foreign_key="tags.id", primary_key=True)


class TaskTagLinkCreate(TaskTagLinkBase):
    """タスクとタグの関連作成用モデル

    タスクとタグの関連を新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。
        tag_id (uuid.UUID): タグのID。
    """


class TaskTagLinkRead(TaskTagLinkBase):
    """タスクとタグの関連読み取り用モデル

    タスクとタグの関連情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。
        tag_id (uuid.UUID): タグのID。
    """

    task_id: uuid.UUID
    tag_id: uuid.UUID


class MemoBase(SQLModel):
    """メモの基本モデル

    Attributes:
        title (str): メモのタイトル。インデックスが設定されており
                     検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNotRequested。
        ai_analysis_log (str | None): AI分析のログ情報。デフォルトはNone。
        created_at (datetime): メモの作成日時。デフォルトは現在日時。
        updated_at (datetime): メモの最終更新日時。デフォルトは現在日時。
        processed_at (datetime | None): メモが最後に処理された日時。デフォルトはNone。
    """

    title: str = Field(index=True)
    content: str
    status: MemoStatus = Field(default=MemoStatus.INBOX, index=True)
    ai_suggestion_status: AiSuggestionStatus = Field(default=AiSuggestionStatus.NOT_REQUESTED, index=True)
    ai_analysis_log: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    processed_at: datetime | None = Field(default=None, index=True)


class Memo(MemoBase, table=True):
    """すべての情報の入り口となる「気になること」を格納するメモのモデル。

    Attributes:
        id: メモを一意に識別するID。
        title: メモのタイトル。
        content: メモの本文。
        status: メモの状態。
        ai_suggestion_status: AIによるタスク分類提案の状態。
        ai_analysis_log: AIによる分類処理のログ。
        source: メモの入力元。
        created_at: メモの作成日時。
        updated_at: メモの最終更新日時。
        processed_at: ユーザーによる確認日時。
        tasks: このメモから生成されたタスクのリスト。
        tags: このメモに付けられたタグのリスト。
    """

    __tablename__ = "memos"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    tasks: list[Task] = Relationship(back_populates="memo")
    tags: list[Tag] = Relationship(back_populates="memos", link_model=MemoTagLink)


class MemoCreate(MemoBase):
    """メモ作成用モデル

    メモを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): メモのタイトル。インデックスが設定されており、検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNotRequested。
        ai_analysis_log (str | None): AI分析のログ情報。デフォルトはNone。
        created_at (datetime): メモの作成日時。デフォルトは現在日時。
        updated_at (datetime): メモの最終更新日時。デフォルトは現在日時。
        processed_at (datetime | None): メモが最後に処理された日時。デフォルトはNone。
    """


class MemoRead(MemoBase):
    """メモ読み取り用モデル

    メモの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): メモのID。
        title (str): メモのタイトル。インデックスが設定されており、検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNotRequested。
        ai_analysis_log (str | None): AI分析のログ情報。デフォルトはNone。
        created_at (datetime): メモの作成日時。デフォルトは現在日時。
        updated_at (datetime): メモの最終更新日時。デフォルトは現在日時。
        processed_at (datetime | None): メモが最後に処理された日時。デフォルトはNone。
    """

    id: uuid.UUID


class MemoUpdate(SQLModel):
    """メモ更新用モデル

    メモの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str | None): メモのタイトル。Noneの場合は更新しない。
        content (str | None): メモの内容。Noneの場合は更新しない。
        status (MemoStatus | None): メモの状態。Noneの場合は更新しない。
        ai_suggestion_status (AiSuggestionStatus | None): AI提案の状態。Noneの場合は更新しない。
        ai_analysis_log (dict | None): AI分析のログ情報。Noneの場合は更新しない。
        processed_at (datetime | None): メモが最後に処理された日時。Noneの場合は更新しない。
    """

    title: str | None = None
    content: str | None = None
    status: MemoStatus | None = None
    ai_suggestion_status: AiSuggestionStatus | None = None
    ai_analysis_log: dict | None = None
    processed_at: datetime | None = None


class ProjectBase(SQLModel):
    """複数のタスクを束ねる「成果」や「結果」を管理するプロジェクトのモデル。

    Attributes:
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
        created_at: プロジェクトの作成日時。
        updated_at: プロジェクトの最終更新日時。
        tasks: このプロジェクトに属するタスクのリスト。
    """

    title: str = Field(index=True)
    description: str | None = None
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    due_date: date | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=False,
    )


class Project(ProjectBase, table=True):
    """プロジェクトモデル

    プロジェクトの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: プロジェクトを一意に識別するID。
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
        created_at: プロジェクトの作成日時。
        updated_at: プロジェクトの最終更新日時。
        tasks: このプロジェクトに属するタスクのリスト。
    """

    __tablename__ = "projects"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    tasks: list[Task] = Relationship(back_populates="project")


class ProjectCreate(ProjectBase):
    """プロジェクト作成用モデル

    プロジェクトを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: プロジェクトを一意に識別するID。
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
        created_at: プロジェクトの作成日時。
        updated_at: プロジェクトの最終更新日時。
        tasks: このプロジェクトに属するタスクのリスト。
    """


class ProjectRead(ProjectBase):
    """プロジェクト読み取り用モデル

    プロジェクトの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: プロジェクトを一意に識別するID。
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
        created_at: プロジェクトの作成日時。
        updated_at: プロジェクトの最終更新日時。
        tasks: このプロジェクトに属するタスクのリスト。
    """

    id: uuid.UUID


class ProjectUpdate(SQLModel):
    """プロジェクト更新用モデル

    プロジェクトの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
    """

    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    due_date: date | None = None


class TagBase(SQLModel):
    """タスクやメモを横断的に分類するタグのモデル。

    Attributes:
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時。
        tasks: このタグが付けられたタスクのリスト。
        memos: このタグが付けられたメモのリスト。
    """

    name: str = Field(unique=True, index=True)
    description: str | None = None
    color: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=False,
    )


class Tag(TagBase, table=True):
    """タグモデル

    タグの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: タグを一意に識別するID。
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時。
        tasks: このタグが付けられたタスクのリスト。
        memos: このタグが付けられたメモのリスト。
    """

    __tablename__ = "tags"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    tasks: list[Task] = Relationship(back_populates="tags", link_model=TaskTagLink)
    memos: list[Memo] = Relationship(back_populates="tags", link_model=MemoTagLink)


class TagCreate(TagBase):
    """タグ作成用モデル

    タグを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: タグを一意に識別するID。
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時。
        tasks: このタグが付けられたタスクのリスト。
        memos: このタグが付けられたメモのリスト。
    """


class TagRead(TagBase):
    """タグ読み取り用モデル

    タグの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: タグを一意に識別するID。
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時。
        tasks: このタグが付けられたタスクのリスト。
        memos: このタグが付けられたメモのリスト。
    """

    id: uuid.UUID


class TagUpdate(SQLModel):
    """タグ更新用モデル

    タグの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
    """

    name: str | None = None
    description: str | None = None
    color: str | None = None


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
    project_id: uuid.UUID | None = Field(default=None, foreign_key="projects.id", nullable=True, index=True)
    memo_id: uuid.UUID | None = Field(default=None, foreign_key="memos.id", nullable=True)
    is_recurring: bool = Field(default=False)
    recurrence_rule: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=False,
    )


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

    project: Project | None = Relationship(back_populates="tasks")
    memo: Memo | None = Relationship(back_populates="tasks")
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTagLink)


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
