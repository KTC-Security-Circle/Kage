"""設定サービスのテスト"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from agents.agent_conf import OpenVINODevice
from errors import ValidationError
from logic.services.settings_service import SettingsService
from settings.manager import ConfigManager
from settings.models import AppSettings

if TYPE_CHECKING:
    from pathlib import Path

_SIZE_ELEMENTS = 2  # Expected number of elements in size and position lists


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
def settings_service(temp_config_manager: ConfigManager[AppSettings]) -> SettingsService:
    """テスト用のSettingsServiceを作成

    Args:
        temp_config_manager: テスト用の設定マネージャー

    Returns:
        設定サービスのインスタンス
    """
    return SettingsService(temp_config_manager)


def test_get_all_settings(settings_service: SettingsService) -> None:
    """全設定取得のテスト"""
    settings = settings_service.get_all_settings()

    assert settings is not None
    assert hasattr(settings, "window")
    assert hasattr(settings, "user")
    assert hasattr(settings, "database")
    assert hasattr(settings, "agents")


def test_get_window_settings(settings_service: SettingsService) -> None:
    """ウィンドウ設定取得のテスト"""
    window_settings = settings_service.get_window_settings()

    assert window_settings is not None
    assert window_settings.size == [1280, 720]
    assert window_settings.position == [100, 100]


def test_get_user_settings(settings_service: SettingsService) -> None:
    """ユーザー設定取得のテスト"""
    user_settings = settings_service.get_user_settings()

    assert user_settings is not None
    assert user_settings.theme in {"light", "dark"}


def test_get_database_settings(settings_service: SettingsService) -> None:
    """データベース設定取得のテスト"""
    db_settings = settings_service.get_database_settings()

    assert db_settings is not None
    assert "sqlite" in db_settings.url


def test_get_agents_settings(settings_service: SettingsService) -> None:
    """エージェント設定取得のテスト"""
    agents_settings = settings_service.get_agents_settings()

    assert agents_settings is not None
    assert hasattr(agents_settings, "provider")


def test_get_setting_by_path(settings_service: SettingsService) -> None:
    """パス指定での設定取得のテスト"""
    theme = settings_service.get_setting_by_path("user.theme")
    assert theme in {"light", "dark"}

    size = settings_service.get_setting_by_path("window.size")
    assert isinstance(size, list)
    assert len(size) == _SIZE_ELEMENTS


def test_get_setting_by_invalid_path(settings_service: SettingsService) -> None:
    """不正なパスでの設定取得のテスト"""
    with pytest.raises(ValidationError, match="設定パスが見つかりません"):
        settings_service.get_setting_by_path("invalid.path")


def test_update_window_settings(settings_service: SettingsService) -> None:
    """ウィンドウ設定更新のテスト"""
    new_size = [1920, 1080]
    new_position = [200, 200]

    result = settings_service.update_window_settings(size=new_size, position=new_position)

    assert result.size == new_size
    assert result.position == new_position

    # 更新が永続化されているか確認
    window_settings = settings_service.get_window_settings()
    assert window_settings.size == new_size
    assert window_settings.position == new_position


def test_update_window_settings_invalid_size(settings_service: SettingsService) -> None:
    """不正なサイズでのウィンドウ設定更新のテスト"""
    with pytest.raises(ValidationError, match=r"サイズは.*2要素のリスト"):
        settings_service.update_window_settings(size=[1920])  # 1要素のみ


def test_update_window_settings_invalid_position(settings_service: SettingsService) -> None:
    """不正な位置でのウィンドウ設定更新のテスト"""
    with pytest.raises(ValidationError, match=r"位置は.*2要素のリスト"):
        settings_service.update_window_settings(position=[200])  # 1要素のみ


def test_update_user_settings(settings_service: SettingsService) -> None:
    """ユーザー設定更新のテスト"""
    original_theme = settings_service.get_user_settings().theme
    new_theme = "dark" if original_theme == "light" else "light"

    result = settings_service.update_user_settings(theme=new_theme, user_name="TestUser")

    assert result.theme == new_theme
    assert result.user_name == "TestUser"

    # 更新が永続化されているか確認
    user_settings = settings_service.get_user_settings()
    assert user_settings.theme == new_theme
    assert user_settings.user_name == "TestUser"


def test_update_user_settings_invalid_theme(settings_service: SettingsService) -> None:
    """不正なテーマでのユーザー設定更新のテスト"""
    with pytest.raises(ValidationError, match="テーマは'light'または'dark'"):
        settings_service.update_user_settings(theme="invalid")


def test_update_database_settings(settings_service: SettingsService) -> None:
    """データベース設定更新のテスト"""
    new_url = "sqlite:///test/path/test.db"

    result = settings_service.update_database_settings(url=new_url)

    assert result.url == new_url

    # 更新が永続化されているか確認
    db_settings = settings_service.get_database_settings()
    assert db_settings.url == new_url


def test_update_database_settings_empty_url(settings_service: SettingsService) -> None:
    """空のURLでのデータベース設定更新のテスト"""
    with pytest.raises(ValidationError, match="URLは空にできません"):
        settings_service.update_database_settings(url="")


def test_update_setting_by_path(settings_service: SettingsService) -> None:
    """パス指定での設定更新のテスト"""
    new_theme = "dark"
    result = settings_service.update_setting_by_path("user.theme", new_theme)

    assert result == new_theme

    # 更新が永続化されているか確認
    theme = settings_service.get_setting_by_path("user.theme")
    assert theme == new_theme


def test_update_setting_by_invalid_path(settings_service: SettingsService) -> None:
    """不正なパスでの設定更新のテスト"""
    with pytest.raises(ValidationError, match="設定パスは少なくとも2階層必要"):
        settings_service.update_setting_by_path("theme", "dark")


def test_load_settings_snapshot_contains_device(settings_service: SettingsService) -> None:
    snapshot = settings_service.load_settings_snapshot()

    assert snapshot["agent"]["device"] in {dev.value for dev in OpenVINODevice}


def test_save_settings_snapshot_updates_device(settings_service: SettingsService) -> None:
    snapshot = settings_service.load_settings_snapshot()
    snapshot["agent"]["device"] = OpenVINODevice.GPU.value

    settings_service.save_settings_snapshot(snapshot)

    updated = settings_service.load_settings_snapshot()
    assert updated["agent"]["device"] == OpenVINODevice.GPU.value
