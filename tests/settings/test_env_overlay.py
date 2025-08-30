from typing import Protocol

from settings.manager import get_config_manager


class _MonkeyPatch(Protocol):  # minimal protocol for fixture
    def setenv(self, name: str, value: str) -> None: ...


def test_env_overlay_database_url(monkeypatch: _MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://env/db")
    mgr = get_config_manager()
    assert mgr.database_url == "postgres://env/db"
