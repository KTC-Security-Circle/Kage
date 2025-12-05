"""プロジェクト作成・編集ダイアログコンポーネント

美しい見た目を重視したシンプルなダイアログ実装。
保存機能は後で実装予定のため、UIの見た目とユーザビリティに焦点を当てる。
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from views.theme import (
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


DATE_SLICE_LENGTH = 10  # YYYY-MM-DD 長さ


def show_create_project_dialog(  # noqa: PLR0915, C901 - UI構築で許容
    page: ft.Page,  # type: ignore[name-defined]
    on_save: Callable[[dict[str, Any]], None] | None = None,
    available_tasks: list[dict[str, Any]] | None = None,
) -> None:
    """新規プロジェクト作成ダイアログを表示する（入力/バリデーション統合）。

    複雑度はUI部品配置のため高めだが、ロジック分離は save_project 内で行う。

    Args:
        page: Fletページインスタンス
        on_save: 保存時のコールバック関数
        available_tasks: 選択可能なタスクのリスト（id, titleを含む辞書のリスト）
    """
    import flet as ft

    # available_tasksがNoneの場合は空リストを使用
    tasks_list = available_tasks or []

    # フォームフィールドを作成（prefix_icon非推奨のためRow構成）
    name_field = ft.TextField(
        label="タイトル",
        hint_text="例: ウェブサイトリニューアル",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        max_length=80,
        counter_text="",
    )

    description_field = ft.TextField(
        label="説明",
        hint_text="プロジェクトの詳細を入力してください",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        hint_style=ft.TextStyle(color=get_text_secondary_color()),
        multiline=True,
        max_lines=3,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value="Active",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=[
            ft.dropdown.Option("Active", "Active"),
            ft.dropdown.Option("On-Hold", "On-Hold"),
            ft.dropdown.Option("Completed", "Completed"),
        ],
    )

    # タスク選択用（複数選択UI）
    selected_tasks: list[str] = []  # タスクIDのリスト
    selected_task_titles: dict[str, str] = {}  # ID -> タイトルのマッピング
    tasks_wrap = ft.Row(wrap=True, spacing=5)

    def add_task(_: ft.ControlEvent) -> None:
        if not task_dropdown.value:
            return
        task_id = task_dropdown.value
        if task_id not in selected_tasks:
            selected_tasks.append(task_id)
            # タイトルを取得
            task_title = selected_task_titles.get(task_id, task_id)
            # Chipを追加
            tasks_wrap.controls.append(
                ft.Chip(
                    label=ft.Text(task_title),
                    on_delete=lambda e, tid=task_id: remove_task(tid, e.control),
                )
            )
            with contextlib.suppress(AssertionError):
                tasks_wrap.update()
            task_dropdown.value = None
            task_dropdown.update()

    def remove_task(task_id: str, chip_control: ft.Control) -> None:
        if task_id in selected_tasks:
            selected_tasks.remove(task_id)
            tasks_wrap.controls.remove(chip_control)
            tasks_wrap.update()

    # 実際のタスクからドロップダウンオプションを生成
    task_options = []
    for task in tasks_list:
        task_id = str(task.get("id", ""))
        task_title = task.get("title", "無題のタスク")
        selected_task_titles[task_id] = task_title
        # project_idがNoneのタスクのみ選択可能
        if not task.get("project_id"):
            task_options.append(ft.dropdown.Option(task_id, task_title))

    task_dropdown = ft.Dropdown(
        label="関連タスク追加",
        hint_text="プロジェクトに未割り当てのタスクを選択",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=task_options,
        on_change=add_task,
        disabled=len(task_options) == 0,
    )

    # DatePicker を用いた期限入力
    due_date_text = ft.TextField(
        label="期限",
        hint_text="YYYY-MM-DD",
        read_only=True,
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        width=200,
    )

    # DatePicker はページ上で開く。選択時に TextField を更新する。
    import datetime as _dt

    # TODO: 日付抽出ロジックの共通化
    # - create/edit 双方で _on_date_change が重複しているため、モジュールレベル関数
    #   _extract_iso_date(e: ft.ControlEvent) -> str に切り出して再利用する。
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
        # 何も選択されず閉じた場合は変更なし（ログ程度ならここに）
        pass

    tz = _dt.UTC
    # locale ja, 範囲を動的(過去1年〜未来2年)へ
    # タイムゾーン付き現在日付（UTC）を利用して範囲生成
    today = _dt.datetime.now(tz=tz).date()
    date_picker = ft.DatePicker(
        first_date=_dt.datetime.combine(today - _dt.timedelta(days=365), _dt.time.min, tzinfo=tz),
        last_date=_dt.datetime.combine(today + _dt.timedelta(days=730), _dt.time.min, tzinfo=tz),
        on_change=_on_date_change,
        on_dismiss=_on_date_dismiss,
        # NOTE: locale引数は現行Fletでは未サポートのため除去（将来対応時に再追加）
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        page.open(date_picker)

    def close_dialog(_: ft.ControlEvent) -> None:
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_project(_: ft.ControlEvent) -> None:
        """プロジェクト保存処理"""
        # タイトル必須バリデーション
        if not (name_field.value and name_field.value.strip()):
            name_field.error_text = "タイトルは必須です"
            name_field.update()
            return
        name_field.error_text = None

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

        # ステータスはドメイン層のparseで正規化
        from models import ProjectStatus

        status_raw = (status_dropdown.value or "Active").strip()
        try:
            status_normalized = ProjectStatus.parse(status_raw).value
        except ValueError:
            status_normalized = "active"  # デフォルト

        # プロジェクトデータを作成（DBスキーマ準拠）
        now_iso = _dt.datetime.now(tz=tz).isoformat()

        project_data = {
            "id": str(__import__("uuid").uuid4()),
            "title": (name_field.value or "新しいプロジェクト").strip(),
            "description": (description_field.value or "").strip(),
            "status": status_normalized,
            "due_date": due_date_val,
            "task_ids": selected_tasks,  # 選択されたタスクのIDリスト
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if on_save:
            on_save(project_data)

        close_dialog(_)

    # 美しいダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD_CIRCLE, color=get_primary_color(), size=28),
                ft.Text(
                    "新しいプロジェクト",
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
                            "新しいプロジェクトの詳細を入力してください",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_text_secondary_color(),
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    name_field,
                    description_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown),
                            ft.Container(
                                on_click=_open_date_picker,
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=get_primary_color()),
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
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=8,
                    ),
                    ft.Column([task_dropdown, tasks_wrap], spacing=5),
                    # 注意書き
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.INFO, color=get_outline_color(), size=16),
                                ft.Text(
                                    "タイトルは必須項目です",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                    color=get_primary_color(),
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
                        style=ft.ButtonStyle(color=get_text_secondary_color()),
                    ),
                    ft.ElevatedButton(
                        text="作成",
                        icon=ft.Icons.ADD,
                        on_click=save_project,
                        bgcolor=get_primary_color(),
                        color=get_on_primary_color(),
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


def show_edit_project_dialog(  # noqa: PLR0915, C901 - 設計上の複合UI構築のため許容
    page: ft.Page,  # type: ignore[name-defined]
    project: dict[str, Any],
    on_save: Callable[[dict[str, Any]], None] | None = None,
    available_tasks: list[dict[str, Any]] | None = None,
) -> None:
    """美しいプロジェクト編集ダイアログを表示する。

    Args:
        page: Fletページインスタンス
        project: 編集対象のプロジェクト
        on_save: 保存時のコールバック関数
        available_tasks: 選択可能なタスクのリスト（id, title, project_idを含む辞書のリスト）
    """
    import flet as ft
    from loguru import logger

    logger.debug(f"show_edit_project_dialog 呼び出し: project={project.get('id')}, tasks={len(available_tasks or [])}")

    # available_tasksがNoneの場合は空リストを使用
    tasks_list = available_tasks or []

    # 既存データでフォームフィールドを初期化
    name_field = ft.TextField(
        label="タイトル",
        value=project.get("title", project.get("name", "")),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        max_length=80,
        counter_text="",
    )

    description_field = ft.TextField(
        label="説明",
        value=project.get("description", ""),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        multiline=True,
        max_lines=3,
        max_length=500,
        counter_text="",
    )

    status_dropdown = ft.Dropdown(
        label="ステータス",
        value=(project.get("status") or "Active").title().replace("_", "-"),
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=[
            ft.dropdown.Option("Active", "Active"),
            ft.dropdown.Option("On-Hold", "On-Hold"),
            ft.dropdown.Option("Completed", "Completed"),
            ft.dropdown.Option("Cancelled", "Cancelled"),
        ],
    )

    # タスク選択用（複数選択UI）
    project_id = str(project.get("id", ""))
    selected_tasks: list[str] = []  # タスクIDのリスト
    selected_task_titles: dict[str, str] = {}  # ID -> タイトルのマッピング
    tasks_wrap = ft.Row(wrap=True, spacing=5)

    # このプロジェクトに既に属しているタスクを初期選択として設定
    for task in tasks_list:
        task_id = str(task.get("id", ""))
        task_title = task.get("title", "無題のタスク")
        selected_task_titles[task_id] = task_title
        if str(task.get("project_id", "")) == project_id:
            selected_tasks.append(task_id)

    def add_task(_: ft.ControlEvent) -> None:
        if not task_dropdown.value:
            return
        task_id = task_dropdown.value
        if task_id not in selected_tasks:
            selected_tasks.append(task_id)
            _add_chip(task_id, do_update=True)
            task_dropdown.value = None
            task_dropdown.update()

    def remove_task(task_id: str, chip_control: ft.Control) -> None:
        if task_id in selected_tasks:
            selected_tasks.remove(task_id)
            tasks_wrap.controls.remove(chip_control)
            with contextlib.suppress(AssertionError):
                tasks_wrap.update()

    def _add_chip(task_id: str, *, do_update: bool = True) -> None:
        task_title = selected_task_titles.get(task_id, task_id)
        tasks_wrap.controls.append(
            ft.Chip(
                label=ft.Text(task_title),
                on_delete=lambda e, tid=task_id: remove_task(tid, e.control),
            )
        )
        if do_update:
            with contextlib.suppress(AssertionError):
                tasks_wrap.update()
            with contextlib.suppress(AssertionError):
                tasks_wrap.update()

    # 初期タスクの表示（この時点ではページに未追加なのでupdate不要）
    for task_id in selected_tasks:
        _add_chip(task_id, do_update=False)

    # 実際のタスクからドロップダウンオプションを生成
    # このプロジェクトに属していないタスクまたはproject_idがNoneのタスクのみ選択可能
    task_options = []
    for task in tasks_list:
        task_id = str(task.get("id", ""))
        task_title = task.get("title", "無題のタスク")
        task_project_id = task.get("project_id")
        # 未割り当てまたは他のプロジェクトに属していないタスクのみ
        if (not task_project_id or str(task_project_id) == project_id) and task_id not in selected_tasks:
            task_options.append(ft.dropdown.Option(task_id, task_title))

    task_dropdown = ft.Dropdown(
        label="関連タスク追加",
        hint_text="タスクを選択してください",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        options=task_options,
        on_change=add_task,
        disabled=len(task_options) == 0,
    )

    # 期限フィールド（編集時は既存値を反映）
    due_date_text = ft.TextField(
        label="期限",
        hint_text="YYYY-MM-DD",
        read_only=True,
        value=str(project.get("due_date", "")) if project.get("due_date") else "",
        border_color=get_outline_color(),
        focused_border_color=get_primary_color(),
        label_style=ft.TextStyle(color=get_primary_color()),
        width=200,
    )
    import datetime as _dt

    tz = _dt.UTC
    today = _dt.datetime.now(tz=tz).date()

    # TODO: 日付抽出ロジックの共通化
    # - create/edit 双方で _on_date_change が重複しているため、モジュールレベル関数
    #   _extract_iso_date(e: ft.ControlEvent) -> str に切り出して再利用する。
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

    date_picker = ft.DatePicker(
        first_date=_dt.datetime.combine(today - _dt.timedelta(days=365), _dt.time.min, tzinfo=tz),
        last_date=_dt.datetime.combine(today + _dt.timedelta(days=730), _dt.time.min, tzinfo=tz),
        on_change=_on_date_change,
    )

    def _open_date_picker(_: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        page.open(date_picker)

    def close_dialog(_: ft.ControlEvent) -> None:
        """ダイアログを閉じる"""
        dialog.open = False
        page.update()

    def save_project(_: ft.ControlEvent) -> None:
        """プロジェクト保存処理"""
        if not (name_field.value and name_field.value.strip()):
            name_field.error_text = "タイトルは必須です"
            name_field.update()
            return
        name_field.error_text = None

        # ステータスはドメイン層のparseで正規化
        from models import ProjectStatus

        raw_status = status_dropdown.value or "Active"
        try:
            normalized_status = ProjectStatus.parse(raw_status).value
        except ValueError:
            normalized_status = "active"

        due_raw = due_date_text.value.strip() if due_date_text.value else None

        title_val = (name_field.value or project.get("title", "")).strip()
        desc_val = (description_field.value or project.get("description", "")).strip()
        updated_project = {
            **project,
            "title": title_val,
            "description": desc_val,
            "status": normalized_status,
            "due_date": due_raw,
            "task_ids": selected_tasks,  # 選択されたタスクのIDリスト
            "updated_at": _dt.datetime.now(tz=tz).isoformat(),
        }
        try:
            # TODO: 本保存ロジックの実装
            # - 現在は on_save コールバックで外側へ返すだけです。
            # - 実装では ProjectApplicationService.update_project(...) を呼び出し、
            #   成功時にデータを再取得して UI を最新化してください。
            # - 失敗時はエラー内容を snackbar で通知してください。
            if on_save:
                on_save(updated_project)
            close_dialog(_)
        except Exception as e:
            # Fallback snackbar (Pageに既存snackbar APIがない場合はDialogで代替)
            from views.theme import get_error_color

            error_bar = ft.SnackBar(ft.Text(f"保存に失敗しました: {e}"), bgcolor=get_error_color())
            page.overlay.append(error_bar)
            error_bar.open = True
            page.update()

    # 美しい編集ダイアログを作成
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.EDIT, color=get_primary_color(), size=28),
                ft.Text(
                    "プロジェクトを編集",
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
                            f"「{project.get('name', '未名')}」の詳細を編集してください",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_text_secondary_color(),
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    # フォームフィールド
                    name_field,
                    description_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=status_dropdown),
                            ft.Container(
                                on_click=_open_date_picker,
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=get_primary_color()),
                                                due_date_text,
                                            ],
                                            spacing=6,
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
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=8,
                    ),
                    ft.Column([task_dropdown, tasks_wrap], spacing=5),
                    # 進捗情報表示
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.TRENDING_UP,
                                    color=get_outline_color(),
                                    size=16,
                                ),
                                ft.Text(
                                    f"進捗: {project.get('completed_tasks', '0')}/"
                                    f"{project.get('tasks_count', '0')} タスク完了",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                    color=get_primary_color(),
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
                        style=ft.ButtonStyle(color=get_text_secondary_color()),
                    ),
                    ft.ElevatedButton(
                        text="保存",
                        icon=ft.Icons.SAVE,
                        on_click=save_project,
                        bgcolor=get_primary_color(),
                        color=get_on_primary_color(),
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
