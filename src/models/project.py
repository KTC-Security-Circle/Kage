"""Projectモデルの定義"""

import uuid
from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from models.task import Task


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

    tasks: list[Task] = Relationship(back_populates="project")


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
