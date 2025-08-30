"""YAML ベース設定管理モジュール。

[AI GENERATED] `AppSettings` モデルを YAML ファイルへ保存/読込し、description をコメントとして保持する。
編集は `edit()` コンテキストマネージャ経由でのみ許可し不変性を担保する。
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from loguru import logger
from pydantic import BaseModel
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

if TYPE_CHECKING:
    from collections.abc import Generator

    import flet as ft  # 型チェック専用 (実行時は遅延インポート)

from config import CONFIG_PATH
from settings.models import (
    AppSettings,
    DatabaseSettings,
    EditableAppSettings,
    EditableDatabaseSettings,
    EditableUserSettings,
    EditableWindowSettings,
    UserSettings,
    WindowSettings,
)

TSettings = TypeVar("TSettings", bound=BaseModel)
TEditableSettings = TypeVar("TEditableSettings", bound=BaseModel)


_FROZEN_TO_EDITABLE: dict[type[BaseModel], type[BaseModel]] = {
    WindowSettings: EditableWindowSettings,
    UserSettings: EditableUserSettings,
    DatabaseSettings: EditableDatabaseSettings,
    AppSettings: EditableAppSettings,
}
_EDITABLE_TO_FROZEN = {v: k for k, v in _FROZEN_TO_EDITABLE.items()}


def _convert_model(obj: BaseModel, mapping: dict[type[BaseModel], type[BaseModel]]) -> BaseModel:
    """[AI GENERATED] モデルを別型へ再帰変換するヘルパ。

    - mapping に存在する型は対応する型へ再構築
    - BaseModel フィールドは再帰処理
    - それ以外は値をそのまま利用
    """
    target_cls = mapping.get(type(obj))
    if target_cls is None:  # マッピングされていない型はそのまま
        return obj
    values: dict[str, object] = {}
    for name, value in obj.__dict__.items():
        if isinstance(value, BaseModel):  # ネスト再帰
            values[name] = _convert_model(value, mapping)
        else:
            values[name] = value
    return target_cls.model_validate(values)


class ConfigManager(Generic[TSettings]):
    """汎用設定マネージャ。

    Args:
        path: 設定ファイルパス
        model_type: ルート設定モデル型
    """

    def __init__(self, path: str | Path, model_type: type[TSettings] = AppSettings) -> None:
        self._path = Path(path)
        self._model_type = model_type
        self._yaml = YAML()
        self._yaml.indent(mapping=2, sequence=4, offset=2)
        self._settings: TSettings = self._load_or_create()

    @property
    def settings(self) -> TSettings:  # [AI GENERATED] 外部からは読み取り専用
        """現在ロードされている読み取り専用設定モデルを返す。"""
        return self._settings

    # -- persistence -------------------------------------------------
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
        schema = self._model_type.model_json_schema()
        commented = self._to_commented_map(data_dict, schema.get("properties", {}))

        # 先頭コメント: ruamel の型が静的解析で拾えないため getattr 経由
        if self._model_type.__doc__ and hasattr(commented, "yaml_set_start_comment"):
            commented.yaml_set_start_comment(self._model_type.__doc__.strip())  # type: ignore[attr-defined]

        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as wf:
            self._yaml.dump(commented, wf)
        logger.debug(f"設定を書き出しました: {self._path}")

    def _to_commented_map(
        self, data: dict, schema_props: dict
    ) -> CommentedMap | list | str | int | float | bool | None:
        """再帰的に `dict` をコメント付き構造へ変換する。"""
        if not isinstance(data, dict):  # [AI GENERATED] プリミティブはそのまま返す
            return data
        cm = CommentedMap()
        for key, value in data.items():
            child_schema = schema_props.get(key, {})
            cm[key] = self._to_commented_map(value, child_schema.get("properties", {}))
            desc = child_schema.get("description")
            if desc:
                # ruamel.yaml API: yaml_set_comment_before_after_key(key, before=..., after=...)
                cm.yaml_set_comment_before_after_key(key, before=desc)
        return cm

    # -- edit context ------------------------------------------------
    @contextmanager
    def edit(self) -> Generator[EditableAppSettings, None, None]:
        """設定編集用コンテキスト。

        Frozen モデルを Editable に再帰変換し、編集後に再度 Frozen に戻して保存する。
        """
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


# -- シングルトンアクセサ ----------------------------------------------
_global_manager: ConfigManager[AppSettings] | None = None


def get_config_manager() -> ConfigManager[AppSettings]:
    """アプリ全体で共有する設定マネージャを取得する。"""
    if _global_manager is None:
        manager = ConfigManager(CONFIG_PATH, AppSettings)
        # グローバル変数へ代入 (関数外で宣言済み)
        globals()["_global_manager"] = manager
    return _global_manager  # type: ignore[return-value]


def apply_page_settings(page: ft.Page) -> None:
    """Flet Page に設定を適用するヘルパ。

    現状はテーマのみ。必要に応じて window サイズ/位置の適用を追加する。
    """
    mgr = get_config_manager()
    theme = mgr.settings.user.theme
    try:
        import flet as ft  # ローカルインポートで起動コストを下げる

        page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
    except (ImportError, AttributeError) as exc:
        logger.warning(f"Flet ページへの設定適用に失敗しました: {exc}")
        logger.warning("Flet ページへの設定適用に失敗しました。")


__all__ = ["ConfigManager", "get_config_manager", "apply_page_settings"]
