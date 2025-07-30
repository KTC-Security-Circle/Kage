"""Tagモデルの定義"""

import uuid

from sqlmodel import Field, SQLModel


class TagBase(SQLModel):
    """タグの基本モデル

    タグの基本情報を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        user_id (uuid.UUID): タグを所有するユーザーのID。
        name (str): タグ名（例: @PC, #重要）。インデックスが設定されており、検索に使用されます。
    """

    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(index=True)


class Tag(TagBase, table=True):
    """タグモデル

    タグの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID | None): タグのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        user_id (uuid.UUID): タグを所有するユーザーのID。
        name (str): タグ名（例: @PC, #重要）。インデックスが設定されており、検索に使用されます。
    """

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class TagCreate(TagBase):
    """タグ作成用モデル

    タグを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        user_id (uuid.UUID): タグを所有するユーザーのID。
        name (str): タグ名（例: @PC, #重要）。インデックスが設定されており、検索に使用されます。
    """


class TagRead(TagBase):
    """タグ読み取り用モデル

    タグの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): タグのID。
        user_id (uuid.UUID): タグを所有するユーザーのID。
        name (str): タグ名（例: @PC, #重要）。インデックスが設定されており、検索に使用されます。
    """

    id: uuid.UUID


class TagUpdate(SQLModel):
    """タグ更新用モデル

    タグの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name (str | None): タグ名。Noneの場合は更新しない。
    """

    name: str | None = None
