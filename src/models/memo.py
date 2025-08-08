"""Memoモデルの定義"""

import uuid

from sqlmodel import Field, SQLModel


class MemoBase(SQLModel):
    """メモの基本モデル"""

    content: str = Field(default="", description="マークダウン形式のメモ内容")
    task_id: uuid.UUID = Field(foreign_key="task.id", index=True)


class Memo(MemoBase, table=True):
    """メモモデル"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class MemoCreate(MemoBase):
    """メモ作成用モデル"""


class MemoRead(MemoBase):
    """メモ読み取り用モデル"""

    id: uuid.UUID


class MemoUpdate(SQLModel):
    """メモ更新用モデル"""

    content: str | None = None
