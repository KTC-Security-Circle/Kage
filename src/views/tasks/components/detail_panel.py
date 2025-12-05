"""Task Detail Panel component.

選択中タスクの詳細表示とステータス変更 UI を提供する。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.tasks.components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS
from views.theme import get_grey_color

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.tasks.presenter import RelatedTaskVM, TaskCardVM, TaskDetailVM


@dataclass(frozen=True)
class DetailPanelProps:
    """初期プロパティ。"""

    on_status_change: Callable[[str, str], None]
    on_edit: Callable[[str], None]  # タスクIDを受け取る編集コールバック
    on_task_select: Callable[[str], None] | None = None  # 関連タスク選択コールバック


class TaskDetailPanel:
    """右ペインの詳細表示コンポーネント (非継承)。"""

    def __init__(self, props: DetailPanelProps) -> None:
        self._props = props
        # TaskDetailVM 優先。後方互換で TaskCardVM も許容
        self._vm: TaskDetailVM | TaskCardVM | None = None
        self._status_dd: ft.Dropdown | None = None
        # ルートは固定のコンテナを持ち、content を差し替える（コントロール参照の不一致を防ぐ）
        self._root: ft.Container = ft.Container(expand=True)

    @property
    def control(self) -> ft.Control:
        # 初期表示はプレースホルダ
        if self._root.content is None:
            self._root.content = self._placeholder()
        return self._root

    def set_item(self, vm: TaskDetailVM | TaskCardVM | None) -> None:
        """詳細対象を切り替えて再描画。"""
        self._vm = vm
        if not vm:
            # 既存ルートの content を置換
            self._root.content = self._placeholder()
            with contextlib.suppress(AssertionError):
                self._root.update()
            return
        # TODO: MVC化時はフォーム編集(タイトル/説明/期日等)をこのパネルに統合し、
        #       変更は Controller 経由で ApplicationService に送る。
        # TODO: ステータス→色 (Badge) のマッピングは constants に集約し、表示とロジックで共有。
        # TODO: 書き込み失敗時は楽観的更新のロールバックとエラーToastを表示する。

        # Flet Option は key/text を指定可能。value は key が使われる。
        status_options = [ft.dropdown.Option(key=s, text=TASK_STATUS_LABELS.get(s, s)) for s in STATUS_ORDER]
        self._status_dd = ft.Dropdown(
            label="ステータス",
            value=vm.status or "",
            options=status_options,
            # 余分な str() 二重変換を排除し、None 時は空文字へ正規化
            on_change=lambda e: self._handle_status_change(e.control.value or ""),  # type: ignore[arg-type]
            width=220,
        )

        # 編集ボタン
        edit_button = ft.ElevatedButton(
            text="編集",
            icon=ft.Icons.EDIT,
            on_click=lambda _: self._handle_edit(),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        )

        card = ft.Card(
            expand=True,
            content=ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("タスク詳細", weight=ft.FontWeight.BOLD, size=18),
                                edit_button,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(vm.title, size=16),
                        ft.Text(getattr(vm, "description", "") or "説明なし", color=get_grey_color(700)),
                        ft.Divider(),
                        ft.Row([ft.Text("ステータス:"), self._status_dd]),
                        ft.Row([ft.Text("更新日:"), ft.Text(getattr(vm, "subtitle", ""))]),
                        ft.Row([ft.Text("期限:"), ft.Text(str(getattr(vm, "due_date", "") or "-"))]),
                        ft.Row([ft.Text("完了:"), ft.Text(str(getattr(vm, "completed_at", "") or "-"))]),
                        ft.Row([ft.Text("メモID:"), ft.Text(str(getattr(vm, "memo_id", "") or "-"))]),
                        ft.Row(
                            [
                                ft.Text("繰り返し:"),
                                ft.Text("あり" if getattr(vm, "is_recurring", False) else "なし"),
                            ]
                        ),
                        ft.Row([ft.Text("RRULE:"), ft.Text(str(getattr(vm, "recurrence_rule", "") or "-"))]),
                        self._build_project_info(vm),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=16,
            ),
        )
        # ルートの content を差し替えて更新
        self._root.content = card
        with contextlib.suppress(AssertionError):
            self._root.update()

    # Internal
    def _placeholder(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [ft.Text("タスクを選択して詳細を表示", color=get_grey_color(600))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
        )

    def _build_project_info(self, vm: TaskDetailVM | TaskCardVM) -> ft.Control:
        """プロジェクト情報を表示するコントロールを構築。

        Args:
            vm: タスクViewModel

        Returns:
            プロジェクト情報のCard
        """
        from views.theme import get_outline_color, get_primary_color, get_text_secondary_color

        project_name = getattr(vm, "project_name", None)
        project_status = getattr(vm, "project_status", None)
        project_tasks = getattr(vm, "project_tasks", [])

        if not project_name:
            return ft.Container()

        # 関連タスクセクション
        if project_tasks:
            # 展開状態を管理
            tasks_list = ft.Column(visible=False, spacing=4)
            toggle_button = ft.TextButton(
                text=f"関連タスクを表示 ({len(project_tasks)})",
                icon=ft.Icons.ARROW_DROP_DOWN,
            )

            def toggle_tasks(_: ft.ControlEvent) -> None:
                tasks_list.visible = not tasks_list.visible
                toggle_button.icon = ft.Icons.ARROW_DROP_UP if tasks_list.visible else ft.Icons.ARROW_DROP_DOWN
                toggle_button.text = (
                    "関連タスクを非表示" if tasks_list.visible else f"関連タスクを表示 ({len(project_tasks)})"
                )
                with contextlib.suppress(AssertionError):
                    toggle_button.update()
                    tasks_list.update()

            toggle_button.on_click = toggle_tasks

            # タスクリスト項目を作成
            def create_task_item(task: RelatedTaskVM) -> ft.Container:
                def on_jump_click(_: ft.ControlEvent) -> None:
                    if self._props.on_task_select:
                        self._props.on_task_select(task.id)

                return ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if task.is_completed else ft.Icons.CIRCLE_OUTLINED,
                                size=16,
                                color=ft.Colors.GREEN if task.is_completed else get_grey_color(400),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        task.title,
                                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        task.status,
                                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                                        color=get_text_secondary_color(),
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD,
                                icon_size=16,
                                tooltip="このタスクを表示",
                                on_click=on_jump_click,
                            ),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(vertical=4, horizontal=0),
                )

            task_items = [create_task_item(task) for task in project_tasks]

            tasks_list.controls = task_items
            tasks_section_controls = [ft.Divider(height=1), toggle_button, tasks_list]
        else:
            tasks_section_controls = []

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # セクションヘッダー
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.FOLDER_OUTLINED, size=20, color=get_primary_color()),
                                    ft.Text(
                                        "プロジェクト",
                                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=8),
                        ),
                        ft.Divider(height=1, color=get_outline_color()),
                        # プロジェクト情報
                        ft.Column(
                            controls=[
                                ft.Text(
                                    project_name,
                                    theme_style=ft.TextThemeStyle.BODY_LARGE,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    f"ステータス: {project_status}",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                    color=get_text_secondary_color(),
                                ),
                            ],
                            spacing=4,
                        ),
                        # 関連タスク
                        *tasks_section_controls,
                    ],
                    spacing=8,
                ),
                padding=16,
            ),
            elevation=1,
        )

    def _handle_status_change(self, new_status: str) -> None:
        """ステータス変更イベントを親へ通知する。

        Args:
            new_status: ドロップダウンで選択された新ステータスキー
        """
        if not self._vm:
            return
        # self._vm.id は VM 内部で文字列前提。安全のため明示的に str にしておく。
        self._props.on_status_change(str(self._vm.id), new_status)

    def _handle_edit(self) -> None:
        """編集ボタンクリック時の処理。"""
        if not self._vm:
            return
        self._props.on_edit(str(self._vm.id))
