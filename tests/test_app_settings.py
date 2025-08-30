"""AppSettings / ConfigManager の基本動作テスト。"""

from pathlib import Path

from settings.manager import ConfigManager
from settings.models import AppSettings


def test_create_default_tmp_path(tmp_path: Path) -> None:
    """存在しないパスを渡すとデフォルト YAML が生成される。"""
    cfg_path = tmp_path / "app_config.yaml"
    mgr = ConfigManager(cfg_path, AppSettings)
    assert cfg_path.exists()
    assert mgr.settings.user.theme in {"light", "dark"}


def test_edit_persists_changes(tmp_path: Path) -> None:
    """edit コンテキストでの変更が保存され再読込される。"""
    cfg_path = tmp_path / "app_config.yaml"
    mgr = ConfigManager(cfg_path, AppSettings)
    original = mgr.settings.user.theme
    new_theme = "dark" if original == "light" else "light"
    with mgr.edit() as editable:
        editable.user.theme = new_theme
    # 変更が永続化されているか
    mgr2 = ConfigManager(cfg_path, AppSettings)
    assert mgr2.settings.user.theme == new_theme
