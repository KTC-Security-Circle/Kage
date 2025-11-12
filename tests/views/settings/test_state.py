"""Tests for SettingsViewState to ensure deep copying of Pydantic models."""

import pytest
from settings.models import EditableUserSettings, EditableWindowSettings
from views.settings.state import SettingsSnapshot, SettingsViewState


def test_load_snapshot_creates_deep_copy():
    """load_snapshotメソッドがPydanticモデルの深いコピーを作成することを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")

    # Act
    state.load_snapshot(snapshot)

    # Assert - currentとoriginalは異なるPydanticインスタンスを持つべき
    assert state.current is not None
    assert state._original is not None
    assert state.current.appearance is snapshot.appearance  # currentは元のインスタンスを参照
    assert state._original.appearance is not snapshot.appearance  # originalは深いコピー
    assert state._original.window is not snapshot.window  # originalは深いコピー


def test_mark_as_saved_creates_deep_copy():
    """mark_as_savedメソッドがPydanticモデルの深いコピーを作成することを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")
    state.current = snapshot

    # Act
    state.mark_as_saved()

    # Assert - originalは深いコピーを持つべき
    assert state._original is not None
    assert state._original.appearance is not state.current.appearance
    assert state._original.window is not state.current.window


def test_has_unsaved_changes_detects_appearance_modifications():
    """appearanceフィールドの変更が正しく検出されることを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")
    state.load_snapshot(snapshot)

    # Act - currentのappearanceを変更
    assert not state.has_unsaved_changes  # 初期状態では変更なし
    state.current.appearance.theme = "dark"

    # Assert - 変更が検出されるべき
    assert state.has_unsaved_changes


def test_has_unsaved_changes_detects_window_modifications():
    """windowフィールドの変更が正しく検出されることを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")
    state.load_snapshot(snapshot)

    # Act - currentのwindowを変更
    assert not state.has_unsaved_changes  # 初期状態では変更なし
    state.current.window.size = [1920, 1080]

    # Assert - 変更が検出されるべき
    assert state.has_unsaved_changes


def test_has_unsaved_changes_after_mark_as_saved():
    """mark_as_saved後に変更フラグがリセットされることを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")
    state.load_snapshot(snapshot)
    state.current.appearance.theme = "dark"

    # Act
    assert state.has_unsaved_changes  # 変更あり
    state.mark_as_saved()

    # Assert - 保存後は変更なし
    assert not state.has_unsaved_changes


def test_multiple_modifications_are_independent():
    """複数回の変更が独立して扱われることを確認する。"""
    # Arrange
    state = SettingsViewState()
    appearance = EditableUserSettings(theme="light", user_name="Test User", last_login_user="test")
    window = EditableWindowSettings(size=[1280, 720], position=[100, 100])
    snapshot = SettingsSnapshot(appearance=appearance, window=window, database_url="sqlite:///test.db")
    state.load_snapshot(snapshot)

    # Act & Assert - 複数の変更
    state.current.appearance.theme = "dark"
    assert state.has_unsaved_changes
    assert state._original.appearance.theme == "light"  # originalは変更されていない

    state.current.window.size = [1920, 1080]
    assert state.has_unsaved_changes
    assert state._original.window.size == [1280, 720]  # originalは変更されていない
