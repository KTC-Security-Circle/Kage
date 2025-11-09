"""プロジェクト作成・編集ダイアログコンポーネント

美しい見た目を重視したシンプルなダイアログ実装。
保存機能は後で実装予定のため、UIの見た目とユーザビリティに焦点を当てる。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


def show_create_project_dialog(
    page: ft.Page,  # type: ignore[name-defined]
    on_save: Callable[[dict[str, str]], None] | None = None,
) -> None:
    """美しい新規プロジェクト作成ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        on_save: 保存時のコールバック関数
    """
    import flet as ft

    # フォームフィールドを作成
    name_field = ft.TextField(
        label="プロジェクト名",
        hint_text="例: ウェブサイトリニューアル",
        prefix_icon=ft.Icons.WORK,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        max_length=80,
        counter_text="",
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="プロジェクトの詳細を入力してください",
        prefix_icon=ft.Icons.DESCRIPTION,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        multiline=True,
        max_lines=3,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value="進行中",
        prefix_icon=ft.Icons.FLAG,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        options=[
            ft.dropdown.Option("進行中", "進行中"),
            ft.dropdown.Option("計画中", "計画中"),
            ft.dropdown.Option("完了", "完了"),
            ft.dropdown.Option("保留", "保留"),
        ],
    )

    priority_dropdown = ft.Dropdown(
        label="優先度",
        value="標準",
        prefix_icon=ft.Icons.PRIORITY_HIGH,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        options=[
            ft.dropdown.Option("低", "低"),
            ft.dropdown.Option("標準", "標準"),
            ft.dropdown.Option("高", "高"),
        ],
    )

    def close_dialog(_: ft.ControlEvent) -> None:
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_project(_: ft.ControlEvent) -> None:
        """プロジェクト保存処理"""
        # プロジェクトデータを作成
        project_data = {
            "id": f"project_{hash(name_field.value or 'new')}",  # 仮のID生成
            "name": name_field.value or "新しいプロジェクト",
            "description": description_field.value or "",
            "status": status_dropdown.value or "進行中",
            "priority": priority_dropdown.value or "標準",
        }

        # コールバック関数を呼び出してデータを親に渡す
        if on_save:
            on_save(project_data)

        close_dialog(_)

    # 美しいダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.BLUE_600, size=28),
                ft.Text(
                    "新しいプロジェクト",
                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=ft.Colors.BLUE_700,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=12,
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    # 説明テキスト
                    ft.Container(
                        content=ft.Text(
                            "新しいプロジェクトの詳細を入力してください",
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.GREY_600,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    name_field,
                    description_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=True),
                            ft.Container(content=priority_dropdown, expand=True),
                        ],
                        spacing=16,
                    ),
                    # 注意書き
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_400, size=16),
                                ft.Text(
                                    "プロジェクト名は必須項目です",
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.Colors.BLUE_600,
                                ),
                            ],
                            spacing=8,
                        ),
                        margin=ft.margin.only(top=12),
                    ),
                ],
                spacing=16,
                tight=True,
            ),
            width=520,
            padding=ft.padding.all(8),
        ),
        actions=[
            ft.Row(
                controls=[
                    ft.TextButton(
                        text="キャンセル",
                        icon=ft.Icons.CLOSE,
                        on_click=close_dialog,
                        style=ft.ButtonStyle(color=ft.Colors.GREY_600),
                    ),
                    ft.ElevatedButton(
                        text="作成",
                        icon=ft.Icons.ADD,
                        on_click=save_project,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            elevation=2,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=12,
            )
        ],
        actions_padding=ft.padding.all(20),
        content_padding=ft.padding.all(20),
        title_padding=ft.padding.all(20),
        shape=ft.RoundedRectangleBorder(radius=12),
    )

    # ダイアログを表示
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_edit_project_dialog(
    page: ft.Page,  # type: ignore[name-defined]
    project: dict[str, str],
    on_save: Callable[[dict[str, str]], None] | None = None,
) -> None:
    """美しいプロジェクト編集ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        project: 編集対象のプロジェクト
        on_save: 保存時のコールバック関数
    """
    import flet as ft

    # 既存データでフォームフィールドを初期化
    name_field = ft.TextField(
        label="プロジェクト名",
        value=project.get("name", ""),
        prefix_icon=ft.Icons.WORK,
        border_color=ft.Colors.ORANGE_400,
        focused_border_color=ft.Colors.ORANGE_600,
        label_style=ft.TextStyle(color=ft.Colors.ORANGE_700),
        max_length=80,
        counter_text="",
    )

    description_field = ft.TextField(
        label="説明",
        value=project.get("description", ""),
        prefix_icon=ft.Icons.DESCRIPTION,
        border_color=ft.Colors.ORANGE_400,
        focused_border_color=ft.Colors.ORANGE_600,
        label_style=ft.TextStyle(color=ft.Colors.ORANGE_700),
        multiline=True,
        max_lines=3,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value=project.get("status", "進行中"),
        prefix_icon=ft.Icons.FLAG,
        border_color=ft.Colors.ORANGE_400,
        focused_border_color=ft.Colors.ORANGE_600,
        label_style=ft.TextStyle(color=ft.Colors.ORANGE_700),
        options=[
            ft.dropdown.Option("進行中", "進行中"),
            ft.dropdown.Option("計画中", "計画中"),
            ft.dropdown.Option("完了", "完了"),
            ft.dropdown.Option("保留", "保留"),
        ],
    )

    priority_dropdown = ft.Dropdown(
        label="優先度",
        value=project.get("priority", "標準"),
        prefix_icon=ft.Icons.PRIORITY_HIGH,
        border_color=ft.Colors.ORANGE_400,
        focused_border_color=ft.Colors.ORANGE_600,
        label_style=ft.TextStyle(color=ft.Colors.ORANGE_700),
        options=[
            ft.dropdown.Option("低", "低"),
            ft.dropdown.Option("標準", "標準"),
            ft.dropdown.Option("高", "高"),
        ],
    )

    def close_dialog(_: ft.ControlEvent) -> None:
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_project(_: ft.ControlEvent) -> None:
        """プロジェクト保存処理"""
        # 更新されたプロジェクトデータを作成
        updated_project = {
            **project,
            "name": name_field.value or project.get("name", ""),
            "description": description_field.value or "",
            "status": status_dropdown.value or "進行中",
            "priority": priority_dropdown.value or "標準",
        }

        # コールバック関数を呼び出してデータを親に渡す
        if on_save:
            on_save(updated_project)

        close_dialog(_)

    # 美しい編集ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.EDIT, color=ft.Colors.ORANGE_600, size=28),
                ft.Text(
                    "プロジェクトを編集",
                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=ft.Colors.ORANGE_700,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=12,
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    # 説明テキスト
                    ft.Container(
                        content=ft.Text(
                            f"「{project.get('name', '未名')}」の詳細を編集してください",
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.GREY_600,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    name_field,
                    description_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=True),
                            ft.Container(content=priority_dropdown, expand=True),
                        ],
                        spacing=16,
                    ),
                    # 進捗情報表示
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.TRENDING_UP,
                                    color=ft.Colors.ORANGE_400,
                                    size=16,
                                ),
                                ft.Text(
                                    f"進捗: {project.get('completed_tasks', '0')}/"
                                    f"{project.get('tasks_count', '0')} タスク完了",
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.Colors.ORANGE_600,
                                ),
                            ],
                            spacing=8,
                        ),
                        margin=ft.margin.only(top=12),
                    ),
                ],
                spacing=16,
                tight=True,
            ),
            width=520,
            padding=ft.padding.all(8),
        ),
        actions=[
            ft.Row(
                controls=[
                    ft.TextButton(
                        text="キャンセル",
                        icon=ft.Icons.CLOSE,
                        on_click=close_dialog,
                        style=ft.ButtonStyle(color=ft.Colors.GREY_600),
                    ),
                    ft.ElevatedButton(
                        text="保存",
                        icon=ft.Icons.SAVE,
                        on_click=save_project,
                        bgcolor=ft.Colors.ORANGE_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            elevation=2,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=12,
            )
        ],
        actions_padding=ft.padding.all(20),
        content_padding=ft.padding.all(20),
        title_padding=ft.padding.all(20),
        shape=ft.RoundedRectangleBorder(radius=12),
    )

    # ダイアログを表示
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
