"""設定管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.services.settings_service import SettingsService
from settings.manager import invalidate_config_manager

if TYPE_CHECKING:
    from settings.models import AgentsSettings, AppSettings, DatabaseSettings, UserSettings, WindowSettings


class SettingsApplicationService(BaseApplicationService[None]):
    """設定管理のApplication Service

    設定の読み取りと更新を行う
    Note: 設定管理はConfigManagerがシングルトンで管理するため、
          Unit of Workパターンは使用しない
    """

    def __init__(self) -> None:
        """SettingsApplicationServiceの初期化"""
        super().__init__()
        self._settings_service = SettingsService()

    @classmethod
    def invalidate(cls) -> None:
        """共有インスタンスと ConfigManager を無効化する。

        次回 get_instance() で新しい設定マネージャー/サービスが構築される。
        """
        invalidate_config_manager()
        super().invalidate()

    def get_all_settings(self) -> AppSettings:
        """全設定取得

        Returns:
            アプリケーション設定全体
        """
        logger.debug("全設定取得")
        return self._settings_service.get_all_settings()

    def get_window_settings(self) -> WindowSettings:
        """ウィンドウ設定取得

        Returns:
            ウィンドウ設定
        """
        logger.debug("ウィンドウ設定取得")
        return self._settings_service.get_window_settings()

    def get_user_settings(self) -> UserSettings:
        """ユーザー設定取得

        Returns:
            ユーザー設定
        """
        logger.debug("ユーザー設定取得")
        return self._settings_service.get_user_settings()

    def get_database_settings(self) -> DatabaseSettings:
        """データベース設定取得

        Returns:
            データベース設定
        """
        logger.debug("データベース設定取得")
        return self._settings_service.get_database_settings()

    def get_agents_settings(self) -> AgentsSettings:
        """エージェント設定取得

        Returns:
            エージェント設定
        """
        logger.debug("エージェント設定取得")
        return self._settings_service.get_agents_settings()

    def get_setting(self, path: str) -> Any:  # noqa: ANN401
        """個別設定取得

        Args:
            path: 個別設定取得パス

        Returns:
            設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.debug(f"個別設定取得: {path}")
        return self._settings_service.get_setting_by_path(path)

    def update_window_settings(self, size: list[int], position: list[int]) -> WindowSettings:
        """ウィンドウ設定更新

        Args:
            size: ウィンドウサイズ
            position: ウィンドウ位置

        Returns:
            更新後のウィンドウ設定

        Raises:
            ValueError: バリデーションエラー
        """
        return self._settings_service.update_window_settings(
            size=size,
            position=position,
        )

    def update_user_settings(self, last_login_user: str, theme: str, user_name: str) -> UserSettings:
        """ユーザー設定更新

        Args:
            last_login_user: 最終ログインユーザー名
            theme: テーマ
            user_name: ユーザー名

        Returns:
            更新後のユーザー設定

        Raises:
            ValueError: バリデーションエラー
        """
        return self._settings_service.update_user_settings(
            last_login_user=last_login_user,
            theme=theme,
            user_name=user_name,
        )

    def update_database_settings(self, url: str) -> DatabaseSettings:
        """データベース設定更新

        Args:
            url: データベースURL

        Returns:
            更新後のデータベース設定

        Raises:
            ValueError: バリデーションエラー
        """
        return self._settings_service.update_database_settings(url=url)

    def update_setting(self, path: str, value: Any) -> Any:  # noqa: ANN401
        """個別設定更新

        Args:
            path: 個別設定更新パス
            value: 更新後の設定値

        Returns:
            更新後の設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.info(f"個別設定更新開始: {path} = {value}")
        return self._settings_service.update_setting_by_path(path, value)

    def load_settings_snapshot(self) -> dict[str, Any]:
        """設定値をスナップショット形式でロードする。

        View層が必要とする設定値を辞書形式で返す。

        Returns:
            設定スナップショット辞書
        """
        logger.debug("設定スナップショットをロード")
        return self._settings_service.load_settings_snapshot()

    def save_settings_snapshot(self, snapshot: dict[str, Any]) -> None:
        """設定スナップショットを保存する。

        Args:
            snapshot: 保存する設定スナップショット

        Raises:
            ValidationError: バリデーションエラー
        """
        logger.info("設定スナップショットを保存")
        self._settings_service.save_settings_snapshot(snapshot)
