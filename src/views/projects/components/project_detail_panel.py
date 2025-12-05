"""プロジェクト詳細パネルコンポーネント。"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

from views.theme import get_grey_color, get_on_primary_color, get_primary_color, get_surface_variant_color

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.projects.presenter import ProjectDetailVM


class ProjectDetailPanel(ft.Column):
    """プロジェクト詳細を表示するパネルコンポーネント。"""

    def __init__(
        self,
        project: ProjectDetailVM,
        *,
        on_edit: Callable[[ProjectDetailVM], None] | None = None,
        on_delete: Callable[[ProjectDetailVM], None] | None = None,
    ) -> None:
        """詳細パネルを初期化。

        Args:
            project: プロジェクト詳細ViewModel
            on_edit: 編集ボタンのコールバック
            on_delete: 削除ボタンのコールバック
        """
        self.project = project
        self.on_edit = on_edit
        self.on_delete = on_delete

        super().__init__(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                self._build_header(),
                                self._build_description(),
                                self._build_tasks(),
                            ],
                            spacing=20,
                        ),
                        padding=24,
                    ),
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_header(self) -> ft.Control:
        """ヘッダー部分を構築。

        Returns:
            ヘッダーコントロール
        """
        return ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            self.project.title,
                            theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{self.project.created_at} 作成",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_grey_color(600),
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                self.project.status,
                                theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                                color=get_on_primary_color(),
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=self.project.status_color,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=16,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="編集",
                            on_click=lambda _: self._handle_edit(),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            tooltip="削除",
                            on_click=lambda _: self._handle_delete(),
                        ),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

    def _build_description(self) -> ft.Control:
        """説明部分を構築。

        Returns:
            説明コントロール
        """
        return ft.Column(
            controls=[
                ft.Text(
                    "説明",
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    color=get_grey_color(500),
                ),
                ft.Text(
                    self.project.description,
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                ),
            ],
            spacing=8,
        )

    def _build_tasks(self) -> ft.Control:
        """関連タスク部分を構築。

        Returns:
            関連タスクコントロール
        """
        task_count = len(self.project.task_id) if self.project.task_id else 0

        if task_count == 0:
            tasks_display = ft.Text(
                "関連付けられたタスクはありません",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=get_grey_color(400),
                italic=True,
            )
        else:
            # タスクの完了数と進捗を計算
            completed = self.project.completed_count
            progress = completed / task_count if task_count > 0 else 0.0

            tasks_display = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.TASK_ALT,
                                size=20,
                                color=get_primary_color(),
                            ),
                            ft.Text(
                                f"{task_count} 件のタスク",
                                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Column(
                        controls=[
                            ft.ProgressBar(
                                value=progress,
                                color=get_primary_color(),
                                bgcolor=get_surface_variant_color(),
                                height=8,
                            ),
                            ft.Text(
                                f"{completed} / {task_count} 完了 ({progress:.0%})",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                color=get_grey_color(600),
                            ),
                        ],
                        spacing=6,
                    ),
                ],
                spacing=12,
            )

        return ft.Column(
            controls=[
                ft.Text(
                    "関連タスク",
                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                    color=get_grey_color(500),
                ),
                tasks_display,
            ],
            spacing=8,
        )

    def _handle_edit(self) -> None:
        """編集ハンドラ。"""
        from loguru import logger

        logger.debug(f"編集ボタンクリック: project_id={self.project.id}, on_edit={self.on_edit is not None}")
        if self.on_edit:
            self.on_edit(self.project)
        else:
            logger.warning("on_editコールバックが設定されていません")

    def _handle_delete(self) -> None:
        """削除ハンドラ。"""
        if self.on_delete:
            self.on_delete(self.project)

    def update_project(self, project: ProjectDetailVM) -> None:
        """プロジェクト詳細を更新。

        Args:
            project: 新しいプロジェクト詳細ViewModel
        """
        self.project = project
        self.controls = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            self._build_header(),
                            self._build_description(),
                            self._build_tasks(),
                        ],
                        spacing=20,
                    ),
                    padding=24,
                ),
            ),
        ]
        with contextlib.suppress(AssertionError):
            self.update()
