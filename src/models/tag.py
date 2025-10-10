"""Tagモデルの定義"""

import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from models.memo import Memo
from models.memo_tag import MemoTagLink
from models.task import Task
from models.task_tag import TaskTagLink


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

    tasks: list[Task] = Relationship(back_populates="tags", link_model=TaskTagLink)
    memos: list[Memo] = Relationship(back_populates="tags", link_model=MemoTagLink)


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
