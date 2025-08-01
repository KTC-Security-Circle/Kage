"""TaskTagモデルの定義（多対多の関連テーブル）"""

import uuid

from sqlmodel import Field, SQLModel


class TaskTagBase(SQLModel):
    """タスクとタグの関連の基本モデル

    タスクとタグの多対多関係を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。
        tag_id (uuid.UUID): タグのID。
    """

    task_id: uuid.UUID = Field(foreign_key="task.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)


class TaskTag(TaskTagBase, table=True):
    """タスクとタグの関連モデル

    タスクとタグの多対多関係をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。複合主キーの一部。
        tag_id (uuid.UUID): タグのID。複合主キーの一部。
    """


class TaskTagCreate(TaskTagBase):
    """タスクとタグの関連作成用モデル

    タスクとタグの関連を新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。
        tag_id (uuid.UUID): タグのID。
    """


class TaskTagRead(TaskTagBase):
    """タスクとタグの関連読み取り用モデル

    タスクとタグの関連情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        task_id (uuid.UUID): タスクのID。
        tag_id (uuid.UUID): タグのID。
    """
