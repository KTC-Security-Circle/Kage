"""メモステータスタブコンポーネント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from models import MemoStatus

if TYPE_CHECKING:
    from collections.abc import Callable

_TabCounts = dict[MemoStatus, int]


# ========================================
# データモデル
# ========================================


@dataclass(frozen=True, slots=True)
class TabData:
    """単一タブの表示データ

    Attributes:
        status: タブのステータス
        label: タブのラベルテキスト
        icon: タブのアイコン名
        count: タブに表示する件数
        is_active: アクティブ状態
    """

    status: MemoStatus
    label: str
    icon: str
    count: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class StatusTabsData:
    """ステータスタブバー全体の表示データ

    Attributes:
        tabs: 各タブのデータリスト
        on_tab_change: タブ切り替え時のコールバック
    """

    tabs: tuple[TabData, ...]
    on_tab_change: Callable[[MemoStatus], None] | None = None


# ========================================
# 内部データモデル
# ========================================


@dataclass(slots=True)
class _TabDefinition:
    status: MemoStatus
    label: str
    icon: str


class MemoStatusTabs(ft.Container):
    """Inbox/Active/Idea/Archive を切り替えるタブバーを表現する。"""

    _TAB_DEFINITIONS: tuple[_TabDefinition, ...] = (
        _TabDefinition(status=MemoStatus.INBOX, label="Inbox", icon=ft.Icons.INBOX),
        _TabDefinition(status=MemoStatus.ACTIVE, label="アクティブ", icon=ft.Icons.AUTO_AWESOME),
        _TabDefinition(status=MemoStatus.IDEA, label="アイデア", icon=ft.Icons.LIGHTBULB),
        _TabDefinition(status=MemoStatus.ARCHIVE, label="アーカイブ", icon=ft.Icons.ARCHIVE),
    )
    _LABEL_INDEX = 1
    _MIN_CONTROL_COUNT = 2

    def __init__(
        self,
        *,
        on_tab_change: Callable[[MemoStatus], None] | None = None,
        active_status: MemoStatus = MemoStatus.INBOX,
        tab_counts: _TabCounts | None = None,
    ) -> None:
        """タブを初期化する。

        Args:
            on_tab_change: タブ切り替え時のコールバック
            active_status: 初期選択するタブのステータス
            tab_counts: タブごとの件数
        """
        self.on_tab_change = on_tab_change
        self.active_status = active_status
        self.tab_counts: _TabCounts = tab_counts or {}
        self._tab_containers: dict[MemoStatus, ft.Container] = {}
        self._count_badges: dict[MemoStatus, ft.Text] = {}

        super().__init__(
            content=self._build_tabs(),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_tabs(self) -> ft.Control:
        """タブの行全体を構築する。"""
        row = ft.Row(spacing=0, expand=True)
        for definition in self._TAB_DEFINITIONS:
            tab_button = self._create_tab_button(definition)
            self._tab_containers[definition.status] = tab_button
            row.controls.append(tab_button)
        return row

    def _create_tab_button(self, definition: _TabDefinition) -> ft.Container:
        """単一タブボタンを生成する（カウントバッジは常駐）。"""
        is_active = definition.status == self.active_status
        badge = self._build_count_badge(definition.status)

        label = ft.Text(
            definition.label,
            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
        )
        controls: list[ft.Control] = [ft.Icon(definition.icon, size=18), label, badge]

        return ft.Container(
            content=ft.Row(
                controls=controls,
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT,
            border_radius=8,
            ink=True,
            expand=True,
            on_click=self._handle_click_factory(definition.status),
        )

    def _build_count_badge(self, status: MemoStatus) -> ft.Container:
        """ステータスごとの件数バッジを生成（常駐）。"""
        count = self.tab_counts.get(status, 0)
        label = ft.Text(
            str(max(count, 0)),
            size=12,
            color=ft.Colors.ON_SECONDARY,
            weight=ft.FontWeight.BOLD,
        )
        self._count_badges[status] = label
        return ft.Container(
            content=label,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            bgcolor=ft.Colors.SECONDARY,
            border_radius=10,
            visible=count > 0,
        )

    def _handle_click_factory(self, status: MemoStatus) -> Callable[[ft.ControlEvent], None]:
        """クリックイベントハンドラを生成する。"""

        def _on_click(_: ft.ControlEvent) -> None:
            if status == self.active_status:
                return
            self.active_status = status
            self._apply_styles()
            if self.on_tab_change is not None:
                self.on_tab_change(status)

        return _on_click

    def update_counts(self, tab_counts: _TabCounts) -> None:
        """タブ件数を更新（値と可視状態のみ切替）。"""
        self.tab_counts = tab_counts
        for definition in self._TAB_DEFINITIONS:
            status = definition.status
            count = max(tab_counts.get(status, 0), 0)
            badge_text = self._count_badges.get(status)
            if badge_text is None:
                continue
            badge_text.value = str(count)
            parent = badge_text.parent
            if parent is not None:
                parent.visible = count > 0
                parent.update()
            badge_text.update()
        self._apply_styles()

    def set_active(self, status: MemoStatus) -> None:
        """アクティブタブを変更する。"""
        if status == self.active_status:
            return
        self.active_status = status
        self._apply_styles()

    def _apply_styles(self) -> None:
        """アクティブ状態に応じてタブのスタイルを更新する。"""
        for definition in self._TAB_DEFINITIONS:
            container = self._tab_containers.get(definition.status)
            if container is None:
                continue
            is_active = definition.status == self.active_status
            container.bgcolor = ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT
            if isinstance(container.content, ft.Row) and len(container.content.controls) >= self._MIN_CONTROL_COUNT:
                label = container.content.controls[self._LABEL_INDEX]
                if isinstance(label, ft.Text):
                    label.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
            container.update()
