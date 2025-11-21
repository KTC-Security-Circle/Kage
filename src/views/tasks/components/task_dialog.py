"""タスク作成・編集ダイアログ

タスクのCRUD操作のためのダイアログコンポーネント。
projectsの実装パターンに準拠した関数ベースのダイアログ。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

from .shared.constants import TASK_STATUS_LABELS


def show_create_task_dialog(
    page: ft.Page,  # type: ignore[name-defined]
    on_save: Callable[[dict[str, str]], None] | None = None,
) -> None:
    """新規タスク作成ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        on_save: 保存時のコールバック関数
    """
    import flet as ft

    # フォームフィールドを作成
    title_field = ft.TextField(
        label="タスクタイトル",
        hint_text="例: 要件定義書の作成",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        max_length=100,
        counter_text="",
        autofocus=True,
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="タスクの詳細を入力してください",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        multiline=True,
        min_lines=3,
        max_lines=5,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value="todo",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        options=[ft.dropdown.Option(key=key, text=label) for key, label in TASK_STATUS_LABELS.items()],
    )

    def close_dialog(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_task(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """タスク保存処理"""
        # タイトル必須バリデーション
        if not (title_field.value and title_field.value.strip()):
            title_field.error_text = "タスクタイトルは必須です"
            title_field.update()
            return
        title_field.error_text = None

        # タスクデータを作成
        task_data = {
            "title": title_field.value.strip(),
            "description": (description_field.value or "").strip(),
            "status": status_dropdown.value or "todo",
        }

        if on_save:
            on_save(task_data)

        close_dialog(_)

    # ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD_TASK, color=ft.Colors.BLUE_600, size=28),
                ft.Text(
                    "新しいタスク",
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
                            "新しいタスクの詳細を入力してください",
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.GREY_600,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    title_field,
                    description_field,
                    status_dropdown,
                ],
                spacing=16,
                tight=True,
            ),
            width=500,
        ),
        actions=[
            ft.TextButton(
                "キャンセル",
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "作成",
                on_click=save_task,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # ダイアログを表示
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_edit_task_dialog(
    page: ft.Page,  # type: ignore[name-defined]
    task_data: dict[str, str],
    on_save: Callable[[dict[str, str]], None] | None = None,
) -> None:
    """タスク編集ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        task_data: 既存のタスクデータ
        on_save: 保存時のコールバック関数
    """
    import flet as ft

    # フォームフィールドを作成（既存データで初期化）
    title_field = ft.TextField(
        label="タスクタイトル",
        hint_text="例: 要件定義書の作成",
        value=task_data.get("title", ""),
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        max_length=100,
        counter_text="",
        autofocus=True,
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="タスクの詳細を入力してください",
        value=task_data.get("description", ""),
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        multiline=True,
        min_lines=3,
        max_lines=5,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value=task_data.get("status", "todo"),
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        options=[ft.dropdown.Option(key=key, text=label) for key, label in TASK_STATUS_LABELS.items()],
    )

    def close_dialog(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_task(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """タスク保存処理"""
        # タイトル必須バリデーション
        if not (title_field.value and title_field.value.strip()):
            title_field.error_text = "タスクタイトルは必須です"
            title_field.update()
            return
        title_field.error_text = None

        # タスクデータを作成（IDは保持）
        updated_data = {
            "id": task_data.get("id", ""),
            "title": title_field.value.strip(),
            "description": (description_field.value or "").strip(),
            "status": status_dropdown.value or "todo",
        }

        if on_save:
            on_save(updated_data)

        close_dialog(_)

    # ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_600, size=28),
                ft.Text(
                    "タスクを編集",
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
                            "タスクの詳細を編集してください",
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.GREY_600,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    title_field,
                    description_field,
                    status_dropdown,
                ],
                spacing=16,
                tight=True,
            ),
            width=500,
        ),
        actions=[
            ft.TextButton(
                "キャンセル",
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "保存",
                on_click=save_task,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # ダイアログを表示
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
