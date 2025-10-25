"""タグカードコンポーネント

タグ情報を表示するカードUIコンポーネント。
色付きチップ、説明、統計情報、アクションボタンを含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


def create_tag_card(
    tag: dict[str, str],
    on_edit: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
    on_delete: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
) -> ft.Control:  # type: ignore[name-defined]
    """タグカードを作成する。

    Args:
        tag: タグデータ（id, name, color, description, task_count, created_at）
        on_edit: 編集ボタンクリック時のコールバック
        on_delete: 削除ボタンクリック時のコールバック

    Returns:
        タグカードコンポーネント
    """
    import flet as ft

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    # Header row with tag chip and actions
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    # Colored tag chip
                                    ft.Container(
                                        content=ft.Text(
                                            tag["name"],
                                            style=ft.TextThemeStyle.LABEL_MEDIUM,
                                            color=ft.colors.WHITE,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        bgcolor=tag["color"],
                                        padding=ft.padding.symmetric(
                                            horizontal=12,
                                            vertical=6,
                                        ),
                                        border_radius=ft.border_radius.all(16),
                                    ),
                                    # Description
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                tag["description"],
                                                style=ft.TextThemeStyle.BODY_MEDIUM,
                                                color=ft.colors.GREY_600,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=12,
                                expand=True,
                            ),
                            # Action buttons
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        tooltip="編集",
                                        icon_size=20,
                                        on_click=lambda e, t=tag: on_edit(e, t),
                                        icon_color=ft.colors.GREY_600,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="削除",
                                        icon_size=20,
                                        on_click=lambda e, t=tag: on_delete(e, t),
                                        icon_color=ft.colors.RED,
                                    ),
                                ],
                                spacing=0,
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
                    # Footer with metadata
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
                                        f"{tag['task_count']} タスク",
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
                                        tag["created_at"],
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                        color=ft.colors.GREY_600,
                                    ),
                                ],
                                spacing=4,
                            ),
                            ft.Container(expand=True),  # Spacer
                            # Color hex code
                            ft.Container(
                                content=ft.Text(
                                    tag["color"].upper(),
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.colors.GREY_600,
                                    weight=ft.FontWeight.W_500,
                                ),
                                padding=ft.padding.symmetric(
                                    horizontal=8,
                                    vertical=2,
                                ),
                                border=ft.border.all(1, ft.colors.GREY_300),
                                border_radius=ft.border_radius.all(4),
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
