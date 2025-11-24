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
# ruff: noqa: UP006 UP035

import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict
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

    @classmethod
    def parse(cls, value: str) -> "ProjectStatus":
        """任意のステータス文字列をProjectStatus Enumへ変換する。

        英語コード、日本語表示値、ハイフン/アンダースコア混在を吸収し、
        統一された Enum 値を返す。

        Args:
            value: 英語コードまたは日本語表示値（例: "active", "進行中", "On-Hold"）

        Returns:
            対応する ProjectStatus Enum

        Raises:
            ValueError: 未知のステータス値が指定された場合
        """
        # 正規化: 小文字化、ハイフン→アンダースコア
        normalized = value.strip().lower().replace("-", "_")

        # 英語コードマッピング
        code_map = {
            "active": cls.ACTIVE,
            "on_hold": cls.ON_HOLD,
            "completed": cls.COMPLETED,
            "cancelled": cls.CANCELLED,
        }

        # 日本語→英語コードマッピング
        jp_to_code = {
            "進行中": "active",
            "計画中": "active",  # 計画中も進行中扱い
            "保留": "on_hold",
            "完了": "completed",
            "中止": "cancelled",
            "キャンセル": "cancelled",
        }

        # 英語コードで直接マッチ
        if normalized in code_map:
            return code_map[normalized]

        # 日本語から英語コードへ変換
        raw = value.strip()
        if raw in jp_to_code:
            return code_map[jp_to_code[raw]]

        # 未知の値
        valid_values = list(code_map.keys()) + list(jp_to_code.keys())
        msg = f"Unknown status value: '{value}'. Valid values: {valid_values}"
        raise ValueError(msg)

    @classmethod
    def display_label(cls, status: "ProjectStatus") -> str:
        """ProjectStatus Enumから日本語表示ラベルを取得する。

        Args:
            status: ProjectStatus Enum値

        Returns:
            対応する日本語表示ラベル
        """
        label_map = {
            cls.ACTIVE: "進行中",
            cls.ON_HOLD: "保留",
            cls.COMPLETED: "完了",
            cls.CANCELLED: "中止",
        }
        return label_map.get(status, status.value)

    @classmethod
    def get_color(cls, status: "ProjectStatus") -> str:
        """ProjectStatus Enumからテーマカラーを取得する。

        Args:
            status: ProjectStatus Enum値

        Returns:
            Flet Color定数文字列
        """
        import flet as ft

        color_map = {
            cls.ACTIVE: ft.Colors.BLUE,
            cls.ON_HOLD: ft.Colors.ORANGE,
            cls.COMPLETED: ft.Colors.GREEN,
            cls.CANCELLED: ft.Colors.GREY,
        }
        return color_map.get(status, ft.Colors.GREY)


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
    DRAFT = "draft"
    TODAYS = "todays"
    PROGRESS = "progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELED = "canceled"
    OVERDUE = "overdue"


class TermStatus(str, Enum):
    """用語のステータス

    Attributes:
        DRAFT: 草案状態（未承認）
        APPROVED: 承認済み
        DEPRECATED: 非推奨（使用すべきでない）
    """

    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


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


class TermTagLink(SQLModel, table=True):
    """用語とタグの関連モデル

    用語とタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        term_id (uuid.UUID): 用語のID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """

    __tablename__ = "term_tag"

    term_id: uuid.UUID = Field(foreign_key="terms.id", primary_key=True)
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

    tasks: List["Task"] = Relationship(back_populates="memo")
    tags: List["Tag"] = Relationship(back_populates="memos", link_model=MemoTagLink)


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

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tags: List["TagRead"] = Field(default_factory=list)
    tasks: List["TaskRead"] = Field(default_factory=list)


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

    tasks: List["Task"] = Relationship(back_populates="project")


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

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tasks: List["TaskRead"] = Field(default_factory=list)


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

    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)
    memos: List["Memo"] = Relationship(back_populates="tags", link_model=MemoTagLink)
    terms: List["Term"] = Relationship(back_populates="tags", link_model=TermTagLink)


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

    model_config = ConfigDict(from_attributes=True)

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

    project: Optional["Project"] = Relationship(back_populates="tasks")
    memo: Optional["Memo"] = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)


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

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tags: List["TagRead"] = Field(default_factory=list)


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


# ==============================================================================
# ==============================================================================
# Terminology Models (用語管理モデル)
# ==============================================================================
# ==============================================================================


