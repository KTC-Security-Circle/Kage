"""プロジェクト詳細パネルコンポーネント。"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import flet as ft

from views.theme import (
    get_on_primary_color,
    get_outline_color,
    get_success_color,
    get_surface_variant_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.projects.presenter import ProjectDetailVM, TaskItemVM


class ProjectDetailPanel(ft.Column):
    """プロジェクト詳細を表示するパネルコンポーネント。"""

    def __init__(
        self,
        project: ProjectDetailVM,
        *,
        on_edit: Callable[[ProjectDetailVM], None] | None = None,
        on_delete: Callable[[ProjectDetailVM], None] | None = None,
        on_task_select: Callable[[str], None] | None = None,
    ) -> None:
        """詳細パネルを初期化。

        Args:
            project: プロジェクト詳細ViewModel
            on_edit: 編集ボタンのコールバック
            on_delete: 削除ボタンのコールバック
            on_task_select: タスク選択コールバック（タスクIDを受け取る）
        """
        self.project = project
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_task_select = on_task_select

        super().__init__(
            controls=[
                self._build_info_card(),
                self._build_tasks_card(),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_info_card(self) -> ft.Card:
        """基本情報カードを構築。

        Returns:
            基本情報カード
        """
        controls_list = [
            self._build_header(),
            self._build_description(),
        ]

        # 期限がある場合は期限セクションを追加
        if self.project.due_date:
            controls_list.append(self._build_due_date())

        controls_list.extend(
            [
                self._build_progress(),
                self._build_edit_button(),
            ]
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=controls_list,
                    spacing=16,
                ),
                padding=20,
            ),
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
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=get_text_secondary_color(),
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text(
                        self.project.status,
                        theme_style=ft.TextThemeStyle.LABEL_SMALL,
                        color=get_on_primary_color(),
                        weight=ft.FontWeight.W_500,
                    ),
                    bgcolor=self.project.status_color,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=16,
                ),
            ],
        )

    def _build_description(self) -> ft.Column:
        """説明セクションを構築。

        Returns:
            説明セクション
        """
        return ft.Column(
            controls=[
                ft.Text(
                    "説明",
                    size=14,
                    color=get_text_secondary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    self.project.description,
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                ),
            ],
            spacing=8,
        )

    def _build_due_date(self) -> ft.Column:
        """期限セクションを構築。

        Returns:
            期限セクション
        """
        return ft.Column(
            controls=[
                ft.Text(
                    "期限",
                    size=14,
                    color=get_text_secondary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.EVENT,
                            size=18,
                            color=get_text_secondary_color(),
                        ),
                        ft.Text(
                            self.project.due_date or "未設定",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        )

    def _build_progress(self) -> ft.Column:
        """進捗セクションを構築。

        Returns:
            進捗セクション
        """
        task_count = len(self.project.task_id) if self.project.task_id else 0
        completed = self.project.completed_count
        progress = completed / task_count if task_count > 0 else 0.0

        return ft.Column(
            controls=[
                ft.Text(
                    "進捗",
                    size=14,
                    color=get_text_secondary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                ft.Column(
                    controls=[
                        ft.ProgressBar(
                            value=progress,
                            color=get_success_color(),
                            bgcolor=get_surface_variant_color(),
                            height=12,
                            border_radius=6,
                        ),
                        ft.Text(
                            f"{progress:.0%} 完了 ({completed} / {task_count} タスク)",
                            size=14,
                            color=get_text_secondary_color(),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        )

    def _build_edit_button(self) -> ft.Control:
        """編集ボタンを構築。

        Returns:
            編集ボタン
        """
        return ft.Container(
            content=ft.ElevatedButton(
                text="編集",
                icon=ft.Icons.EDIT,
                on_click=lambda _: self._handle_edit(),
                expand=True,
            ),
            padding=ft.padding.only(top=4),
        )

    def _build_tasks_card(self) -> ft.Card:
        """タスク一覧カードを構築。

        Returns:
            タスク一覧カード
        """
        task_count = len(self.project.task_id) if self.project.task_id else 0

        if task_count == 0:
            content = ft.Container(
                content=ft.Text(
                    "タスクはありません",
                    color=get_text_secondary_color(),
                ),
                padding=ft.padding.symmetric(vertical=20),
                alignment=ft.alignment.center,
            )
        else:
            task_items = [self._create_task_item(task) for task in self.project.tasks]
            content = ft.Column(
                controls=task_items,
                spacing=8,
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "タスク一覧",
                                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"このプロジェクトに含まれるタスク ({task_count}件)",
                                    size=13,
                                    color=get_text_secondary_color(),
                                ),
                            ],
                            spacing=4,
                        ),
                        content,
                    ],
                    spacing=16,
                ),
                padding=20,
            ),
        )

    def _create_task_item(self, task: TaskItemVM) -> ft.Container:
        """タスク項目を作成。

        Args:
            task: タスクViewModel

        Returns:
            タスク項目コンテナ
        """

        def on_task_click(_: ft.ControlEvent) -> None:
            if self.on_task_select:
                self.on_task_select(str(task.id))

        status_badge = None
        if task.is_completed:
            status_badge = ft.Container(
                content=ft.Text(
                    "完了",
                    size=11,
                    weight=ft.FontWeight.W_500,
                ),
                bgcolor=get_surface_variant_color(),
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=4,
            )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        task.title,
                                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                    ),
                                    status_badge,
                                ]
                                if status_badge
                                else [
                                    ft.Text(
                                        task.title,
                                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        icon_size=18,
                        tooltip="タスクを表示",
                        on_click=on_task_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=12,
            border=ft.border.all(1, get_outline_color()),
            border_radius=8,
            ink=True,
            on_click=on_task_click,
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
            self._build_info_card(),
            self._build_tasks_card(),
        ]
        with contextlib.suppress(AssertionError):
            self.update()
