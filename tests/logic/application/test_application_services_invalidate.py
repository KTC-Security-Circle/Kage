from __future__ import annotations

from agents.agent_conf import LLMProvider
from logic.application.apps import ApplicationServices
from logic.application.one_liner_application_service import OneLinerApplicationService
from logic.application.settings_application_service import SettingsApplicationService


class TestApplicationServicesInvalidate:
    def test_provider_reflects_after_invalidate(self) -> None:
        """設定変更後に invalidate_all() で再構築され、新しい設定が反映されること。"""
        # 初期状態
        settings_app = SettingsApplicationService.get_instance()  # type: ignore[assignment]
        # get_instance は BaseApplicationService を返す型定義なので具体型へ cast
        from typing import cast

        concrete_settings_app = cast("SettingsApplicationService", settings_app)
        before_provider = concrete_settings_app.get_agents_settings().provider

        apps = ApplicationServices.create()
        svc1 = apps.get_service(OneLinerApplicationService)
        assert isinstance(svc1, OneLinerApplicationService)
        assert getattr(svc1, "_provider", None) == before_provider

        # 設定を変更
        new_provider = LLMProvider.GOOGLE if before_provider != LLMProvider.GOOGLE else LLMProvider.OPENVINO
        concrete_settings_app.update_setting("agents.provider", new_provider)

        # invalidate → 再取得
        apps.invalidate_all()
        svc2 = apps.get_service(OneLinerApplicationService)
        assert isinstance(svc2, OneLinerApplicationService)
        assert getattr(svc2, "_provider", None) == new_provider

        # 念のため、古いインスタンスと異なることを確認（再構築された）
        assert svc1 is not svc2
