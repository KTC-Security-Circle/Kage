"""LLMエージェント設定セクション。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from agents.agent_conf import LLMProvider, OpenVINODevice
from settings.models import AgentDetailLevel
from views.theme import SPACING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class LLMRuntimeFormValues:
    temperature: float
    debug_mode: bool
    device: str


@dataclass(frozen=True, slots=True)
class PromptFormValues:
    instructions: str
    detail_level: str


class AgentSection(ft.Column):
    """LLMエージェント設定を編集するセクション。"""

    def __init__(self, on_change: Callable[[], None]) -> None:
        super().__init__()
        self.on_change = on_change

        provider_options = [
            ft.dropdown.Option(key=provider.value, text=provider.name.title()) for provider in LLMProvider
        ]

        self.provider_dropdown = ft.Dropdown(
            label="LLMプロバイダ",
            options=provider_options,
            value=LLMProvider.FAKE.value,
            on_change=self._handle_provider_change,
            expand=True,
        )

        self.model_field = ft.TextField(
            label="モデル名",
            hint_text="例: gemini-2.0-flash",
            on_change=self._handle_change,
            expand=True,
        )

        self.temperature_slider = ft.Slider(
            min=0.0,
            max=1.0,
            divisions=10,
            value=0.2,
            label="{value:.1f}",
            on_change=self._handle_change,
        )

        self.debug_switch = ft.Switch(
            label="デバッグモード",
            value=False,
            on_change=self._handle_change,
        )

        self.device_dropdown = ft.Dropdown(
            label="実行デバイス (OpenVINO)",
            options=[ft.dropdown.Option(key=device.value, text=device.name) for device in OpenVINODevice],
            value="CPU",
            on_change=self._handle_change,
            expand=True,
        )
        self.device_container = ft.Column(
            controls=[
                ft.Text("OpenVINO デバイス", size=14, weight=ft.FontWeight.BOLD),
                self.device_dropdown,
            ],
            spacing=4,
            visible=False,
        )

        detail_options = [
            ft.dropdown.Option(key=level.value, text=self._detail_level_label(level)) for level in AgentDetailLevel
        ]

        self.memo_prompt_field = ft.TextField(
            label="MemoToTask カスタム指示",
            hint_text="追加したい指示があれば入力",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=self._handle_change,
        )
        self.memo_detail_dropdown = ft.Dropdown(
            label="MemoToTask 生成粒度",
            options=detail_options,
            value=AgentDetailLevel.BALANCED.value,
            on_change=self._handle_change,
            expand=True,
        )

        self.review_prompt_field = ft.TextField(
            label="レビュー カスタム指示",
            hint_text="レビュー構成への追加指示",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=self._handle_change,
        )
        self.review_detail_dropdown = ft.Dropdown(
            label="レビュー生成粒度",
            options=detail_options,
            value=AgentDetailLevel.BALANCED.value,
            on_change=self._handle_change,
            expand=True,
        )

        self.controls = [
            ft.Text("LLM 設定", size=16, weight=ft.FontWeight.BOLD),
            self.provider_dropdown,
            ft.Text("モデル", size=14, weight=ft.FontWeight.BOLD),
            self.model_field,
            ft.Text("温度", size=14, weight=ft.FontWeight.BOLD),
            self.temperature_slider,
            self.device_container,
            self.debug_switch,
            ft.Divider(),
            ft.Text("MemoToTask プロンプト", size=16, weight=ft.FontWeight.BOLD),
            self.memo_prompt_field,
            self.memo_detail_dropdown,
            ft.Divider(),
            ft.Text("レビュー プロンプト", size=16, weight=ft.FontWeight.BOLD),
            self.review_prompt_field,
            self.review_detail_dropdown,
        ]
        self.spacing = SPACING.md

    def set_values(
        self,
        *,
        provider: str,
        model: str | None,
        runtime: LLMRuntimeFormValues,
        memo_prompt: PromptFormValues,
        review_prompt: PromptFormValues,
    ) -> None:
        self.provider_dropdown.value = provider
        self._update_device_visibility(provider)
        self.model_field.value = model or ""
        self.temperature_slider.value = float(max(0.0, min(1.0, runtime.temperature)))
        self.debug_switch.value = runtime.debug_mode
        self.device_dropdown.value = runtime.device or "CPU"
        self.memo_prompt_field.value = memo_prompt.instructions
        self.memo_detail_dropdown.value = memo_prompt.detail_level or AgentDetailLevel.BALANCED.value
        self.review_prompt_field.value = review_prompt.instructions
        self.review_detail_dropdown.value = review_prompt.detail_level or AgentDetailLevel.BALANCED.value
        if self.page:
            self.update()

    @property
    def device_value(self) -> str:
        return self.device_dropdown.value or "CPU"

    def _handle_change(self, _: ft.ControlEvent) -> None:
        self.on_change()

    def _handle_provider_change(self, _: ft.ControlEvent) -> None:
        self._update_device_visibility(self.provider_dropdown.value)
        self.on_change()

    def _update_device_visibility(self, provider_value: str | None) -> None:
        is_openvino = provider_value == LLMProvider.OPENVINO.value
        self.device_container.visible = is_openvino
        if self.page:
            self.update()

    @staticmethod
    def _detail_level_label(level: AgentDetailLevel) -> str:
        labels = {
            AgentDetailLevel.BRIEF: "簡潔 (brief)",
            AgentDetailLevel.BALANCED: "標準 (balanced)",
            AgentDetailLevel.DETAILED: "詳細 (detailed)",
        }
        return labels.get(level, level.value)
