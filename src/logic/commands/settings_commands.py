"""設定関連のコマンドオブジェクト

Application Service層で使用するCommand DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UpdateWindowSettingsCommand:
    """ウィンドウ設定更新コマンド"""

    size: list[int] | None = None
    position: list[int] | None = None


@dataclass
class UpdateUserSettingsCommand:
    """ユーザー設定更新コマンド"""

    last_login_user: str | None = None
    theme: str | None = None
    user_name: str | None = None


@dataclass
class UpdateDatabaseSettingsCommand:
    """データベース設定更新コマンド"""

    url: str | None = None


@dataclass
class UpdateAgentModelCommand:
    """エージェントモデル設定更新コマンド"""

    agent_name: str
    model_name: str


@dataclass
class UpdateSettingCommand:
    """汎用設定更新コマンド

    任意のネストされた設定パスに対して値を更新する
    """

    path: str  # "user.theme" や "window.size" のようなドット区切りパス
    value: Any
