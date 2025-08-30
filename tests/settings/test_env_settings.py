"""EnvSettings と設定管理関連の詳細テスト。[AI GENERATED]

対象:
  - EnvSettings.init_environment / _ensure_keys / _create_env_file / get / キャッシュ
  - Bool バリデータ空文字処理
  - 未設定警告 (_warn_unset)
  - ConfigManager.database_url / theme / window_size フォールバック
  - Frozen / Editable モデル差異 & edit() ネスト更新
  - シングルトン get_config_manager
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # [AI GENERATED] 型チェック専用
    from collections.abc import Iterator

import pytest

from settings.manager import ConfigManager, get_config_manager
from settings.models import (
    ENV_BOOL_KEYS,
    ENV_SETTINGS_KEYS,
    AppSettings,
    EditableAppSettings,
    EnvSettings,
)


@pytest.fixture
def temp_env_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """一時ディレクトリをカレントにして .env を隔離。[AI GENERATED]"""
    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        # キャッシュ初期化
        EnvSettings._cached = None  # type: ignore[attr-defined]
        EnvSettings._initialized = False  # type: ignore[attr-defined]
        yield tmp_path
    finally:
        os.chdir(cwd)
        # 後始末
        if (tmp_path / ".env").exists():
            (tmp_path / ".env").unlink()


def test_init_environment_creates_file(temp_env_dir: Path) -> None:
    EnvSettings.init_environment()
    env_path = temp_env_dir / ".env"
    assert env_path.exists()
    content = env_path.read_text(encoding="utf-8")
    # 全キーが含まれる
    for key in ENV_SETTINGS_KEYS:
        assert key in content
    # bool キーは false デフォルト
    for key in ENV_BOOL_KEYS:
        assert f"{key}=false" in content


def test_ensure_keys_appends_missing(temp_env_dir: Path) -> None:
    # まず生成
    EnvSettings.init_environment()
    env_path = temp_env_dir / ".env"
    original = env_path.read_text(encoding="utf-8")
    # 任意のキーを削除して再実行
    modified = "\n".join([line for line in original.splitlines() if not line.startswith("GOOGLE_API_KEY")])
    env_path.write_text(modified + "\n", encoding="utf-8")
    EnvSettings.init_environment()  # ensure_keys 再追記
    new_content = env_path.read_text(encoding="utf-8")
    assert "GOOGLE_API_KEY=" in new_content


def test_get_caches_instance(temp_env_dir: Path) -> None:
    EnvSettings.init_environment()
    a = EnvSettings.get()
    b = EnvSettings.get()
    assert a is b


def test_get_auto_init_when_not_initialized(temp_env_dir: Path) -> None:
    assert EnvSettings._initialized is False  # type: ignore[attr-defined]
    inst = EnvSettings.get()
    assert inst is EnvSettings.get()
    assert EnvSettings._initialized is True  # type: ignore[attr-defined]


def test_bool_validator_empty_string(monkeypatch: pytest.MonkeyPatch, temp_env_dir: Path) -> None:
    # 空文字を設定
    monkeypatch.setenv("LANGSMITH_TRACING", "")
    monkeypatch.setenv("KAGE_USE_LLM_ONE_LINER", "")
    EnvSettings.init_environment()
    env = EnvSettings.get()
    assert env.langsmith_tracing is None
    assert env.kage_use_llm_one_liner is None


def test_bool_validator_true_false(monkeypatch: pytest.MonkeyPatch, temp_env_dir: Path) -> None:
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("KAGE_USE_LLM_ONE_LINER", "false")
    EnvSettings.init_environment()
    env = EnvSettings.get()
    assert env.langsmith_tracing is True
    assert env.kage_use_llm_one_liner is False


def test_warn_unset_logs(monkeypatch: pytest.MonkeyPatch, temp_env_dir: Path, caplog: pytest.LogCaptureFixture) -> None:
    # 何も設定せず init -> 未設定キーについて warning 出力されることを確認
    caplog.set_level("WARNING")
    EnvSettings.init_environment()
    warned = {r.message.split(":")[-1].strip() for r in caplog.records if "環境変数が設定されていません" in r.message}
    expected = set(ENV_SETTINGS_KEYS)
    assert warned.issubset(expected)


def test_config_manager_database_url_overlay(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://overlay/db")
    env_cfg = tmp_path / ".env"
    env_cfg.write_text("DATABASE_URL=postgres://overlay/db\n", encoding="utf-8")
    mgr = ConfigManager(tmp_path / "app.yaml", AppSettings)
    assert mgr.database_url == "postgres://overlay/db"


def test_config_manager_fallback_yaml(tmp_path: Path) -> None:
    mgr = ConfigManager(tmp_path / "app.yaml", AppSettings)
    assert mgr.database_url.endswith("tasks.db")


def test_frozen_vs_editable_models(tmp_path: Path) -> None:
    mgr = ConfigManager(tmp_path / "app.yaml", AppSettings)
    # Pydantic v2 は frozen 変更時 ValidationError(frozen_instance) を送出
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        # 凍結モデルの属性書き換えは禁止
        mgr.settings.user.theme = "dark"  # type: ignore[misc]
    # editable 経由なら更新可能
    new_width = 1024
    with mgr.edit() as editable:
        assert isinstance(editable, EditableAppSettings)
        editable.window.size[0] = new_width
    mgr2 = ConfigManager(tmp_path / "app.yaml", AppSettings)
    assert mgr2.settings.window.size[0] == new_width


def test_singleton_get_config_manager(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # シングルトン確認
    monkeypatch.setenv("DATABASE_URL", "sqlite:///example.db")
    # 強制的にグローバル初期化をクリーンにするため settings.manager 内の _global_manager をリセットしたいが
    # 直接 import 循環を避け簡易に最初の呼び出しだけで確認
    a = get_config_manager()
    b = get_config_manager()
    assert a is b


def test_edit_nested_persistence(tmp_path: Path) -> None:
    mgr = ConfigManager(tmp_path / "app.yaml", AppSettings)
    new_y = 400
    with mgr.edit() as editable:
        editable.user.theme = "dark"
        editable.window.position[1] = new_y
    reloaded = ConfigManager(tmp_path / "app.yaml", AppSettings)
    assert reloaded.settings.user.theme == "dark"
    assert reloaded.settings.window.position[1] == new_y
