"""Settings View Controller Layer.

【責務】
    Controller層はユーザーイベントに応じた状態更新とサービス呼び出しを担当する。
    ユースケースの実行、State更新の調整を行う。

    - 設定値のロード（Serviceから取得→Snapshot生成→State更新）
    - 設定値の保存（State→Snapshot→Service保存）
    - 設定値のリセット（再ロード）
    - 設定値の更新（Snapshot再生成）
    - ランタイム設定の適用（テーマ、ウィンドウサイズ等）
    - エラーハンドリングと分類

【責務外（他層の担当）】
    - UI要素の構築・更新 → Presenter
    - 状態の保持 → State
    - UIレイアウトの決定 → View
    - データの永続化 → SettingsService
    - バリデーション → validation.py

【アーキテクチャ上の位置づけ】
    View → Controller → SettingsService
                ↓
              State

【主な機能】
    - load_settings: サービスから設定値を読み込んでSnapshotとしてStateに反映
    - save_settings: StateのSnapshotをサービス経由で保存
    - reset_settings: 保存済み設定値で State をリセット
    - update_xxx: 設定変更時のSnapshot再生成
    - apply_runtime_effects: ページへの設定適用（テーマ、ウィンドウサイズ）
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from errors import ValidationError
from logic.services.settings_service import SettingsService  # noqa: TC001 - Runtime dependency
from settings.models import EditableUserSettings, EditableWindowSettings

from .state import SettingsSnapshot, SettingsViewState
from .validation import validate_database_url, validate_theme, validate_window_size

if TYPE_CHECKING:
    from flet import Page


class SettingsError(Exception):
    """設定エラーの基底クラス。"""


class SettingsLoadError(SettingsError):
    """設定ロードエラー。"""


class SettingsSaveError(SettingsError):
    """設定保存エラー。"""


@dataclass(slots=True)
class SettingsController:
    """SettingsView 用の状態操作とサービス呼び出しを集約する。"""

    state: SettingsViewState
    service: SettingsService

    def load_settings(self) -> None:
        """現在の設定値を読み込んでStateに反映する。

        Raises:
            SettingsLoadError: 設定読み込みに失敗した場合
        """
        try:
            self.state.start_loading()
            self.state.set_error(None)

            # Serviceからスナップショット取得
            data = self.service.load_settings_snapshot()

            # Snapshot生成
            snapshot = SettingsSnapshot(
                appearance=EditableUserSettings(
                    theme=data["appearance"]["theme"],
                    user_name=data["appearance"]["user_name"],
                    last_login_user=data["appearance"]["last_login_user"],
                ),
                window=EditableWindowSettings(
                    size=data["window"]["size"],
                    position=data["window"]["position"],
                ),
                database_url=data["database_url"],
            )

            # Stateに反映
            self.state.load_snapshot(snapshot)

            logger.debug("設定値を読み込みました")

        except Exception as e:
            logger.error(f"設定値の読み込みに失敗しました: {e}")
            error_msg = f"設定の読み込みに失敗しました: {e}"
            self.state.set_error(error_msg)
            raise SettingsLoadError(error_msg) from e

        finally:
            self.state.stop_loading()

    def save_settings(self) -> None:
        """Stateの編集内容を保存する。

        Raises:
            SettingsSaveError: 設定保存に失敗した場合
        """
        if self.state.current is None:
            msg = "保存する設定がありません"
            raise SettingsSaveError(msg)

        try:
            self.state.start_loading()
            self.state.set_error(None)

            # バリデーション
            self._validate_current_settings()

            # Snapshotを辞書に変換
            snapshot_dict = {
                "appearance": {
                    "theme": self.state.current.appearance.theme,
                    "user_name": self.state.current.appearance.user_name,
                    "last_login_user": self.state.current.appearance.last_login_user,
                },
                "window": {
                    "size": self.state.current.window.size,
                    "position": self.state.current.window.position,
                },
                "database_url": self.state.current.database_url,
            }

            # Serviceで保存
            self.service.save_settings_snapshot(snapshot_dict)

            # Stateを保存済みとしてマーク
            self.state.mark_as_saved()
            logger.info("設定を保存しました")

        except ValidationError as e:
            logger.warning(f"設定のバリデーションエラー: {e}")
            error_msg = f"設定の検証に失敗しました: {e}"
            self.state.set_error(error_msg)
            raise SettingsSaveError(error_msg) from e

        except Exception as e:
            logger.error(f"設定の保存に失敗しました: {e}")
            error_msg = f"設定の保存に失敗しました: {e}"
            self.state.set_error(error_msg)
            raise SettingsSaveError(error_msg) from e

        finally:
            self.state.stop_loading()

    def reset_settings(self) -> None:
        """保存済み設定値でStateをリセットする。

        Raises:
            SettingsLoadError: 設定リセットに失敗した場合
        """
        try:
            self.load_settings()
            logger.debug("設定をリセットしました")

        except Exception as e:
            logger.error(f"設定のリセットに失敗しました: {e}")
            error_msg = f"設定のリセットに失敗しました: {e}"
            self.state.set_error(error_msg)
            raise SettingsLoadError(error_msg) from e

    def update_theme(self, theme: str) -> None:
        """テーマを更新する。

        Args:
            theme: 新しいテーマ値
        """
        if self.state.current is None:
            return

        new_appearance = replace(self.state.current.appearance, theme=theme)
        new_snapshot = replace(self.state.current, appearance=new_appearance)
        self.state.update_current(new_snapshot)

    def update_user_name(self, user_name: str) -> None:
        """ユーザー名を更新する。

        Args:
            user_name: 新しいユーザー名
        """
        if self.state.current is None:
            return

        new_appearance = replace(self.state.current.appearance, user_name=user_name)
        new_snapshot = replace(self.state.current, appearance=new_appearance)
        self.state.update_current(new_snapshot)

    def update_window_size(self, width: int, height: int) -> None:
        """ウィンドウサイズを更新する。

        Args:
            width: ウィンドウ幅
            height: ウィンドウ高さ
        """
        if self.state.current is None:
            return

        new_window = replace(self.state.current.window, size=[width, height])
        new_snapshot = replace(self.state.current, window=new_window)
        self.state.update_current(new_snapshot)

    def update_window_position(self, x: int, y: int) -> None:
        """ウィンドウ位置を更新する。

        Args:
            x: X座標
            y: Y座標
        """
        if self.state.current is None:
            return

        new_window = replace(self.state.current.window, position=[x, y])
        new_snapshot = replace(self.state.current, window=new_window)
        self.state.update_current(new_snapshot)

    def update_database_url(self, url: str) -> None:
        """データベースURLを更新する。

        Args:
            url: 新しいデータベースURL
        """
        if self.state.current is None:
            return

        new_snapshot = replace(self.state.current, database_url=url)
        self.state.update_current(new_snapshot)

    def apply_runtime_effects(self, page: Page) -> None:
        """ページに設定を適用する（ランタイム副作用）。

        Args:
            page: Fletページオブジェクト
        """
        if self.state.current is None:
            return

        try:
            # テーマの適用
            theme = self.state.current.appearance.theme
            if hasattr(page, "theme_mode"):
                page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT

            # ウィンドウサイズの適用（デスクトップアプリの場合）
            window_size = self.state.current.window.size
            if hasattr(page, "window") and hasattr(page.window, "width"):  # type: ignore[attr-defined]
                page.window.width = window_size[0]  # type: ignore[attr-defined]
                page.window.height = window_size[1]  # type: ignore[attr-defined]

            if hasattr(page, "update"):
                page.update()

            logger.debug("ランタイム設定を適用しました")

        except Exception as e:
            logger.warning(f"ランタイム設定の適用に失敗しました: {e}")

    def _validate_current_settings(self) -> None:
        """現在の設定値を検証する。

        Raises:
            ValidationError: バリデーションエラー
        """
        if self.state.current is None:
            msg = "設定値が存在しません"
            raise ValidationError(msg)

        # テーマの検証
        is_valid, error_msg = validate_theme(self.state.current.appearance.theme)
        if not is_valid:
            raise ValidationError(error_msg or "テーマが不正です")

        # ウィンドウサイズの検証
        size = self.state.current.window.size
        is_valid, error_msg = validate_window_size(size[0], size[1])
        if not is_valid:
            raise ValidationError(error_msg or "ウィンドウサイズが不正です")

        # データベースURLの検証
        is_valid, error_msg = validate_database_url(self.state.current.database_url)
        if not is_valid:
            raise ValidationError(error_msg or "データベースURLが不正です")
