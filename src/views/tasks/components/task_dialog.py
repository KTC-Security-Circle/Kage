"""タスク作成・編集ダイアログ

タスクのCRUD操作のためのダイアログコンポーネント。
projectsの実装パターンに準拠した関数ベースのダイアログ。
"""

from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING

from views.theme import (
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

from .shared.constants import TASK_STATUS_LABELS

DATE_SLICE_LENGTH = 10  # YYYY-MM-DD 長さ


def show_create_task_dialog(  # noqa: C901, PLR0915
    page: ft.Page,  # type: ignore[name-defined]
    on_save: Callable[[dict[str, str]], None] | None = None,
    all_tags: list | None = None,
    on_tags_change: Callable[[list[str]], None] | None = None,
) -> None:
    """新規タスク作成ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        on_save: 保存時のコールバック関数
        all_tags: 全タグのリスト
        on_tags_change: タグ変更時のコールバック関数
    """
    import flet as ft

    from views.theme import get_grey_color

    # フォームフィールドを作成
    title_field = ft.TextField(
        label="タスクタイトル",
        hint_text="例: 要件定義書の作成",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        max_length=100,
        counter_text="",
        autofocus=True,
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="タスクの詳細を入力してください",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        multiline=True,
        min_lines=3,
        max_lines=5,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value="todo",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=[ft.dropdown.Option(key=key, text=label) for key, label in TASK_STATUS_LABELS.items()],
    )

    # DatePicker を用いた期限入力
    date_picker = ft.DatePicker(
        on_change=lambda e: (
            setattr(due_date_text, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""),
            due_date_text.update(),
        ),
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:
        """DatePicker を開く"""
        page.open(date_picker)

    calendar_button = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        icon_size=20,
        tooltip="カレンダーから選択",
        on_click=_open_date_picker,
    )

    due_date_text = ft.TextField(
        label="期限日",
        hint_text="YYYY-MM-DD 形式で入力",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        suffix=calendar_button,
    )

    # タグ選択機能
    selected_tag_ids: set[str] = set()

    tag_options = [ft.dropdown.Option(key=tag.name, text=tag.name) for tag in all_tags] if all_tags else []
    tag_dropdown = ft.Dropdown(
        label="タグを追加",
        hint_text="タグを選択...",
        options=tag_options,
        width=300,
    )

    selected_tags_container = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def _update_selected_tags_display() -> None:
        """選択中タグのバッジ表示を更新"""
        selected_tags_container.controls.clear()
        if not all_tags:
            return

        for tag_name in sorted(selected_tag_ids):
            tag = next((t for t in all_tags if t.name == tag_name), None)
            if tag is None:
                continue

            color = tag.color or get_grey_color(600)

            def make_remove_handler(name: str) -> Callable[[ft.ControlEvent], None]:
                def handler(_: ft.ControlEvent) -> None:
                    selected_tag_ids.discard(name)
                    _update_selected_tags_display()

                return handler

            badge = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(tag_name, size=12, color=get_on_primary_color()),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=14,
                            icon_color=get_on_primary_color(),
                            on_click=make_remove_handler(tag_name),
                            tooltip=f"{tag_name}を削除",
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=color,
                border_radius=12,
                padding=ft.padding.only(left=12, right=4, top=4, bottom=4),
            )
            selected_tags_container.controls.append(badge)

        if hasattr(selected_tags_container, "page") and selected_tags_container.page:
            try:
                selected_tags_container.update()
            except Exception as e:
                from loguru import logger

                logger.debug(f"Failed to update selected tags display: {e}")

    def _on_tag_select(e: ft.ControlEvent) -> None:
        """タグ選択時のハンドラ"""
        if e.control.value and e.control.value not in selected_tag_ids:
            selected_tag_ids.add(e.control.value)
            _update_selected_tags_display()
            tag_dropdown.value = None
            try:
                tag_dropdown.update()
            except Exception as ex:
                from loguru import logger

                logger.debug(f"Failed to update tag dropdown: {ex}")

    tag_dropdown.on_change = _on_tag_select

    # 初期表示時にタグバッジを更新
    _update_selected_tags_display()

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

            min_str = (_dt.datetime.now(tz=_dt.UTC).date() - _dt.timedelta(days=365)).strftime("%Y-%m-%d")
            max_str = (_dt.datetime.now(tz=_dt.UTC).date() + _dt.timedelta(days=730)).strftime("%Y-%m-%d")
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
        }

        if on_save:
            on_save(task_data)

        # タグ変更を通知
        if on_tags_change and all_tags:
            tag_ids = [str(tag.id) for tag in all_tags if tag.name in selected_tag_ids]
            on_tags_change(tag_ids)

        close_dialog(_)

    # ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD_TASK, color=get_primary_color(), size=28),
                ft.Text(
                    "新しいタスク",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=get_primary_color(),
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
                            "タスクのタイトル、説明、ステータス、期限日を入力してください。\n期限日はカレンダーから選択するか、YYYY-MM-DD形式で直接入力できます。",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_text_secondary_color(),
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    title_field,
                    description_field,
                    # ステータスと期限を横並び
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=1),
                            ft.Container(content=due_date_text, expand=1),
                        ],
                        spacing=16,
                    ),
                    # タグ選択
                    *(
                        [
                            ft.Divider(height=1),
                            ft.Text("タグ", weight=ft.FontWeight.BOLD, size=14),
                            tag_dropdown,
                            selected_tags_container,
                        ]
                        if all_tags
                        else []
                    ),
                ],
                spacing=20,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=600,
            padding=ft.padding.symmetric(horizontal=4),
        ),
        actions=[
            ft.TextButton(
                "キャンセル",
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "作成",
                on_click=save_task,
                bgcolor=get_primary_color(),
                color=get_on_primary_color(),
            ),
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


def show_edit_task_dialog(  # noqa: C901, PLR0915
    page: ft.Page,  # type: ignore[name-defined]
    task_data: dict[str, str],
    on_save: Callable[[dict[str, str]], None] | None = None,
    all_tags: list | None = None,
    on_tags_change: Callable[[list[str]], None] | None = None,
) -> None:
    """タスク編集ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        task_data: 既存のタスクデータ
        on_save: 保存時のコールバック関数
        all_tags: 全タグのリスト
        on_tags_change: タグ変更時のコールバック関数
    """
    import flet as ft

    from views.theme import get_grey_color

    # フォームフィールドを作成（既存データで初期化）
    title_field = ft.TextField(
        label="タスクタイトル",
        hint_text="例: 要件定義書の作成",
        value=task_data.get("title", ""),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        max_length=100,
        counter_text="",
        autofocus=True,
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="タスクの詳細を入力してください",
        value=task_data.get("description", ""),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        multiline=True,
        min_lines=3,
        max_lines=5,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value=task_data.get("status", "todo"),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=[ft.dropdown.Option(key=key, text=label) for key, label in TASK_STATUS_LABELS.items()],
    )

    # DatePicker を用いた期限入力
    due_date_raw = task_data.get("due_date", "")
    # 期限日の初期値を処理（None, 空文字列、または日付文字列）
    if due_date_raw and due_date_raw not in ("None", "null", ""):
        # 日付文字列の場合、YYYY-MM-DD形式に正規化
        due_date_initial = str(due_date_raw)[:DATE_SLICE_LENGTH]
    else:
        due_date_initial = ""

    date_picker = ft.DatePicker(
        on_change=lambda e: (
            setattr(due_date_text, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""),
            due_date_text.update(),
        ),
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:
        """DatePicker を開く"""
        page.open(date_picker)

    calendar_button = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        icon_size=20,
        tooltip="カレンダーから選択",
        on_click=_open_date_picker,
    )

    due_date_text = ft.TextField(
        label="期限日",
        hint_text="YYYY-MM-DD 形式で入力",
        value=due_date_initial,
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        suffix=calendar_button,
    )

    # タグ選択機能
    task_tags = task_data.get("tags", []) or []
    # task_tagsは文字列のリスト（タグ名）
    selected_tag_ids: set[str] = {str(tag) for tag in task_tags if isinstance(tag, str)}

    tag_options = [ft.dropdown.Option(key=tag.name, text=tag.name) for tag in all_tags] if all_tags else []
    tag_dropdown = ft.Dropdown(
        label="タグを追加",
        hint_text="タグを選択...",
        options=tag_options,
        width=300,
    )

    selected_tags_container = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def _update_selected_tags_display() -> None:
        """選択中タグのバッジ表示を更新"""
        selected_tags_container.controls.clear()
        if not all_tags:
            return

        for tag_name in sorted(selected_tag_ids):
            tag = next((t for t in all_tags if t.name == tag_name), None)
            if tag is None:
                continue

            color = tag.color or get_grey_color(600)

            def make_remove_handler(name: str) -> Callable[[ft.ControlEvent], None]:
                def handler(_: ft.ControlEvent) -> None:
                    selected_tag_ids.discard(name)
                    _update_selected_tags_display()

                return handler

            badge = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(tag_name, size=12, color=get_on_primary_color()),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=14,
                            icon_color=get_on_primary_color(),
                            on_click=make_remove_handler(tag_name),
                            tooltip=f"{tag_name}を削除",
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=color,
                border_radius=12,
                padding=ft.padding.only(left=12, right=4, top=4, bottom=4),
            )
            selected_tags_container.controls.append(badge)

        if hasattr(selected_tags_container, "page") and selected_tags_container.page:
            try:
                selected_tags_container.update()
            except Exception as e:
                from loguru import logger

                logger.debug(f"Failed to update selected tags display: {e}")

    def _on_tag_select(e: ft.ControlEvent) -> None:
        """タグ選択時のハンドラ"""
        if e.control.value and e.control.value not in selected_tag_ids:
            selected_tag_ids.add(e.control.value)
            _update_selected_tags_display()
            tag_dropdown.value = None
            try:
                tag_dropdown.update()
            except Exception as ex:
                from loguru import logger

                logger.debug(f"Failed to update tag dropdown: {ex}")

    tag_dropdown.on_change = _on_tag_select

    # 初期表示時にタグバッジを更新
    _update_selected_tags_display()

    def close_dialog(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_task(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """タスク保存処理"""
        from loguru import logger

        logger.info(f"編集ダイアログの保存ボタンがクリックされました: task_id={task_data.get('id')}")

        # タイトル必須バリデーション
        if not (title_field.value and title_field.value.strip()):
            title_field.error_text = "タスクタイトルは必須です"
            title_field.update()
            logger.warning("タイトルが空のため保存をキャンセルしました")
            return
        title_field.error_text = None

        # due_date 未設定時は None 表現 + 範囲バリデーション
        due_date_val = due_date_text.value.strip() if due_date_text.value else None
        if due_date_val:
            from views.shared.forms.validators import ValidationRule

            min_str = (_dt.datetime.now(tz=_dt.UTC).date() - _dt.timedelta(days=365)).strftime("%Y-%m-%d")
            max_str = (_dt.datetime.now(tz=_dt.UTC).date() + _dt.timedelta(days=730)).strftime("%Y-%m-%d")
            valid, error = ValidationRule.date_range(min_str, max_str)(due_date_val)
            if not valid:
                due_date_text.error_text = error
                due_date_text.update()
                logger.warning(f"期限日のバリデーションエラー: {error}")
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

        logger.debug(f"保存データ: {updated_data}")

        if on_save:
            logger.info("on_saveコールバックを呼び出します")
            on_save(updated_data)
        else:
            logger.warning("on_saveコールバックが設定されていません")

        # タグ変更を通知
        if on_tags_change and all_tags:
            tag_ids = [str(tag.id) for tag in all_tags if tag.name in selected_tag_ids]
            logger.info(f"タグ変更を通知: {len(tag_ids)}個のタグ")
            on_tags_change(tag_ids)

        logger.info("ダイアログを閉じます")
        close_dialog(_)

    # ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.EDIT, color=get_primary_color(), size=28),
                ft.Text(
                    "タスクを編集",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=get_primary_color(),
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
                            "タスクのタイトル、説明、ステータス、期限日を編集できます。\n期限日はカレンダーから選択するか、YYYY-MM-DD形式で直接入力できます。",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_text_secondary_color(),
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    title_field,
                    description_field,
                    # ステータスと期限を横並び
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown, expand=1),
                            ft.Container(content=due_date_text, expand=1),
                        ],
                        spacing=16,
                    ),
                    # タグ選択
                    *(
                        [
                            ft.Divider(height=1),
                            ft.Text("タグ", weight=ft.FontWeight.BOLD, size=14),
                            tag_dropdown,
                            selected_tags_container,
                        ]
                        if all_tags
                        else []
                    ),
                ],
                spacing=20,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=600,
            padding=ft.padding.symmetric(horizontal=4),
        ),
        actions=[
            ft.TextButton(
                "キャンセル",
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "保存",
                on_click=save_task,
                bgcolor=get_primary_color(),
                color=get_on_primary_color(),
            ),
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
