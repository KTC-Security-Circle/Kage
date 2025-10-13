"""設定管理サービス

設定の読み取りと更新を行うドメインサービス
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from logic.services.base import ServiceBase
from settings.manager import ConfigManager, get_config_manager

if TYPE_CHECKING:
    from settings.models import (
        AgentsSettings,
        AppSettings,
        DatabaseSettings,
        UserSettings,
        WindowSettings,
    )

# Constants for validation
_POSITION_SIZE_ELEMENTS = 2
_MIN_PATH_DEPTH = 2


class SettingsService(ServiceBase):
    """設定管理サービス

    ConfigManagerを使用して設定の読み取りと更新を行う
    """

    def __init__(self, config_manager: ConfigManager[AppSettings] | None = None) -> None:
        """SettingsServiceの初期化

        Args:
            config_manager: 設定マネージャー。Noneの場合はグローバルインスタンスを使用
        """
        self._config_manager = config_manager or get_config_manager()

    @classmethod
    def build_service(cls) -> SettingsService:
        """SettingsServiceのインスタンスを生成するファクトリメソッド

        Returns:
            SettingsService: 設定管理サービスのインスタンス
        """
        return cls()

    def get_all_settings(self) -> AppSettings:
        """全設定を取得

        Returns:
            アプリケーション設定全体
        """
        logger.debug("全設定を取得")
        return self._config_manager.settings

    def get_window_settings(self) -> WindowSettings:
        """ウィンドウ設定を取得

        Returns:
            ウィンドウ設定
        """
        logger.debug("ウィンドウ設定を取得")
        return self._config_manager.settings.window

    def get_user_settings(self) -> UserSettings:
        """ユーザー設定を取得

        Returns:
            ユーザー設定
        """
        logger.debug("ユーザー設定を取得")
        return self._config_manager.settings.user

    def get_database_settings(self) -> DatabaseSettings:
        """データベース設定を取得

        Returns:
            データベース設定
        """
        logger.debug("データベース設定を取得")
        return self._config_manager.settings.database

    def get_agents_settings(self) -> AgentsSettings:
        """エージェント設定を取得

        Returns:
            エージェント設定
        """
        logger.debug("エージェント設定を取得")
        return self._config_manager.settings.agents

    def get_setting_by_path(self, path: str) -> Any:  # noqa: ANN401
        """パス指定で設定値を取得

        Args:
            path: ドット区切りの設定パス（例: "user.theme", "window.size"）

        Returns:
            設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.debug(f"設定を取得: {path}")
        parts = path.split(".")
        value: Any = self._config_manager.settings

        try:
            for part in parts:
                value = getattr(value, part)
        except AttributeError as e:
            msg = f"設定パスが見つかりません: {path}"
            raise ValueError(msg) from e
        else:
            return value

    def update_window_settings(
        self, size: list[int] | None = None, position: list[int] | None = None
    ) -> WindowSettings:
        """ウィンドウ設定を更新

        Args:
            size: ウィンドウサイズ [幅, 高さ]
            position: ウィンドウ位置 [X, Y]

        Returns:
            更新後のウィンドウ設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"ウィンドウ設定を更新: size={size}, position={position}")

        if size is not None and len(size) != _POSITION_SIZE_ELEMENTS:
            msg = "サイズは[幅, 高さ]の2要素のリストである必要があります"
            raise ValueError(msg)

        if position is not None and len(position) != _POSITION_SIZE_ELEMENTS:
            msg = "位置は[X, Y]の2要素のリストである必要があります"
            raise ValueError(msg)

        with self._config_manager.edit() as editable:
            if size is not None:
                editable.window.size = size
            if position is not None:
                editable.window.position = position

        return self._config_manager.settings.window

    def update_user_settings(
        self,
        last_login_user: str | None = None,
        theme: str | None = None,
        user_name: str | None = None,
    ) -> UserSettings:
        """ユーザー設定を更新

        Args:
            last_login_user: 最後にログインしたユーザー名
            theme: UIテーマ ('light' または 'dark')
            user_name: ユーザー表示名

        Returns:
            更新後のユーザー設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"ユーザー設定を更新: theme={theme}, user_name={user_name}")

        if theme is not None and theme not in {"light", "dark"}:
            msg = "テーマは'light'または'dark'である必要があります"
            raise ValueError(msg)

        with self._config_manager.edit() as editable:
            if last_login_user is not None:
                editable.user.last_login_user = last_login_user
            if theme is not None:
                editable.user.theme = theme
            if user_name is not None:
                editable.user.user_name = user_name

        return self._config_manager.settings.user

    def update_database_settings(self, url: str | None = None) -> DatabaseSettings:
        """データベース設定を更新

        Args:
            url: データベース接続URL

        Returns:
            更新後のデータベース設定

        Raises:
            ValueError: バリデーションエラー
        """
        logger.info(f"データベース設定を更新: url={url}")

        if url is not None and not url.strip():
            msg = "URLは空にできません"
            raise ValueError(msg)

        with self._config_manager.edit() as editable:
            if url is not None:
                editable.database.url = url

        return self._config_manager.settings.database

    def update_setting_by_path(self, path: str, value: Any) -> Any:  # noqa: ANN401
        """パス指定で設定値を更新

        Args:
            path: ドット区切りの設定パス（例: "user.theme", "window.size"）
            value: 設定する値

        Returns:
            更新後の設定値

        Raises:
            ValueError: パスが不正な場合
        """
        logger.info(f"設定を更新: {path} = {value}")
        parts = path.split(".")

        if len(parts) < _MIN_PATH_DEPTH:
            msg = f"設定パスは少なくとも2階層必要です: {path}"
            raise ValueError(msg)

        with self._config_manager.edit() as editable:
            obj: Any = editable
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)

        # 更新後の値を返す
        return self.get_setting_by_path(path)
