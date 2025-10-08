"""設定関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GetAllSettingsQuery:
    """全設定取得クエリ"""


@dataclass
class GetWindowSettingsQuery:
    """ウィンドウ設定取得クエリ"""


@dataclass
class GetUserSettingsQuery:
    """ユーザー設定取得クエリ"""


@dataclass
class GetDatabaseSettingsQuery:
    """データベース設定取得クエリ"""


@dataclass
class GetAgentsSettingsQuery:
    """エージェント設定取得クエリ"""


@dataclass
class GetSettingQuery:
    """個別設定取得クエリ

    ドット区切りパスで特定の設定値を取得する
    """

    path: str  # "user.theme" や "window.size" のようなドット区切りパス
