"""Settings View Controller Layer.

【責務】
    Controller層はユーザーイベントに応じた状態更新とサービス呼び出しを担当する。
    ユースケースの実行、State更新の調整を行う。

    - 設定値のロード
    - 設定値の保存
    - 設定値のリセット
    - 状態更新の調整
    - エラーハンドリング

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持 → State
    - UIレイアウトの決定 → View
    - データの永続化 → ConfigManager

【アーキテクチャ上の位置づけ】
    View → Controller → Query/ConfigManager
                ↓
              State

【主な機能】
    - load_settings: 現在の設定値を読み込んでStateに反映
    - save_settings: Stateの編集内容をConfigManagerで保存
    - reset_settings: 保存済み設定値でStateをリセット
    - on_setting_changed: 設定変更時の未保存フラグ更新
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from settings.manager import get_config_manager
from settings.models import (
    EditableDatabaseSettings,
    EditableUserSettings,
    EditableWindowSettings,
)

from .query import fetch_current_settings

if TYPE_CHECKING:
    from .state import SettingsViewState


@dataclass(slots=True)
class SettingsController:
    """SettingsView 用の状態操作とサービス呼び出しを集約する。"""

    state: SettingsViewState

    def load_settings(self) -> None:
        """現在の設定値を読み込んでStateに反映する。"""
        try:
            self.state.start_loading()
            self.state.set_error(None)

            current_data = fetch_current_settings()

            self.state.appearance_settings = current_data.appearance
            self.state.window_settings = current_data.window
            self.state.database_url = current_data.database_url
            self.state.mark_as_saved()

            logger.debug("設定値を読み込みました")

        except Exception as e:
            logger.error(f"設定値の読み込みに失敗しました: {e}")
            self.state.set_error(f"設定の読み込みに失敗しました: {e}")
            raise

        finally:
            self.state.stop_loading()

    def save_settings(self) -> None:
        """Stateの編集内容を保存する。"""
        try:
            self.state.start_loading()
            self.state.set_error(None)

            config_manager = get_config_manager()

            with config_manager.edit() as editable_settings:
                # Editable モデルを直接更新
                editable_settings.user = EditableUserSettings(
                    theme=self.state.appearance_settings.theme,
                    user_name=self.state.appearance_settings.user_name,
                    last_login_user=self.state.appearance_settings.last_login_user,
                )

                editable_settings.window = EditableWindowSettings(
                    size=self.state.window_settings.size.copy(),
                    position=self.state.window_settings.position.copy(),
                )

                editable_settings.database = EditableDatabaseSettings(
                    url=self.state.database_url,
                )

            self.state.mark_as_saved()
            logger.info("設定を保存しました")

        except Exception as e:
            logger.error(f"設定の保存に失敗しました: {e}")
            self.state.set_error(f"設定の保存に失敗しました: {e}")
            raise

        finally:
            self.state.stop_loading()

    def reset_settings(self) -> None:
        """保存済み設定値でStateをリセットする。"""
        try:
            self.load_settings()
            logger.debug("設定をリセットしました")

        except Exception as e:
            logger.error(f"設定のリセットに失敗しました: {e}")
            self.state.set_error(f"設定のリセットに失敗しました: {e}")

    def on_setting_changed(self) -> None:
        """設定が変更されたことをマークする。"""
        self.state.mark_as_changed()

    def update_theme(self, theme: str) -> None:
        """テーマを更新する。

        Args:
            theme: 新しいテーマ値
        """
        self.state.appearance_settings.theme = theme
        self.on_setting_changed()

    def update_user_name(self, user_name: str) -> None:
        """ユーザー名を更新する。

        Args:
            user_name: 新しいユーザー名
        """
        self.state.appearance_settings.user_name = user_name
        self.on_setting_changed()

    def update_window_size(self, width: int, height: int) -> None:
        """ウィンドウサイズを更新する。

        Args:
            width: ウィンドウ幅
            height: ウィンドウ高さ
        """
        self.state.window_settings.size = [width, height]
        self.on_setting_changed()

    def update_window_position(self, x: int, y: int) -> None:
        """ウィンドウ位置を更新する。

        Args:
            x: X座標
            y: Y座標
        """
        self.state.window_settings.position = [x, y]
        self.on_setting_changed()

    def update_database_url(self, url: str) -> None:
        """データベースURLを更新する。

        Args:
            url: 新しいデータベースURL
        """
        self.state.database_url = url
        self.on_setting_changed()
