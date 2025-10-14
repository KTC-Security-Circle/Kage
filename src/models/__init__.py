"""データベースモデルの定義

このモジュールでは、SQLModelを使用してデータベースモデルを定義しています。
各モデルは、アプリケーション内で使用されるエンティティ（タスク、プロジェクト、メモ、タグなど）を表現しています。

各モデルクラスは、SQLModelの基礎クラスを継承したBaseクラスがあり、そこから派生した各エンティティのモデルクラスが定義されています。

- Baseクラス: SQLModelの基礎クラス。
- データベースモデルクラス: 各エンティティのデータベースモデルを定義するクラス。
- Readクラス: データベースからの読み取り専用のモデル。
- Createクラス: 新規作成用のモデル。
- Updateクラス: 更新用のモデル。


Attributes:
    Base: SQLModelの基礎クラス。

    ## ステータス用列挙型
    TaskStatus: タスクのステータスを表す列挙型。
    ProjectStatus: プロジェクトのステータスを表す列挙型。
    AiSuggestionStatus: AI提案のステータスを表す列挙型。
    MemoStatus: メモのステータスを表す列挙型。

    ## モデルクラス
    Task: タスクモデル。
    TaskCreate: タスク作成用モデル。
    TaskRead: タスク読み取り用モデル。
    TaskUpdate: タスク更新用モデル。
    Project: プロジェクトモデル。
    ProjectCreate: プロジェクト作成用モデル。
    ProjectRead: プロジェクト読み取り用モデル。
    ProjectUpdate: プロジェクト更新用モデル。
    Memo: メモモデル。
    MemoCreate: メモ作成用モデル。
    MemoRead: メモ読み取り用モデル。
    MemoUpdate: メモ更新用モデル。
    Tag: タグモデル。
    TagCreate: タグ作成用モデル。
    TagRead: タグ読み取り用モデル。
    TagUpdate: タグ更新用モデル。
    TaskTagLink: タスクとタグの中間テーブルモデル。
    TaskTagLinkCreate: タスクとタグの関連作成用モデル。
    TaskTagLinkRead: タスクとタグの関連読み取り用モデル。
    MemoTagLink: メモとタグの中間テーブルモデル。
    MemoTagLinkCreate: メモとタグの関連作成用モデル。
    MemoTagLinkRead: メモとタグの関連読み取り用モデル。
"""

# tablename用 ignore
# # 型アサインメントの警告を無効化
# pyright: reportAssignmentType=false
# # 一般的な型の問題の警告を無効化
# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


# ==============================================================================
# ==============================================================================
# Enums (列挙型)
# ==============================================================================
# ==============================================================================
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


# ==============================================================================
# ==============================================================================
# Base Model (基底モデル)
# ==============================================================================
# ==============================================================================


class BaseModel(SQLModel):
    """IDを持つ基本モデル

    Attributes:
        id (uuid.UUID): エンティティの一意な識別子。デフォルトでUUID4が生成される。
        created_at (datetime): エンティティの作成日時。デフォルトで現在日時が設定される。
        updated_at (datetime): エンティティの最終更新日時。デフォルトで現在日時が設定され、更新時に自動的に更新される。
    """

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime | None = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=False,
    )


# ==============================================================================
# ==============================================================================
# Link Models (中間テーブルモデル)
# 中間テーブルは読み書きする際のBase/Create/Readモデルを定義しない
# ==============================================================================
# ==============================================================================


