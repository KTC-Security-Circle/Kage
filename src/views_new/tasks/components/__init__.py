"""タスク管理画面のコンポーネント

カンバンボード、タスクカード、アクションバーなどの再利用可能なUIコンポーネント。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

# タスクダイアログのインポート
from .task_dialog import create_task_dialog

# 定数定義
DESCRIPTION_MAX_LENGTH = 50

# コンポーネントの公開関数をエクスポート
__all__ = [
    "create_action_bar",
    "create_kanban_board",
    "create_task_card",
    "create_task_dialog",
]


def create_action_bar(
    on_create: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_search: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_filter: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_refresh: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
) -> ft.Container:  # type: ignore[name-defined]
    """アクションバーを作成する。

    Args:
        on_create: 新規作成ボタンのコールバック
        on_search: 検索のコールバック
        on_filter: フィルターボタンのコールバック
        on_refresh: 更新ボタンのコールバック

    Returns:
        アクションバーのコンテナ
    """
    import flet as ft

    return ft.Container(
        content=ft.Row(
            controls=[
                # 新規作成ボタン
                ft.ElevatedButton(
                    text="新規タスク",
                    icon=ft.Icons.ADD,
                    on_click=on_create,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        elevation=2,
                    ),
                ),
                # 検索ボックス
                ft.Container(
                    content=ft.TextField(
                        hint_text="タスクを検索...",
                        prefix_icon=ft.Icons.SEARCH,
                        border_radius=ft.border_radius.all(8),
                        on_change=on_search,
                        width=300,
                    ),
                    expand=True,
                ),
                # フィルターボタン
                ft.IconButton(
                    icon=ft.Icons.FILTER_LIST,
                    tooltip="フィルター",
                    on_click=on_filter,
                    style=ft.ButtonStyle(
                        icon_color=ft.Colors.GREY_700,
                        bgcolor=ft.Colors.GREY_100,
                    ),
                ),
                # 更新ボタン
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="更新",
                    on_click=on_refresh,
                    style=ft.ButtonStyle(
                        icon_color=ft.Colors.GREY_700,
                        bgcolor=ft.Colors.GREY_100,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.border_radius.all(8),
        border=ft.border.all(1, ft.Colors.GREY_300),
    )


def create_kanban_board(
    tasks_data: dict[str, list[dict[str, str]]],
    on_task_click: Callable[[ft.ControlEvent, dict[str, str]], None],  # type: ignore[name-defined]
) -> ft.Container:  # type: ignore[name-defined]
    """カンバンボードを作成する。

    Args:
        tasks_data: ステータス別のタスクデータ
        on_task_click: タスククリックのコールバック

    Returns:
        カンバンボードのコンテナ
    """
    import flet as ft

    columns = []

    for status, tasks in tasks_data.items():
        # ステータス列を作成
        column_cards = [
            create_task_card(
                task=task,
                on_click=lambda e, t=task: on_task_click(e, t),
            )
            for task in tasks
        ]

        column = ft.Container(
            content=ft.Column(
                controls=[
                    # ステータスヘッダー
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    status,
                                    style=ft.TextThemeStyle.TITLE_MEDIUM,
                                    color=ft.Colors.GREY_800,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        str(len(tasks)),
                                        color=ft.Colors.WHITE,
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=_get_status_color(status),
                                    border_radius=ft.border_radius.all(12),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    ),
                    # タスクカード一覧
                    ft.Container(
                        content=ft.Column(
                            controls=column_cards,
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=ft.padding.symmetric(horizontal=16),
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=ft.Colors.GREY_50,
            border_radius=ft.border_radius.all(8),
            border=ft.border.all(1, ft.Colors.GREY_300),
            width=350,
            expand=True,
        )

        columns.append(column)

    return ft.Container(
        content=ft.Row(
            controls=columns,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.START,
        ),
        expand=True,
    )


def create_task_card(
    task: dict[str, str],
    on_click: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
) -> ft.Container:  # type: ignore[name-defined]
    """タスクカードを作成する。

    Args:
        task: タスクデータ
        on_click: クリックのコールバック

    Returns:
        タスクカードのコンテナ
    """
    import flet as ft

    # 優先度カラーを取得
    priority_color = _get_priority_color(task.get("priority", "medium"))

    # タグのチップを作成
    tag_chips = []
    tags = task.get("tags", [])
    if isinstance(tags, list):
        tag_chips = [
            ft.Container(
                content=ft.Text(
                    tag,
                    size=10,
                    color=ft.Colors.BLUE_700,
                ),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )
            for tag in tags[:3]  # 最大3つまで表示
        ]

    # 説明文の処理
    description = task.get("description", "")
    truncated_description = description[:DESCRIPTION_MAX_LENGTH] + (
        "..." if len(description) > DESCRIPTION_MAX_LENGTH else ""
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                # 優先度インジケーター
                ft.Container(
                    height=4,
                    bgcolor=priority_color,
                    border_radius=ft.border_radius.vertical(top=4),
                ),
                # メインコンテンツ
                ft.Container(
                    content=ft.Column(
                        controls=[
                            control
                            for control in [
                                # タイトル
                                ft.Text(
                                    task.get("title", "無題"),
                                    style=ft.TextThemeStyle.TITLE_SMALL,
                                    color=ft.Colors.GREY_900,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                # 説明（最初の50文字）
                                ft.Text(
                                    truncated_description,
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.Colors.GREY_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                )
                                if truncated_description
                                else None,
                                # タグ
                                ft.Row(
                                    controls=tag_chips,
                                    spacing=4,
                                    wrap=True,
                                )
                                if tag_chips
                                else None,
                                # メタデータ（担当者、期限）
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.Icons.PERSON,
                                            size=16,
                                            color=ft.Colors.GREY_500,
                                        ),
                                        ft.Text(
                                            task.get("assignee", "未割当"),
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                            expand=True,
                                        ),
                                        ft.Icon(
                                            name=ft.Icons.SCHEDULE,
                                            size=16,
                                            color=ft.Colors.GREY_500,
                                        ),
                                        ft.Text(
                                            task.get("due_date", "未設定"),
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                    spacing=4,
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ]
                            if control is not None
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    padding=ft.padding.all(12),
                ),
            ],
            spacing=0,
            tight=True,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.border_radius.all(8),
        border=ft.border.all(1, ft.Colors.GREY_200),
        on_click=on_click,
        ink=True,
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
    )


def _get_status_color(status: str) -> str:
    """ステータスに対応する色を取得する。

    Args:
        status: ステータス名

    Returns:
        カラーコード
    """
    import flet as ft

    color_map = {
        "計画中": ft.Colors.BLUE_500,
        "進行中": ft.Colors.ORANGE_500,
        "完了": ft.Colors.GREEN_500,
        "保留": ft.Colors.GREY_500,
        "キャンセル": ft.Colors.RED_500,
    }
    return color_map.get(status, ft.Colors.GREY_500)


def _get_priority_color(priority: str) -> str:
    """優先度に対応する色を取得する。

    Args:
        priority: 優先度

    Returns:
        カラーコード
    """
    import flet as ft

    color_map = {
        "high": ft.Colors.RED_500,
        "medium": ft.Colors.ORANGE_500,
        "low": ft.Colors.GREEN_500,
    }
    return color_map.get(priority.lower(), ft.Colors.GREY_500)
