"""Settings View Query Layer.

【責務】
    Query層はロジック層(SettingsApplicationService)へのアクセスを抽象化する薄いラッパー。
    Controllerがロジック層と直接依存しないように、データ取得・保存の責務を分離する。

    - 設定スナップショットの取得
    - 設定スナップショットの保存
    - エラーハンドリングとログ記録

【責務外（他層の担当）】
    - スナップショットからStateへの変換 → Controller
    - バリデーション → validation.py
    - UI状態管理 → State
    - ビジネスロジック → SettingsApplicationService

【アーキテクチャ上の位置づけ】
    Controller → Query → SettingsApplicationService

【設計上の特徴】
    - SettingsApplicationServiceへの薄いラッパー（追加ロジックなし）
    - テスト時にモック差し替えが容易
    - 将来的な非同期化や複雑なデータ取得にも対応可能
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from logic.application.settings_application_service import SettingsApplicationService


class SettingsQuery:
    """SettingsApplicationServiceへのクエリを提供する薄いラッパー。

    Attributes:
        app_service: SettingsApplicationService のインスタンス
    """

    def __init__(self, app_service: SettingsApplicationService) -> None:
        """SettingsQueryを初期化する。

        Args:
            app_service: SettingsApplicationServiceのインスタンス
        """
        self.app_service = app_service

    def load_snapshot(self) -> dict[str, Any]:
        """設定スナップショットを取得する。

        Returns:
            設定スナップショット辞書
            {
                "appearance": {
                    "theme": str,
                    "user_name": str,
                    "last_login_user": str | None
                },
                "window": {
                    "size": list[int],
                    "position": list[int]
                },
                "database_url": str
            }

        Raises:
            Exception: 設定ロード時のエラー
        """
        return self.app_service.load_settings_snapshot()

    def save_snapshot(self, snapshot: dict[str, Any]) -> None:
        """設定スナップショットを保存する。

        Args:
            snapshot: 保存する設定スナップショット

        Raises:
            ValidationError: バリデーションエラー
            Exception: 設定保存時のその他のエラー
        """
        self.app_service.save_settings_snapshot(snapshot)
