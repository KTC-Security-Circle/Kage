"""設定管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from logic.application.base import BaseApplicationService
from logic.services.settings_service import SettingsService

if TYPE_CHECKING:
    from logic.commands.settings_commands import (
        UpdateDatabaseSettingsCommand,
        UpdateSettingCommand,
        UpdateUserSettingsCommand,
        UpdateWindowSettingsCommand,
    )
    from logic.queries.settings_queries import (
        GetAgentsSettingsQuery,
        GetAllSettingsQuery,
        GetDatabaseSettingsQuery,
        GetSettingQuery,
        GetUserSettingsQuery,
        GetWindowSettingsQuery,
    )
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

    def get_all_settings(self, query: GetAllSettingsQuery) -> AppSettings:
        """全設定取得

        Args:
            query: 全設定取得クエリ

        Returns:
            アプリケーション設定全体
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("全設定取得")
        return self._settings_service.get_all_settings()

    def get_window_settings(self, query: GetWindowSettingsQuery) -> WindowSettings:
        """ウィンドウ設定取得

        Args:
            query: ウィンドウ設定取得クエリ

        Returns:
            ウィンドウ設定
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("ウィンドウ設定取得")
        return self._settings_service.get_window_settings()

    def get_user_settings(self, query: GetUserSettingsQuery) -> UserSettings:
        """ユーザー設定取得

        Args:
            query: ユーザー設定取得クエリ

        Returns:
            ユーザー設定
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("ユーザー設定取得")
        return self._settings_service.get_user_settings()

    def get_database_settings(self, query: GetDatabaseSettingsQuery) -> DatabaseSettings:
        """データベース設定取得

        Args:
            query: データベース設定取得クエリ

        Returns:
            データベース設定
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("データベース設定取得")
        return self._settings_service.get_database_settings()

    def get_agents_settings(self, query: GetAgentsSettingsQuery) -> AgentsSettings:
        """エージェント設定取得

        Args:
            query: エージェント設定取得クエリ

        Returns:
            エージェント設定
        """
        _ = query  # 将来の拡張用パラメータ
        logger.debug("エージェント設定取得")
        return self._settings_service.get_agents_settings()

    def get_setting(self, query: GetSettingQuery) -> Any:  # noqa: ANN401
        """個別設定取得

        Args:
            query: 個別設定取得クエリ

        Returns:
            設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.debug(f"個別設定取得: {query.path}")
        return self._settings_service.get_setting_by_path(query.path)

    def update_window_settings(self, command: UpdateWindowSettingsCommand) -> WindowSettings:
        """ウィンドウ設定更新

        Args:
            command: ウィンドウ設定更新コマンド

        Returns:
            更新後のウィンドウ設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"ウィンドウ設定更新開始: {command}")
        return self._settings_service.update_window_settings(
            size=command.size,
            position=command.position,
        )

    def update_user_settings(self, command: UpdateUserSettingsCommand) -> UserSettings:
        """ユーザー設定更新

        Args:
            command: ユーザー設定更新コマンド

        Returns:
            更新後のユーザー設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"ユーザー設定更新開始: {command}")
        return self._settings_service.update_user_settings(
            last_login_user=command.last_login_user,
            theme=command.theme,
            user_name=command.user_name,
        )

    def update_database_settings(self, command: UpdateDatabaseSettingsCommand) -> DatabaseSettings:
        """データベース設定更新

        Args:
            command: データベース設定更新コマンド

        Returns:
            更新後のデータベース設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"データベース設定更新開始: {command}")
        return self._settings_service.update_database_settings(url=command.url)

    def update_setting(self, command: UpdateSettingCommand) -> Any:  # noqa: ANN401
        """個別設定更新

        Args:
            command: 個別設定更新コマンド

        Returns:
            更新後の設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.info(f"個別設定更新開始: {command.path} = {command.value}")
        return self._settings_service.update_setting_by_path(command.path, command.value)
