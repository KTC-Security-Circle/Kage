"""Settings View Query Layer.

【責務】
    Query層は設定値の取得を担当する。
    設定管理サービスから現在の設定値を読み取り、純粋関数として提供する。

    - 現在の設定値の取得
    - 編集可能モデルへの変換
    - テーマ選択肢の提供

【責務外（他層の担当）】
    - 設定値の保存 → Controller/ApplicationService
    - UI表示用の整形 → Presenter
    - 状態管理 → State

【設計上の特徴】
    - 純粋関数（副作用なし）
    - ConfigManagerからの読み取りのみ
    - 型安全な返り値

【アーキテクチャ上の位置づけ】
    View → Controller → Query.fetch_current_settings()
                            ↓
                        State更新
"""

from __future__ import annotations

from dataclasses import dataclass

from settings.manager import get_config_manager
from settings.models import (
    EditableUserSettings,
    EditableWindowSettings,
)


@dataclass
class CurrentSettingsData:
    """現在の設定値をまとめたデータクラス。"""

    appearance: EditableUserSettings
    window: EditableWindowSettings
    database_url: str


def fetch_current_settings() -> CurrentSettingsData:
    """現在の設定値を取得する。

    ConfigManagerから最新の設定値を取得し、編集可能なモデルに変換する。

    Returns:
        現在の設定値
    """
    config_manager = get_config_manager()
    settings = config_manager.settings

    # frozenモデルをEditableモデルに変換
    appearance = EditableUserSettings(
        theme=settings.user.theme,
        user_name=settings.user.user_name,
        last_login_user=settings.user.last_login_user,
    )

    window = EditableWindowSettings(
        size=settings.window.size.copy(),
        position=settings.window.position.copy(),
    )

    database_url = config_manager.database_url

    return CurrentSettingsData(
        appearance=appearance,
        window=window,
        database_url=database_url,
    )


def get_available_themes() -> list[tuple[str, str]]:
    """利用可能なテーマの選択肢を返す。

    Returns:
        (value, label) のタプルのリスト
    """
    return [
        ("light", "ライト"),
        ("dark", "ダーク"),
    ]
