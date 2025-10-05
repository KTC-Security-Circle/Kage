"""設定管理 (YAML + .env) 統合モジュール。"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, cast

from loguru import logger
from pydantic import BaseModel
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from config import CONFIG_PATH
from settings.models import (
    AgentsSettings,
    AppSettings,
    DatabaseSettings,
    EditableAgentsSettings,
    EditableAppSettings,
    EditableDatabaseSettings,
    EditableUserSettings,
    EditableWindowSettings,
    EnvSettings,
    UserSettings,
    WindowSettings,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    import flet as ft


_FROZEN_TO_EDITABLE: dict[type[BaseModel], type[BaseModel]] = {
    WindowSettings: EditableWindowSettings,
    UserSettings: EditableUserSettings,
    DatabaseSettings: EditableDatabaseSettings,
    AgentsSettings: EditableAgentsSettings,
    AppSettings: EditableAppSettings,
}
_EDITABLE_TO_FROZEN = {v: k for k, v in _FROZEN_TO_EDITABLE.items()}


def _convert_model(obj: BaseModel, mapping: dict[type[BaseModel], type[BaseModel]]) -> BaseModel:
    target_cls = mapping.get(type(obj))
    if target_cls is None:
        return obj
    values: dict[str, object] = {}
    for name, value in obj.__dict__.items():
        if isinstance(value, BaseModel):
            values[name] = _convert_model(value, mapping)
        else:
            values[name] = value
    return target_cls.model_validate(values)


class ConfigManager[TSettings: BaseModel]:
    def __init__(self, path: str | Path, model_type: type[TSettings] = AppSettings) -> None:
        self._path = Path(path)
        self._model_type = model_type
        self._yaml = YAML()
        self._yaml.indent(mapping=2, sequence=4, offset=2)
        self._settings: TSettings = self._load_or_create()

    # 環境設定は都度 EnvSettings.get() / os.environ を参照し最新値を使うため固定キャッシュしない

    # --- properties -------------------------------------------------
    @property
    def settings(self) -> TSettings:
        return self._settings

    @property
    def env(self) -> EnvSettings:
        # 常に最新の環境変数状態を取得 (EnvSettings.get はキャッシュされるが init_environment で再評価される)
        return EnvSettings.get()

    @property
    def database_url(self) -> str:
        # 直接 os.environ の値を最優先し、なければ EnvSettings.get() 経由、それも無ければ設定ファイル値
        import os

        env_val = os.environ.get("DATABASE_URL")
        if env_val:
            return env_val
        env_settings = EnvSettings.get()
        return env_settings.database_url or cast("AppSettings", self._settings).database.url

    @property
    def theme(self) -> str:
        return cast("AppSettings", self._settings).user.theme

    @property
    def window_size(self) -> list[int]:
        return cast("AppSettings", self._settings).window.size

    # --- persistence ------------------------------------------------
    def _load_or_create(self) -> TSettings:
        if not self._path.exists():
            logger.info(f"設定ファイルが存在しません。デフォルトを作成します: {self._path}")
            default_obj = self._model_type()
            self._save_model(default_obj)
            return default_obj
        with self._path.open("r", encoding="utf-8") as rf:
            data = self._yaml.load(rf) or {}
        return self._model_type.model_validate(data)

    def _save_model(self, obj: TSettings) -> None:
        data_dict = obj.model_dump()
        # Enum を再帰的に値へ変換して YAML シリアライズ可能にする [AI GENERATED]
        from enum import Enum

        def convert(val: object) -> object:  # [AI GENERATED]
            if isinstance(val, Enum):
                return val.value
            if isinstance(val, dict):
                return {k: convert(v) for k, v in val.items()}
            if isinstance(val, list):
                return [convert(v) for v in val]
            return val

        data_dict = convert(data_dict)
        schema = self._model_type.model_json_schema()
        commented: object
        if isinstance(data_dict, dict):
            commented = self._to_commented_map(data_dict, schema.get("properties", {}))
            if self._model_type.__doc__ and hasattr(commented, "yaml_set_start_comment"):
                # CommentedMap のみがこの属性を持つ
                commented.yaml_set_start_comment(self._model_type.__doc__.strip())  # type: ignore[attr-defined]
        else:  # 異常ケース (念のため)
            commented = data_dict
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as wf:
            self._yaml.dump(commented, wf)
        logger.debug(f"設定を書き出しました: {self._path}")

    def _to_commented_map(
        self, data: dict, schema_props: dict
    ) -> CommentedMap | list | str | int | float | bool | None:
        if not isinstance(data, dict):
            return data
        cm = CommentedMap()
        for key, value in data.items():
            child_schema = schema_props.get(key, {})
            cm[key] = self._to_commented_map(value, child_schema.get("properties", {}))
            desc = child_schema.get("description")
            if desc:
                cm.yaml_set_comment_before_after_key(key, before=desc)
        return cm

    # --- edit context -----------------------------------------------
    @contextmanager
    def edit(self) -> Generator[EditableAppSettings, None, None]:
        editable = _convert_model(self._settings, _FROZEN_TO_EDITABLE)
        if not isinstance(editable, EditableAppSettings):
            msg = "EditableAppSettings への変換に失敗しました"
            raise TypeError(msg)
        try:
            yield editable
        finally:
            frozen_back = _convert_model(editable, _EDITABLE_TO_FROZEN)
            validated = self._model_type.model_validate(frozen_back.model_dump())
            self._save_model(validated)
            self._settings = validated
            logger.info(f"設定を保存しました: {self._path}")


# --- singleton ------------------------------------------------------
_global_manager: ConfigManager[AppSettings] | None = None


def get_config_manager() -> ConfigManager[AppSettings]:
    if _global_manager is None:
        EnvSettings.init_environment()
        manager = ConfigManager(CONFIG_PATH, AppSettings)
        globals()["_global_manager"] = manager
    return _global_manager  # type: ignore[return-value]


def apply_page_settings(page: ft.Page) -> None:
    mgr = get_config_manager()
    theme = mgr.theme
    try:
        import flet as ft  # ローカルインポート

        page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
    except (ImportError, AttributeError) as exc:
        logger.warning(f"Flet ページへの設定適用に失敗しました: {exc}")


__all__ = ["ConfigManager", "get_config_manager", "apply_page_settings", "EnvSettings"]
