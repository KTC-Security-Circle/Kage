"""Memoモデルの定義

すべての情報の入り口となる「気になること」を格納します。
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from models.tag import Tag
from models.task import Task


class MemoStatus(Enum):
    """メモの状態を表す列挙型

    Attributes:
        Inbox: タスクになる前の整理をされていないメモ
        Active: Inboxのメモからタスクが生成された際にこのステータスになる
        Idea: タスクにもプロジェクトにもならなかったメモ
        Archive: タスクがCompletedかCanceledになった際にそのタスクに紐づいたメモが行き着く先
                 メモに対して複数タスクが紐づいている場合は紐づいているタスクすべてが先ほどのステータスになっている必要がある
    """

    Inbox = "inbox"
    Active = "active"
    Idea = "idea"
    Archive = "archive"


class AiSuggestionStatus(Enum):
    """AI提案の状態を表す列挙型

    Attributes:
        NotRequested: AI提案がまだリクエストされていない状態
        Pending: AI提案がリクエストされ、処理中の状態
        Available: AI提案が利用可能な状態
        Reviewed: AI提案がユーザーによって確認された状態
        Failed: AI提案のリクエストが失敗した状態
    """

    NotRequested = "not_requested"
    Pending = "pending"
    Available = "available"
    Reviewed = "reviewed"
    Failed = "failed"


class MemoBase(SQLModel):
    """メモの基本モデル

    Attributes:
        title (str): メモのタイトル。インデックスが設定されており
                     検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNotRequested。
        ai_analysis_log (dict | None): AI分析のログ情報。デフォルトはNone。
        created_at (datetime): メモの作成日時。デフォルトは現在日時。
        updated_at (datetime): メモの最終更新日時。デフォルトは現在日時。
        processed_at (datetime | None): メモが最後に処理された日時。デフォルトはNone。
    """

    title: str = Field(index=True)
    content: str
    status: MemoStatus = Field(default=MemoStatus.Inbox, index=True)
    ai_suggestion_status: AiSuggestionStatus = Field(default=AiSuggestionStatus.NotRequested, index=True)
    ai_analysis_log: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    processed_at: datetime | None = Field(default=None, index=True)

    tasks: list[Task] = Relationship(back_populates="memo")
    tags: list[Tag] = Relationship(back_populates="memos", link_model="MemoTagLink")


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


class MemoCreate(MemoBase):
    """メモ作成用モデル

    メモを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): メモのタイトル。インデックスが設定されており、検索可能です。
        content (str): メモの内容。デフォルトは空文字列。
        status (MemoStatus): メモの状態。デフォルトはInbox。
        ai_suggestion_status (AiSuggestionStatus): AI提案の状態。デフォルトはNotRequested。
        ai_analysis_log (dict | None): AI分析のログ情報。デフォルトはNone。
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
        ai_analysis_log (dict | None): AI分析のログ情報。デフォルトはNone。
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
