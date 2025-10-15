"""TaskApplicationServiceの新機能（QuickAction、表示関連）の旧テストをスキップ"""

import pytest


@pytest.mark.skip(reason="旧QuickAction/表示APIは現行コードから削除済みのためスキップ")
def test_task_application_service_display_features_placeholder() -> None:  # pragma: no cover - placeholder
    assert True
