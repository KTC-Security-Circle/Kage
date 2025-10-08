"""設定Application Serviceのテスト"""

from __future__ import annotations

from pathlib import Path

import pytest

from logic.application.settings_application_service import SettingsApplicationService
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
from settings.manager import ConfigManager, get_config_manager
from settings.models import AppSettings


@pytest.fixture
def temp_config_manager(tmp_path: Path) -> ConfigManager[AppSettings]:
    """テスト用の一時ConfigManagerを作成

    Args:
        tmp_path: pytest提供の一時ディレクトリ

    Returns:
        一時的な設定マネージャー
    """
    config_path = tmp_path / "test_config.yaml"
    return ConfigManager(config_path, AppSettings)


@pytest.fixture
def app_service() -> SettingsApplicationService:
    """テスト用のSettingsApplicationServiceを作成

    Returns:
        設定アプリケーションサービスのインスタンス
    """
    return SettingsApplicationService()


def test_get_all_settings(app_service: SettingsApplicationService) -> None:
    """全設定取得のテスト"""
    query = GetAllSettingsQuery()
    settings = app_service.get_all_settings(query)

    assert settings is not None
    assert hasattr(settings, "window")
    assert hasattr(settings, "user")
    assert hasattr(settings, "database")
    assert hasattr(settings, "agents")


def test_get_window_settings(app_service: SettingsApplicationService) -> None:
    """ウィンドウ設定取得のテスト"""
    query = GetWindowSettingsQuery()
    window_settings = app_service.get_window_settings(query)

    assert window_settings is not None
    assert isinstance(window_settings.size, list)
    assert isinstance(window_settings.position, list)


def test_get_user_settings(app_service: SettingsApplicationService) -> None:
    """ユーザー設定取得のテスト"""
    query = GetUserSettingsQuery()
    user_settings = app_service.get_user_settings(query)

    assert user_settings is not None
    assert user_settings.theme in {"light", "dark"}


def test_get_database_settings(app_service: SettingsApplicationService) -> None:
    """データベース設定取得のテスト"""
    query = GetDatabaseSettingsQuery()
    db_settings = app_service.get_database_settings(query)

    assert db_settings is not None
    assert isinstance(db_settings.url, str)


def test_get_agents_settings(app_service: SettingsApplicationService) -> None:
    """エージェント設定取得のテスト"""
    query = GetAgentsSettingsQuery()
    agents_settings = app_service.get_agents_settings(query)

    assert agents_settings is not None
    assert hasattr(agents_settings, "provider")


def test_get_setting(app_service: SettingsApplicationService) -> None:
    """個別設定取得のテスト"""
    query = GetSettingQuery(path="user.theme")
    theme = app_service.get_setting(query)

    assert theme in {"light", "dark"}


def test_update_window_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ウィンドウ設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateWindowSettingsCommand(size=[1920, 1080], position=[200, 200])
    result = app_service.update_window_settings(command)

    assert result.size == [1920, 1080]
    assert result.position == [200, 200]


def test_update_user_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ユーザー設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateUserSettingsCommand(theme="dark", user_name="TestUser")
    result = app_service.update_user_settings(command)

    assert result.theme == "dark"
    assert result.user_name == "TestUser"


def test_update_database_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """データベース設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateDatabaseSettingsCommand(url="sqlite:///test/path/test.db")
    result = app_service.update_database_settings(command)

    assert result.url == "sqlite:///test/path/test.db"


def test_update_setting(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """個別設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateSettingCommand(path="user.theme", value="dark")
    result = app_service.update_setting(command)

    assert result == "dark"


def test_update_window_settings_validation_error(
    app_service: SettingsApplicationService, tmp_path: Path
) -> None:
    """ウィンドウ設定更新時のバリデーションエラーのテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateWindowSettingsCommand(size=[1920])  # 不正なサイズ
    with pytest.raises(ValueError, match="サイズは.*2要素のリスト"):
        app_service.update_window_settings(command)


def test_update_user_settings_validation_error(
    app_service: SettingsApplicationService, tmp_path: Path
) -> None:
    """ユーザー設定更新時のバリデーションエラーのテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    command = UpdateUserSettingsCommand(theme="invalid")  # 不正なテーマ
    with pytest.raises(ValueError, match="テーマは'light'または'dark'"):
        app_service.update_user_settings(command)