class TermBase(BaseModel):
    """用語の基本モデル

    Attributes:
        key: 用語のキー（一意識別子、例: "LLM", "RAG"）。
        title: 用語の正式名称。
        description: 用語の説明・定義。
        status: 用語のステータス（草案/承認済み/非推奨）。
        source_url: 出典や参照先のURL。
    """

    key: str = Field(unique=True, index=True, max_length=100)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TermStatus = Field(default=TermStatus.DRAFT, index=True)
    source_url: str | None = Field(default=None, max_length=500)


class Term(TermBase, table=True):
    """用語モデル

    社内固有の用語・略語・定義を管理するモデルクラス。
    タグや同義語と関連付けて、検索性とLLM連携を強化します。

    Attributes:
        id: 用語を一意に識別するID。
        key: 用語のキー（一意識別子）。
        title: 用語の正式名称。
        description: 用語の説明・定義。
        status: 用語のステータス。
        source_url: 出典や参照先のURL。
        created_at: 用語の作成日時。
        updated_at: 用語の最終更新日時。
        synonyms: この用語の同義語のリスト。
        tags: この用語に付けられたタグのリスト。
    """

    __tablename__ = "terms"

    synonyms: List["Synonym"] = Relationship(
        back_populates="term", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: List["Tag"] = Relationship(back_populates="terms", link_model=TermTagLink)


class TermCreate(SQLModel):
    """用語作成用モデル

    用語を新規作成する際に使用するモデルクラス。

    Attributes:
        key: 用語のキー（一意識別子）。
        title: 用語の正式名称。
        description: 用語の説明・定義。
        status: 用語のステータス。
        source_url: 出典や参照先のURL。
    """

    key: str = Field(max_length=100)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TermStatus = Field(default=TermStatus.DRAFT)
    source_url: str | None = Field(default=None, max_length=500)


class TermRead(TermBase):
    """用語読み取り用モデル

    用語の情報を読み取る際に使用するモデルクラス。

    Attributes:
        id: 用語を一意に識別するID。
        key: 用語のキー。
        title: 用語の正式名称。
        description: 用語の説明・定義。
        status: 用語のステータス。
        source_url: 出典や参照先のURL。
        created_at: 用語の作成日時。
        updated_at: 用語の最終更新日時。
    """

    id: uuid.UUID


class TermUpdate(SQLModel):
    """用語更新用モデル

    用語の情報を更新する際に使用するモデルクラス。
    Noneが指定された属性は更新されません。

    Attributes:
        key: 用語のキー。
        title: 用語の正式名称。
        description: 用語の説明・定義。
        status: 用語のステータス。
        source_url: 出典や参照先のURL。
    """

    key: str | None = Field(default=None, max_length=100)
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TermStatus | None = None
    source_url: str | None = Field(default=None, max_length=500)


# ==============================================================================
# Synonym Models (同義語モデル)
# ==============================================================================


class SynonymBase(SQLModel):
    """同義語の基本モデル

    Attributes:
        text: 同義語のテキスト（例: "大規模言語モデル", "LLM"）。
        term_id: この同義語が属する用語のID。
    """

    text: str = Field(max_length=200, index=True)
    term_id: uuid.UUID = Field(foreign_key="terms.id", index=True)


class Synonym(SynonymBase, table=True):
    """同義語モデル

    用語の同義語・別名を管理するモデルクラス。
    検索時に同義語展開を行い、検索精度を向上させます。

    Attributes:
        id: 同義語を一意に識別するID。
        text: 同義語のテキスト。
        term_id: この同義語が属する用語のID。
        term: この同義語が属する用語オブジェクト。
    """

    __tablename__ = "synonyms"

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    term: "Term" = Relationship(back_populates="synonyms")


class SynonymCreate(SQLModel):
    """同義語作成用モデル

    同義語を新規作成する際に使用するモデルクラス。

    Attributes:
        text: 同義語のテキスト。
        term_id: この同義語が属する用語のID。
    """

    text: str = Field(max_length=200)
    term_id: uuid.UUID


class SynonymRead(SynonymBase):
    """同義語読み取り用モデル

    同義語の情報を読み取る際に使用するモデルクラス。

    Attributes:
        id: 同義語を一意に識別するID。
        text: 同義語のテキスト。
        term_id: この同義語が属する用語のID。
    """

    id: uuid.UUID


class SynonymUpdate(SQLModel):
    """同義語更新用モデル

    同義語の情報を更新する際に使用するモデルクラス。
    Noneが指定された属性は更新されません。

    Attributes:
        text: 同義語のテキスト。
        term_id: この同義語が属する用語のID。
    """

    text: str | None = Field(default=None, max_length=200)
    term_id: uuid.UUID | None = None
