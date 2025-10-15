"""設定Application Serviceのテスト（現行API対応）"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logic.application.settings_application_service import SettingsApplicationService
from settings.manager import ConfigManager
from settings.models import AppSettings

if TYPE_CHECKING:
    from pathlib import Path


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
    settings = app_service.get_all_settings()

    assert settings is not None
    assert hasattr(settings, "window")
    assert hasattr(settings, "user")
    assert hasattr(settings, "database")
    assert hasattr(settings, "agents")


def test_get_window_settings(app_service: SettingsApplicationService) -> None:
    """ウィンドウ設定取得のテスト"""
    window_settings = app_service.get_window_settings()

    assert window_settings is not None
    assert isinstance(window_settings.size, list)
    assert isinstance(window_settings.position, list)


def test_get_user_settings(app_service: SettingsApplicationService) -> None:
    """ユーザー設定取得のテスト"""
    user_settings = app_service.get_user_settings()

    assert user_settings is not None
    assert user_settings.theme in {"light", "dark"}


def test_get_database_settings(app_service: SettingsApplicationService) -> None:
    """データベース設定取得のテスト"""
    db_settings = app_service.get_database_settings()

    assert db_settings is not None
    assert isinstance(db_settings.url, str)


def test_get_agents_settings(app_service: SettingsApplicationService) -> None:
    """エージェント設定取得のテスト"""
    agents_settings = app_service.get_agents_settings()

    assert agents_settings is not None
    assert hasattr(agents_settings, "provider")


def test_get_setting(app_service: SettingsApplicationService) -> None:
    """個別設定取得のテスト"""
    theme = app_service.get_setting("user.theme")

    assert theme in {"light", "dark"}


def test_update_window_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ウィンドウ設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    result = app_service.update_window_settings(size=[1920, 1080], position=[200, 200])

    assert result.size == [1920, 1080]
    assert result.position == [200, 200]


def test_update_user_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ユーザー設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    result = app_service.update_user_settings(last_login_user="tester", theme="dark", user_name="TestUser")

    assert result.theme == "dark"
    assert result.user_name == "TestUser"


def test_update_database_settings(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """データベース設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    result = app_service.update_database_settings(url="sqlite:///test/path/test.db")

    assert result.url == "sqlite:///test/path/test.db"


def test_update_setting(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """個別設定更新のテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    result = app_service.update_setting(path="user.theme", value="dark")

    assert result == "dark"


def test_update_window_settings_validation_error(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ウィンドウ設定更新時のバリデーションエラーのテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    from errors import ValidationError

    with pytest.raises(ValidationError, match=r"サイズは.*2要素のリスト"):
        app_service.update_window_settings(size=[1920], position=[0, 0])


def test_update_user_settings_validation_error(app_service: SettingsApplicationService, tmp_path: Path) -> None:
    """ユーザー設定更新時のバリデーションエラーのテスト"""
    # グローバルマネージャーをモックするため、一時的な設定で実行
    config_path = tmp_path / "test_config.yaml"
    temp_manager = ConfigManager(config_path, AppSettings)

    from logic.services.settings_service import SettingsService

    app_service._settings_service = SettingsService(temp_manager)

    from errors import ValidationError

    with pytest.raises(ValidationError, match="テーマは'light'または'dark'"):
        app_service.update_user_settings(last_login_user="tester", theme="invalid", user_name="User")