class MemoTagLink(SQLModel, table=True):
    """メモとタグの関連モデル

    メモとタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        memo_id (uuid.UUID): メモのID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """

    __tablename__ = "memo_tag"

    memo_id: uuid.UUID = Field(foreign_key="memos.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class TaskTagLink(SQLModel, table=True):
    """タスクとタグの関連モデル

    タスクとタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """

    __tablename__ = "task_tag"

    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


# ==============================================================================
# ==============================================================================
# Memo Models (メモモデル)
# ==============================================================================
# ==============================================================================
class MemoBase(BaseModel):
    """メモの基本モデル

    Attributes:
        title (str): メモのタイトル。インデックスが設定されており検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNOT_REQUESTED。
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

    __tablename__ = "memos"

    tasks: list[Task] = Relationship(back_populates="memo")
    tags: list[Tag] = Relationship(back_populates="memos", link_model=MemoTagLink)


class MemoCreate(SQLModel):
    """メモ作成用モデル

    メモを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): メモのタイトル。
        content (str): メモの内容。
        status (MemoStatus): メモの状態。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。
        ai_analysis_log (str | None): AI分析のログ情報。
        processed_at (datetime | None): メモが最後に処理された日時。
    """

    title: str
    content: str
    status: MemoStatus = Field(default=MemoStatus.INBOX)
    ai_suggestion_status: AiSuggestionStatus = Field(default=AiSuggestionStatus.NOT_REQUESTED)
    ai_analysis_log: str | None = None
    processed_at: datetime | None = None


class MemoRead(MemoBase):
    """メモ読み取り用モデル

    メモの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): メモを一意に識別するID。
        title (str): メモのタイトル。インデックスが設定されており検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNOT_REQUESTED。
        ai_analysis_log (str | None): AI分析のログ情報。デフォルトはNone。
        created_at (datetime): メモの作成日時。デフォルトは現在日時。
        updated_at (datetime): メモの最終更新日時。デフォルトは現在日時。
        processed_at (datetime | None): メモが最後に処理された日時。デフォルトはNone。
    """

    id: uuid.UUID


class MemoUpdate(SQLModel):
    """メモ更新用モデル

    メモの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。
    Noneが指定された属性は更新されません。

    Attributes:
        title (str | None): メモのタイトル。
        content (str | None): メモの内容。
        status (MemoStatus | None): メモの状態。
        ai_suggestion_status (AiSuggestionStatus | None): AI提案の状態。
        ai_analysis_log (str | None): AI分析のログ情報。
        processed_at (datetime | None): メモが最後に処理された日時。
    """

    title: str | None = None
    content: str | None = None
    status: MemoStatus | None = None
    ai_suggestion_status: AiSuggestionStatus | None = None
    ai_analysis_log: str | None = None
    processed_at: datetime | None = None


# ==============================================================================
# ==============================================================================
# Project Models (プロジェクトモデル)
# ==============================================================================
# ==============================================================================


class ProjectBase(BaseModel):
    """複数のタスクを束ねる「成果」や「結果」を管理するプロジェクトのモデル。

    Attributes:
        id: プロジェクトを一意に識別するID。
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
        created_at: プロジェクトの作成日時。
        updated_at: プロジェクトの最終更新日時。
    """

    title: str = Field(index=True)
    description: str | None = None
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    due_date: date | None = None


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

    __tablename__ = "projects"

    tasks: list[Task] = Relationship(back_populates="project")


class ProjectCreate(SQLModel):
    """プロジェクト作成用モデル

    プロジェクトを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title: プロジェクトの名称。
        description: プロジェクトの目的や概要。
        status: プロジェクト全体の進捗状況。
        due_date: プロジェクト全体の完了目標日。
    """

    title: str
    description: str | None = None
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    due_date: date | None = None


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


# ==============================================================================
# ==============================================================================
# Tag Models (タグモデル)
# ==============================================================================
# ==============================================================================


class TagBase(BaseModel):
    """タスクやメモを横断的に分類するタグのモデル。

    Attributes:
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時。
    """

    name: str = Field(unique=True, index=True)
    description: str | None = None
    color: str | None = None


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

    __tablename__ = "tags"

    tasks: list[Task] = Relationship(back_populates="tags", link_model=TaskTagLink)
    memos: list[Memo] = Relationship(back_populates="tags", link_model=MemoTagLink)


class TagCreate(SQLModel):
    """タグ作成用モデル

    タグを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
    """

    name: str
    description: str | None = None
    color: str | None = None


class TagRead(TagBase):
    """タグ読み取り用モデル

    タグの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id: タグを一意に識別するID。
        name: タグ名。
        description: タグの目的や概要。
        color: UIで視覚的に区別するための色情報（例: '#FF5733'）。
        created_at: タグの作成日時。
        updated_at: タグの最終更新日時
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


# ==============================================================================
# ==============================================================================
# Task Models (タスクモデル)
# ==============================================================================
# ==============================================================================


class TaskBase(BaseModel):
    """タスクの基本モデル

    Attributes:
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
    """

    title: str = Field(index=True)
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    due_date: date | None = Field(default=None, index=True)
    completed_at: datetime | None = None
    is_recurring: bool = Field(default=False)
    recurrence_rule: str | None = None

    # foreign keys
    project_id: uuid.UUID | None = Field(default=None, foreign_key="projects.id", nullable=True, index=True)
    memo_id: uuid.UUID | None = Field(default=None, foreign_key="memos.id", nullable=True)


class Task(TaskBase, table=True):
    """新しいタスクモデル

    タスクの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

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

    __tablename__ = "tasks"

    project: Project | None = Relationship(back_populates="tasks")
    memo: Memo | None = Relationship(back_populates="tasks")
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTagLink)


class TaskCreate(SQLModel):
    """新しいタスク作成用モデル

    タスクを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title: タスクのタイトル。
        description: タスクの詳細な説明。
        status: タスクの状態。
        due_date: タスクの期限日。
        completed_at: タスクの完了日時。
        project_id: このタスクが属するプロジェクトのID。
        memo_id: このタスクの生成元となったメモのID。
        is_recurring: 繰り返しタスクかどうかを示すフラグ。
        recurrence_rule: 繰り返しのルールを定義する文字列 (iCalendar RRULE形式)。
    """

    title: str
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    due_date: date | None = None
    completed_at: datetime | None = None
    project_id: uuid.UUID | None = None
    memo_id: uuid.UUID | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None


class TaskRead(TaskBase):
    """新しいタスク読み取り用モデル

    タスクの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

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
