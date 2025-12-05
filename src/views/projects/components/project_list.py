"""プロジェクトカードリストコンポーネント。"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

from views.projects.components.project_card import create_project_card_from_vm

from .empty_state import ProjectEmptyState

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.projects.presenter import ProjectCardVM


class ProjectCardList(ft.Column):
    """プロジェクトカードを一覧表示するリストコンポーネント。"""

    def __init__(
        self,
        projects: list[ProjectCardVM],
        *,
        on_select: Callable[[str], None] | None = None,
        selected_id: str | None = None,
        on_create: Callable[[], None] | None = None,
    ) -> None:
        """プロジェクトリストを初期化。

        Args:
            projects: 表示するプロジェクトのリスト
            on_select: プロジェクト選択時のコールバック
            selected_id: 選択中のプロジェクトID
            on_create: 新規作成ボタンのコールバック
        """
        self.projects = projects
        self.on_select = on_select
        self.selected_id = selected_id
        self.on_create = on_create

        super().__init__(
            controls=self._build_controls(),
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_controls(self) -> list[ft.Control]:
        """リストコントロールを構築。

        Returns:
            プロジェクトカードのリスト、または空の状態
        """
        if not self.projects:
            return [ProjectEmptyState(on_create=self.on_create)]

        cards: list[ft.Control] = []
        for project in self.projects:
            is_selected = self.selected_id == project.id
            # on_select が None の場合は空の関数を渡す
            on_select_handler = self.on_select if self.on_select else lambda _: None
            card = create_project_card_from_vm(
                vm=project,
                on_select=on_select_handler,
                is_selected=is_selected,
            )
            cards.append(card)
        return cards

    def update_projects(
        self,
        projects: list[ProjectCardVM],
        *,
        selected_id: str | None = None,
    ) -> None:
        """プロジェクトリストを更新。

        Args:
            projects: 新しいプロジェクトリスト
            selected_id: 選択中のプロジェクトID
        """
        self.projects = projects
        self.selected_id = selected_id
        self.controls = self._build_controls()
        with contextlib.suppress(AssertionError):
            self.update()
