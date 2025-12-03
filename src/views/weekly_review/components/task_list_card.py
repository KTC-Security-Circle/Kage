"""週次レビューコンポーネント - タスクリストカード

タスクリスト表示用のカードコンポーネント。
"""

from collections.abc import Callable, Sequence
from contextlib import suppress
from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True, slots=True)
class TaskItemData:
    """タスク項目データ"""

    id: str
    title: str
    priority: str | None = None


@dataclass(frozen=True, slots=True)
class TaskListCardProps:
    """タスクリストカードのプロパティ"""

    title: str
    icon_name: str
    tasks: Sequence[TaskItemData]
    on_task_click: Callable[[str], None]
    on_show_more: Callable[[], None]
    max_display: int = 3


class TaskListCard(ft.Container):
    """タスクリスト表示カードコンポーネント"""

    def __init__(self, props: TaskListCardProps) -> None:
        """タスクリストカードを初期化

        Args:
            props: カードのプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()

    def _build_content(self) -> ft.Card:
        """カードコンテンツを構築

        Returns:
            構築されたカード
        """
        # ヘッダー
        header = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=self.props.icon_name,
                            size=16,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            self.props.title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(
                    content=ft.Text(
                        str(len(self.props.tasks)),
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PRIMARY,
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=12,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # タスクリスト
        task_items = []
        if len(self.props.tasks) == 0:
            task_items.append(
                ft.Container(
                    content=ft.Text(
                        "タスクなし",
                        size=14,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.padding.all(8),
                    alignment=ft.alignment.center,
                )
            )
        else:
            display_tasks = list(self.props.tasks)[: self.props.max_display]
            for task in display_tasks:
                # 優先度バッジ
                priority_badge = None
                if task.priority == "high":
                    priority_badge = ft.Container(
                        content=ft.Text(
                            "高",
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        bgcolor=ft.Colors.RED_400,
                        border_radius=8,
                    )

                # タスク行
                title_control = ft.Text(
                    task.title,
                    size=14,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                )
                controls_list: list[ft.Control] = [title_control]
                if priority_badge:
                    controls_list.append(priority_badge)

                task_row = ft.Container(
                    content=ft.Row(
                        controls=controls_list,
                        spacing=8,
                    ),
                    padding=ft.padding.all(8),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    ink=True,
                    on_click=lambda _e, task_id=task.id: self.props.on_task_click(task_id),
                )
                task_items.append(task_row)

            # "さらに表示" ボタン
            if len(self.props.tasks) > self.props.max_display:
                remaining = len(self.props.tasks) - self.props.max_display
                task_items.append(
                    ft.TextButton(
                        text=f"さらに {remaining} 件を表示",
                        on_click=lambda _: self.props.on_show_more(),
                        style=ft.ButtonStyle(
                            color=ft.Colors.PRIMARY,
                        ),
                        expand=True,
                    )
                )

        # カード内容
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(height=16),
                    ft.Column(
                        controls=task_items,
                        spacing=8,
                    ),
                ],
                spacing=12,
            ),
            padding=20,
        )

        return ft.Card(
            content=card_content,
            elevation=2,
        )

    def set_props(self, new_props: TaskListCardProps) -> None:
        """プロパティを更新してカードを再構築

        Args:
            new_props: 新しいプロパティ
        """
        self.props = new_props
        self.content = self._build_content()
        with suppress(Exception):
            self.update()
