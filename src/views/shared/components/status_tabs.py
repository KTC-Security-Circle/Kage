"""汎用ステータスタブコンポーネント。

任意のEnumステータスとカウントを表示するタブコンポーネント。
Projects、Memos、Terms等の各ビューで再利用可能。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TabDefinition[TStatus: Enum]:
    """単一タブの定義データ。

    Attributes:
        status: タブが表すステータス（None = 全件表示）
        label: タブのラベルテキスト
        icon: タブのアイコン名（オプション）
    """

    status: TStatus | None
    label: str
    icon: str | None = None


class StatusTabs[TStatus: Enum](ft.Container):
    """汎用ステータスタブコンポーネント。

    任意のEnumステータスを持つデータをフィルタリングするためのタブバーを提供。
    各タブにはカウントバッジが表示され、アクティブタブは強調表示される。
    """

    def __init__(
        self,
        *,
        tab_definitions: tuple[TabDefinition[TStatus], ...],
        on_tab_change: Callable[[TStatus | None], None] | None = None,
        active_status: TStatus | None = None,
        tab_counts: dict[TStatus, int] | None = None,
    ) -> None:
        """ステータスタブを初期化。

        Args:
            tab_definitions: タブ定義のタプル（順序固定）
            on_tab_change: タブ変更時のコールバック（ステータスを受け取る）
            active_status: 初期アクティブステータス（Noneの場合は最初のタブ）
            tab_counts: 各ステータスの件数マップ
        """
        self.tab_definitions = tab_definitions
        self.on_tab_change = on_tab_change
        self.active_status = active_status if active_status is not None else tab_definitions[0].status
        self.tab_counts = tab_counts or {}

        self._tab_containers: dict[TStatus | None, ft.Container] = {}
        self._count_badges: dict[TStatus | None, ft.Text] = {}

        super().__init__(
            content=self._build_tabs(),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(width=1, color=ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_tabs(self) -> ft.Control:
        """タブの行全体を構築する。"""
        row = ft.Row(spacing=4, expand=True)
        for definition in self.tab_definitions:
            tab_button = self._create_tab_button(definition)
            self._tab_containers[definition.status] = tab_button
            row.controls.append(tab_button)
        return row

    def _create_tab_button(self, definition: TabDefinition[TStatus]) -> ft.Container:
        """単一タブボタンを生成する。

        Args:
            definition: タブ定義データ

        Returns:
            タブボタンコンテナ
        """
        is_active = definition.status == self.active_status
        badge = self._build_count_badge(definition.status)

        controls: list[ft.Control] = []

        # アイコンがあれば追加
        if definition.icon:
            controls.append(ft.Icon(definition.icon, size=18))

        # ラベルテキスト
        label = ft.Text(
            definition.label,
            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
            size=14,
        )
        controls.append(label)

        # カウントバッジ
        controls.append(badge)

        return ft.Container(
            content=ft.Row(
                controls=controls,
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

    def _build_count_badge(self, status: TStatus | None) -> ft.Container:
        """ステータスごとの件数バッジを生成。

        Args:
            status: ステータス（None = 全件）

        Returns:
            カウントバッジコンテナ
        """
        # status=Noneの場合は全件合計、それ以外は個別カウント
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

    def _handle_click_factory(self, status: TStatus | None) -> Callable[[ft.ControlEvent], None]:
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
        for definition in self.tab_definitions:
            container = self._tab_containers.get(definition.status)
            if container:
                is_active = definition.status == self.active_status
                container.bgcolor = ft.Colors.SECONDARY_CONTAINER if is_active else ft.Colors.TRANSPARENT

                # ラベルの太さも更新
                if container.content and isinstance(container.content, ft.Row):
                    row_controls = container.content.controls
                    # アイコンがある場合はラベルはインデックス1、ない場合は0
                    label_index = 1 if definition.icon else 0
                    if len(row_controls) > label_index:
                        label_control = row_controls[label_index]
                        if isinstance(label_control, ft.Text):
                            label_control.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL

                with contextlib.suppress(AssertionError):
                    container.update()

    def update_counts(self, tab_counts: dict[TStatus, int]) -> None:
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

    def set_active(self, status: TStatus | None) -> None:
        """アクティブなステータスを設定。

        Args:
            status: アクティブにするステータス
        """
        if self.active_status != status:
            self.active_status = status
            self._update_active_states()
