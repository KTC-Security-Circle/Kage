"""アプリ設定モデル定義モジュール。

[AI GENERATED] Pydantic v2 を用いてアプリケーション設定の不変モデルを定義する。`ConfigManager` が YAML との変換を行う。
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WindowSettings(BaseModel):
    """ウィンドウ表示に関する設定。

    サイズと位置は整数 2 要素のリストで保持する。
    """

    model_config = ConfigDict(frozen=True)

    size: list[int] = Field(
        default=[1280, 720],
        description="""起動時のウィンドウサイズ。[幅, 高さ] のリスト。""",
    )
    position: list[int] = Field(
        default=[100, 100],
        description="起動時のウィンドウ位置。[X, Y] のリスト。",
    )


class EditableWindowSettings(BaseModel):
    """編集可能なウィンドウ設定。

    不変モデルとの差異: frozen=False。
    """

    model_config = ConfigDict(frozen=False)

    size: list[int] = Field(
        default=[1280, 720],
        description="""起動時のウィンドウサイズ。[幅, 高さ] のリスト。""",
    )
    position: list[int] = Field(
        default=[100, 100],
        description="起動時のウィンドウ位置。[X, Y] のリスト。",
    )


class UserSettings(BaseModel):
    """ユーザー固有の UI/動作設定。"""

    model_config = ConfigDict(frozen=True)

    last_login_user: str | None = Field(
        default=None,
        description="最後にログインしたユーザー名 (未ログインは null)。",
    )
    theme: str = Field(
        default="light",
        description="UI テーマ。'light' または 'dark'。",
    )


class EditableUserSettings(BaseModel):
    """編集可能なユーザー設定。"""

    model_config = ConfigDict(frozen=False)

    last_login_user: str | None = Field(
        default=None,
        description="最後にログインしたユーザー名 (未ログインは null)。",
    )
    theme: str = Field(
        default="light",
        description="UI テーマ。'light' または 'dark'。",
    )


class DatabaseSettings(BaseModel):
    """データベース接続に関する設定。"""

    model_config = ConfigDict(frozen=True)

    # 既存の SQLite 利用を想定し最低限のフィールドのみ。将来拡張時は別モデルへ分離。
    url: str = Field(
        default="sqlite:///storage/data/tasks.db",
        description="接続 URL。既定はアプリ内 SQLite ファイル。",
    )


class EditableDatabaseSettings(BaseModel):
    """編集可能なデータベース設定。"""

    model_config = ConfigDict(frozen=False)

    url: str = Field(
        default="sqlite:///storage/data/tasks.db",
        description="接続 URL。既定はアプリ内 SQLite ファイル。",
    )


class AppSettings(BaseModel):
    """アプリケーション全体の設定ルートモデル。

    このファイルは初回起動時に YAML として生成され、以後編集はコンテキストマネージャ経由で行う。
    """

    model_config = ConfigDict(frozen=True)

    window: WindowSettings = Field(default_factory=WindowSettings, description="ウィンドウ関連設定。")
    user: UserSettings = Field(default_factory=UserSettings, description="ユーザー関連設定。")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings, description="データベース設定。")


class EditableAppSettings(BaseModel):
    """編集可能なアプリケーション設定。"""

    model_config = ConfigDict(frozen=False)

    window: EditableWindowSettings = Field(default_factory=EditableWindowSettings, description="ウィンドウ関連設定。")
    user: EditableUserSettings = Field(default_factory=EditableUserSettings, description="ユーザー関連設定。")
    database: EditableDatabaseSettings = Field(
        default_factory=EditableDatabaseSettings, description="データベース設定。"
    )


__all__ = [
    "WindowSettings",
    "UserSettings",
    "DatabaseSettings",
    "AppSettings",
    "EditableWindowSettings",
    "EditableUserSettings",
    "EditableDatabaseSettings",
    "EditableAppSettings",
]
