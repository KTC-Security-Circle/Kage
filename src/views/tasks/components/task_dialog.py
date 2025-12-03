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

DATE_SLICE_LENGTH = 10  # YYYY-MM-DD 長さ


def show_create_task_dialog(  # noqa: PLR0915, C901 - UI構築で許容
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

    # DatePicker を用いた期限入力
    due_date_text = ft.TextField(
        label="期限日",
        hint_text="YYYY-MM-DD",
        read_only=True,
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        width=200,
    )

    # DatePicker はページ上で開く。選択時に TextField を更新する。
    import datetime as _dt

    def _on_date_change(e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        # e.data が '2025-11-27T00:00:00.000' のような日時文字列で来る場合があるため日付部分のみ抽出
        raw = e.data or ""
        if raw:
            # ISO形式の先頭10文字(YYYY-MM-DD)を利用
            iso_date = raw[:10]
        elif e.control.value:
            try:
                iso_date = e.control.value.strftime("%Y-%m-%d")
            except Exception:
                txt = str(e.control.value)
                iso_date = txt[:DATE_SLICE_LENGTH] if len(txt) >= DATE_SLICE_LENGTH else txt
        else:
            iso_date = ""
        due_date_text.value = iso_date
        due_date_text.update()

    def _on_date_dismiss(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        pass

    tz = _dt.UTC
    today = _dt.datetime.now(tz=tz).date()
    date_picker = ft.DatePicker(
        first_date=_dt.datetime.combine(today - _dt.timedelta(days=365), _dt.time.min, tzinfo=tz),
        last_date=_dt.datetime.combine(today + _dt.timedelta(days=730), _dt.time.min, tzinfo=tz),
        on_change=_on_date_change,
        on_dismiss=_on_date_dismiss,
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        page.open(date_picker)

    completed_at_field = ft.TextField(
        label="完了日時",
        hint_text="YYYY-MM-DD HH:MM:SS",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        expand=True,
    )

    project_id_field = ft.TextField(
        label="プロジェクトID",
        hint_text="UUID",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        expand=True,
    )

    memo_id_field = ft.TextField(
        label="メモID",
        hint_text="UUID",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        expand=True,
    )

    recurrence_rule_field = ft.TextField(
        label="繰り返しルール",
        hint_text="例: FREQ=DAILY",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        visible=False,
        expand=True,
    )

    def on_recurring_change(e: ft.ControlEvent) -> None:
        recurrence_rule_field.visible = e.control.value
        recurrence_rule_field.update()

    is_recurring_checkbox = ft.Checkbox(
        label="繰り返しタスク",
        on_change=on_recurring_change,
        fill_color=ft.Colors.BLUE_600,
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

        # due_date 未設定時は None 表現 + 範囲バリデーション
        due_date_val = due_date_text.value.strip() if due_date_text.value else None
        if due_date_val:
            from views.shared.forms.validators import ValidationRule

            min_str = (_dt.datetime.now(tz=tz).date() - _dt.timedelta(days=365)).strftime("%Y-%m-%d")
            max_str = (_dt.datetime.now(tz=tz).date() + _dt.timedelta(days=730)).strftime("%Y-%m-%d")
            valid, error = ValidationRule.date_range(min_str, max_str)(due_date_val)
            if not valid:
                due_date_text.error_text = error
                due_date_text.update()
                return
            due_date_text.error_text = None

        # タスクデータを作成
        task_data = {
            "title": title_field.value.strip(),
            "description": (description_field.value or "").strip(),
            "status": status_dropdown.value or "todo",
            "due_date": due_date_val,
            "completed_at": completed_at_field.value.strip() if completed_at_field.value else None,
            "project_id": project_id_field.value.strip() if project_id_field.value else None,
            "memo_id": memo_id_field.value.strip() if memo_id_field.value else None,
            "is_recurring": str(is_recurring_checkbox.value),
            "recurrence_rule": recurrence_rule_field.value.strip() if recurrence_rule_field.value else None,
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
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=True),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=ft.Colors.BLUE_600),
                                                due_date_text,
                                            ],
                                            spacing=6,
                                            alignment=ft.MainAxisAlignment.START,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.EVENT_AVAILABLE,
                                            tooltip="期限を選択",
                                            on_click=_open_date_picker,
                                            icon_size=26,
                                            style=ft.ButtonStyle(padding=ft.padding.all(8)),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.CLEAR,
                                            tooltip="期限クリア",
                                            on_click=lambda _: (
                                                setattr(due_date_text, "value", ""),
                                                due_date_text.update(),
                                            ),
                                            icon_size=22,
                                            style=ft.ButtonStyle(padding=ft.padding.all(8)),
                                        ),
                                    ],
                                    spacing=8,
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                            ),
                        ],
                        spacing=20,
                    ),
                    ft.Row([project_id_field, memo_id_field], spacing=20),
                    completed_at_field,
                    is_recurring_checkbox,
                    recurrence_rule_field,
                ],
                spacing=16,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=600,
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
                        on_click=save_task,
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


