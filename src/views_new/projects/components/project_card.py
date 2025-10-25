"""プロジェクトカードコンポーネント

プロジェクト情報を表示するカードUIコンポーネント。
ステータスバッジ、説明、統計情報、アクションボタンを含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

from views_new.theme import get_status_color


def create_project_card(
    project: dict[str, str],
    on_edit: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
    on_delete: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
) -> ft.Control:  # type: ignore[name-defined]
    """プロジェクトカードを作成する。

    Args:
        project: プロジェクトデータ（id, name, description, status, tasks_count, created_at）
        on_edit: 編集ボタンクリック時のコールバック
        on_delete: 削除ボタンクリック時のコールバック

    Returns:
        プロジェクトカードコンポーネント
    """
    import flet as ft

    status_color = get_status_color(project["status"])

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    # Header row with title, description and status badge
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        project["name"],
                                        style=ft.TextThemeStyle.TITLE_MEDIUM,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        project["description"],
                                        style=ft.TextThemeStyle.BODY_MEDIUM,
                                        color=ft.colors.GREY_600,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                spacing=8,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    project["status"],
                                    style=ft.TextThemeStyle.LABEL_SMALL,
                                    color=ft.colors.WHITE,
                                    weight=ft.FontWeight.W_500,
                                ),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(
                                    horizontal=8,
                                    vertical=4,
                                ),
                                border_radius=ft.border_radius.all(12),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    # Divider
                    ft.Divider(
                        height=1,
                        color=ft.colors.GREY_300,
                    ),
                    # Footer with metadata and actions
                    ft.Row(
                        controls=[
                            # Task count
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.TASK_ALT,
                                        size=16,
                                        color=ft.colors.GREY_600,
                                    ),
                                    ft.Text(
                                        f"{project['tasks_count']} タスク",
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                        color=ft.colors.GREY_600,
                                    ),
                                ],
                                spacing=4,
                            ),
                            # Created date
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.CALENDAR_TODAY,
                                        size=16,
                                        color=ft.colors.GREY_600,
                                    ),
                                    ft.Text(
                                        project["created_at"],
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                        color=ft.colors.GREY_600,
                                    ),
                                ],
                                spacing=4,
                            ),
                            ft.Container(expand=True),  # Spacer
                            # Action buttons
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        tooltip="編集",
                                        icon_size=20,
                                        on_click=lambda e, p=project: on_edit(e, p),
                                        icon_color=ft.colors.GREY_600,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="削除",
                                        icon_size=20,
                                        on_click=lambda e, p=project: on_delete(e, p),
                                        icon_color=ft.colors.RED,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=16,
            ),
            padding=20,
        ),
        elevation=2,
    )
