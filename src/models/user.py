"""Userモデルの定義"""

import uuid

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """ユーザーの基本モデル

    ユーザーの基本情報を定義するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name (str): ユーザー名。
        email (str): メールアドレス。インデックスが設定されており、検索に使用されます。
    """

    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    """ユーザーモデル

    ユーザーの情報をデータベースに保存するためのモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID | None): ユーザーのID。デフォルトはNoneで、データベースに保存時に自動生成されます。
        name (str): ユーザー名。
        email (str): メールアドレス。インデックスが設定されており、検索に使用されます。
    """

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class UserCreate(UserBase):
    """ユーザー作成用モデル

    ユーザーを新規作成する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name (str): ユーザー名。
        email (str): メールアドレス。インデックスが設定されており、検索に使用されます。
    """


class UserRead(UserBase):
    """ユーザー読み取り用モデル

    ユーザーの情報を読み取る際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        id (uuid.UUID): ユーザーのID。
        name (str): ユーザー名。
        email (str): メールアドレス。インデックスが設定されており、検索に使用されます。
    """

    id: uuid.UUID


class UserUpdate(SQLModel):
    """ユーザー更新用モデル

    ユーザーの情報を更新する際に使用するモデルクラス。SQLModelを使用してデータベースと連携します。

    Attributes:
        name (str | None): ユーザー名。Noneの場合は更新しない。
        email (str | None): メールアドレス。Noneの場合は更新しない。
    """

    name: str | None = None
    email: str | None = None