def show_edit_task_dialog(  # noqa: PLR0915, C901 - UI構築で許容
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

    # DatePicker を用いた期限入力
    due_date_text = ft.TextField(
        label="期限日",
        hint_text="YYYY-MM-DD",
        read_only=True,
        value=task_data.get("due_date", ""),
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_700),
        width=200,
    )

    import datetime as _dt

    def _on_date_change(e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        raw = e.data or ""
        if raw:
            iso_date = raw[:10]
        elif e.control.value:
            try:
                iso_date = e.control.value.strftime("%Y-%m-%d")
            except Exception:
                txt = str(e.control.value)
                iso_date = txt[:DATE_SLICE_LENGTH] if len(txt) >= DATE_SLICE_LENGTH else txt
        else:
            iso_date = ""
        due_date_text.value = iso_date
        due_date_text.update()

    def _on_date_dismiss(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        pass

    tz = _dt.UTC
    today = _dt.datetime.now(tz=tz).date()
    date_picker = ft.DatePicker(
        first_date=_dt.datetime.combine(today - _dt.timedelta(days=365), _dt.time.min, tzinfo=tz),
        last_date=_dt.datetime.combine(today + _dt.timedelta(days=730), _dt.time.min, tzinfo=tz),
        on_change=_on_date_change,
        on_dismiss=_on_date_dismiss,
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        page.open(date_picker)

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

        # due_date 未設定時は None 表現 + 範囲バリデーション
        due_date_val = due_date_text.value.strip() if due_date_text.value else None
        if due_date_val:
            from views.shared.forms.validators import ValidationRule

            min_str = (_dt.datetime.now(tz=tz).date() - _dt.timedelta(days=365)).strftime("%Y-%m-%d")
            max_str = (_dt.datetime.now(tz=tz).date() + _dt.timedelta(days=730)).strftime("%Y-%m-%d")
            valid, error = ValidationRule.date_range(min_str, max_str)(due_date_val)
            if not valid:
                due_date_text.error_text = error
                due_date_text.update()
                return
            due_date_text.error_text = None

        # タスクデータを作成（IDは保持）
        updated_data = {
            "id": task_data.get("id", ""),
            "title": title_field.value.strip(),
            "description": (description_field.value or "").strip(),
            "status": status_dropdown.value or "todo",
            "due_date": due_date_val,
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
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=True),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=ft.Colors.BLUE_600),
                                                due_date_text,
                                            ],
                                            spacing=6,
                                            alignment=ft.MainAxisAlignment.START,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.EVENT_AVAILABLE,
                                            tooltip="期限を選択",
                                            on_click=_open_date_picker,
                                            icon_size=26,
                                            style=ft.ButtonStyle(padding=ft.padding.all(8)),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.CLEAR,
                                            tooltip="期限クリア",
                                            on_click=lambda _: (
                                                setattr(due_date_text, "value", ""),
                                                due_date_text.update(),
                                            ),
                                            icon_size=22,
                                            style=ft.ButtonStyle(padding=ft.padding.all(8)),
                                        ),
                                    ],
                                    spacing=8,
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                            ),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=16,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=600,
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
                        on_click=save_task,
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
