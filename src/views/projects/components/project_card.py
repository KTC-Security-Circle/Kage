"""プロジェクトカードコンポーネント

プロジェクト情報を表示するカードUIコンポーネント。
ステータスバッジ、説明、統計情報、アクションボタンを含む。

共通カードコンポーネント（views.shared.components.card）を使用。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from views.shared.components import Card, CardActionData, CardBadgeData, CardData, CardMetadataData
from views.theme import (
    get_error_color,
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_status_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

    from views.projects.presenter import ProjectCardVM


def create_project_card(
    project: dict[str, Any],
    on_edit: Callable[[ft.ControlEvent, dict[str, Any]], None],
    on_delete: Callable[[ft.ControlEvent, dict[str, Any]], None],
) -> ft.Control:
    """プロジェクトカードを作成する（共通Cardコンポーネント使用）。

    Args:
        project: プロジェクトデータ（id, name, description, status, task_id, created_at）
        on_edit: 編集ボタンクリック時のコールバック
        on_delete: 削除ボタンクリック時のコールバック

    Returns:
        プロジェクトカードコンポーネント
    """
    import flet as ft

    # ステータス色はテーマに集約
    status_color = get_status_color(project["status"])

    # CardDataを構築
    card_data = CardData(
        title=project.get("title", project.get("name", "")),
        description=project["description"],
        badge=CardBadgeData(
            text=project["status"],
            color=status_color,
        ),
        metadata=[
            CardMetadataData(
                icon=ft.Icons.TASK_ALT,
                text=f"{len(project.get('task_id', []))} タスク",
            ),
            CardMetadataData(
                icon=ft.Icons.CALENDAR_TODAY,
                text=project["created_at"],
            ),
        ],
        actions=[
            CardActionData(
                icon=ft.Icons.EDIT_OUTLINED,
                tooltip="編集",
                on_click=lambda e, p=project: on_edit(e, p),
            ),
            CardActionData(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip="削除",
                on_click=lambda e, p=project: on_delete(e, p),
                icon_color=get_error_color(),
            ),
        ],
    )

    return Card(data=card_data)


def create_project_card_from_vm(
    vm: ProjectCardVM,  # type: ignore[name-defined]
    on_select: Callable[[str], None],
    *,
    is_selected: bool = False,
) -> ft.Control:  # type: ignore[name-defined]
    """ViewModel からプロジェクトカードを作成する。

    View の直書きを置き換え、再利用性を高めた統一インターフェース。

    Args:
        vm: プロジェクトカードViewModel
        on_select: カード選択時のコールバック (project_id を引数に取る)
        is_selected: 選択状態フラグ

    Returns:
        プロジェクトカードコンポーネント
    """
    import flet as ft

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                vm.title,
                                theme_style=ft.TextThemeStyle.TITLE_SMALL,
                                weight=ft.FontWeight.W_500,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    vm.status,
                                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                                    color=get_on_primary_color(),
                                    weight=ft.FontWeight.W_500,
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                bgcolor=vm.status_color,
                                border_radius=12,
                            ),
                        ],
                    ),
                    ft.Text(
                        vm.subtitle,
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=get_text_secondary_color(),
                    ),
                    ft.Text(
                        vm.description,
                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=get_text_secondary_color(),
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        vm.progress_text,
                                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                                        color=get_text_secondary_color(),
                                    ),
                                ],
                            ),
                            ft.ProgressBar(
                                value=vm.progress_value,
                                color=get_primary_color(),
                                bgcolor=get_outline_color(),
                                height=6,
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=8,
            ),
            padding=16,
            ink=True,
            on_click=lambda _: on_select(vm.id),
        ),
        elevation=1 if not is_selected else 3,
    )
