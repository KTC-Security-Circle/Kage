"""TaskTagLinkモデルの定義（多対多の関連テーブル）"""

import uuid

from sqlmodel import Field, SQLModel


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
