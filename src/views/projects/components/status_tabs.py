"""プロジェクトステータスタブコンポーネント。"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from models import ProjectStatus

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(slots=True)
class _TabDefinition:
    """タブ定義データ。"""

    status: ProjectStatus | None
    label: str


class ProjectStatusTabs(ft.Container):
    """プロジェクトステータスタブを表示するコンポーネント。"""

    def __init__(
        self,
        *,
        on_tab_change: Callable[[ProjectStatus | None], None] | None = None,
        active_status: ProjectStatus | None = None,
        tab_counts: dict[ProjectStatus, int] | None = None,
    ) -> None:
        """ステータスタブを初期化。

        Args:
            on_tab_change: タブ変更時のコールバック（ステータスを直接受け取る）
            active_status: アクティブなステータス
            tab_counts: 各ステータスのカウント
        """
        self.on_tab_change = on_tab_change
        self.active_status = active_status
        self.tab_counts = tab_counts or {}

        # タブ定義（None = すべて）
        self._tab_definitions: tuple[_TabDefinition, ...] = (
            _TabDefinition(status=None, label="すべて"),
            _TabDefinition(status=ProjectStatus.ACTIVE, label=ProjectStatus.display_label(ProjectStatus.ACTIVE)),
            _TabDefinition(status=ProjectStatus.ON_HOLD, label=ProjectStatus.display_label(ProjectStatus.ON_HOLD)),
            _TabDefinition(status=ProjectStatus.COMPLETED, label=ProjectStatus.display_label(ProjectStatus.COMPLETED)),
            _TabDefinition(status=ProjectStatus.CANCELLED, label=ProjectStatus.display_label(ProjectStatus.CANCELLED)),
        )

        self._tab_containers: dict[ProjectStatus | None, ft.Container] = {}
        self._count_badges: dict[ProjectStatus | None, ft.Text] = {}

        super().__init__(
            content=self._build_tabs(),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_tabs(self) -> ft.Control:
        """タブの行全体を構築する。"""
        row = ft.Row(spacing=4, expand=True)
        for definition in self._tab_definitions:
            tab_button = self._create_tab_button(definition)
            self._tab_containers[definition.status] = tab_button
            row.controls.append(tab_button)
        return row

    def _create_tab_button(self, definition: _TabDefinition) -> ft.Container:
        """単一タブボタンを生成する。"""
        is_active = definition.status == self.active_status
        badge = self._build_count_badge(definition.status)

        label = ft.Text(
            definition.label,
            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
            size=14,
        )

        return ft.Container(
            content=ft.Row(
                controls=[label, badge],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT,
            border_radius=8,
            ink=True,
            expand=True,
            on_click=self._handle_click_factory(definition.status),
        )

    def _build_count_badge(self, status: ProjectStatus | None) -> ft.Container:
        """ステータスごとの件数バッジを生成。"""
        count = sum(self.tab_counts.values()) if status is None else self.tab_counts.get(status, 0)

        label = ft.Text(
            str(max(count, 0)),
            size=12,
            color=ft.Colors.ON_SECONDARY,
            weight=ft.FontWeight.BOLD,
        )
        self._count_badges[status] = label
        return ft.Container(
            content=label,
            bgcolor=ft.Colors.SECONDARY,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10,
        )

    def _handle_click_factory(self, status: ProjectStatus | None) -> Callable[[ft.ControlEvent], None]:
        """タブクリック時のコールバックファクトリ。

        Args:
            status: タブのステータス

        Returns:
            クリックハンドラ
        """

        def _on_click(_e: ft.ControlEvent) -> None:
            if self.active_status != status:
                self.active_status = status
                self._update_active_states()
                if self.on_tab_change:
                    self.on_tab_change(status)

        return _on_click

    def _update_active_states(self) -> None:
        """全タブのアクティブ状態を更新する。"""
        for definition in self._tab_definitions:
            container = self._tab_containers.get(definition.status)
            if container:
                is_active = definition.status == self.active_status
                container.bgcolor = ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT
                # ラベルの太さも更新
                if container.content and isinstance(container.content, ft.Row):
                    row_controls = container.content.controls
                    if row_controls and isinstance(row_controls[0], ft.Text):
                        row_controls[0].weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
                with contextlib.suppress(AssertionError):
                    container.update()

    def update_counts(self, tab_counts: dict[ProjectStatus, int]) -> None:
        """タブのカウントを更新。

        Args:
            tab_counts: 各ステータスのカウント
        """
        self.tab_counts = tab_counts
        # 各バッジの件数を更新
        for status, badge_text in self._count_badges.items():
            count = sum(tab_counts.values()) if status is None else tab_counts.get(status, 0)
            badge_text.value = str(max(count, 0))
            with contextlib.suppress(AssertionError):
                badge_text.update()

    def set_active(self, status: ProjectStatus | None) -> None:
        """アクティブなステータスを設定。

        Args:
            status: アクティブにするステータス
        """
        if self.active_status != status:
            self.active_status = status
            self._update_active_states()
