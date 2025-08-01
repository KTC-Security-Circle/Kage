"""Projectモデルの定義"""

import uuid
from enum import Enum

from sqlmodel import Field, SQLModel


class ProjectStatus(str, Enum):
    """プロジェクトのステータス"""

    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectBase(SQLModel):
    """プロジェクトの基本モデル

    プロジェクトの基本情報を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): プロジェクト名。インデックスが設定されており、検索に使用されます。
        description (str): プロジェクトの説明。デフォルトは空文字列。
        status (ProjectStatus): プロジェクトのステータス。デフォルトはACTIVE。
    """

    title: str = Field(index=True)
    description: str = Field(default="")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, index=True)


class Project(ProjectBase, table=True):
    """プロジェクトモデル

    プロジェクトの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID | None): プロジェクトのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        title (str): プロジェクト名。インデックスが設定されており、検索に使用されます。
        description (str): プロジェクトの説明。デフォルトは空文字列。
        status (ProjectStatus): プロジェクトのステータス。デフォルトはACTIVE。
    """

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class ProjectCreate(ProjectBase):
    """プロジェクト作成用モデル

    プロジェクトを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str): プロジェクト名。インデックスが設定されており、検索に使用されます。
        description (str): プロジェクトの説明。デフォルトは空文字列。
        status (ProjectStatus): プロジェクトのステータス。デフォルトはACTIVE。
    """


class ProjectRead(ProjectBase):
    """プロジェクト読み取り用モデル

    プロジェクトの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): プロジェクトのID。
        title (str): プロジェクト名。インデックスが設定されており、検索に使用されます。
        description (str): プロジェクトの説明。デフォルトは空文字列。
        status (ProjectStatus): プロジェクトのステータス。デフォルトはACTIVE。
    """

    id: uuid.UUID


class ProjectUpdate(SQLModel):
    """プロジェクト更新用モデル

    プロジェクトの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        title (str | None): プロジェクト名。Noneの場合は更新しない。
        description (str | None): プロジェクトの説明。Noneの場合は更新しない。
        status (ProjectStatus | None): プロジェクトのステータス。Noneの場合は更新しない。
    """

    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
