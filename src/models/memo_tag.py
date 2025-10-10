"""MemoTagモデルの定義（多対多の関連テーブル）"""

import uuid

from sqlmodel import Field, SQLModel


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
