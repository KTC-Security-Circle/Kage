"""Task Detail Panel component.

選択中タスクの詳細表示とステータス変更 UI を提供する。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.tasks.components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.tasks.presenter import TaskCardVM, TaskDetailVM


@dataclass(frozen=True)
class DetailPanelProps:
    """初期プロパティ。"""

    on_status_change: Callable[[str, str], None]
    on_edit: Callable[[str], None]  # タスクIDを受け取る編集コールバック


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
                        ft.Text(getattr(vm, "description", "") or "説明なし", color=ft.Colors.GREY_700),
                        ft.Divider(),
                        ft.Row([ft.Text("ステータス:"), self._status_dd]),
                        ft.Row([ft.Text("更新日:"), ft.Text(getattr(vm, "subtitle", ""))]),
                        ft.Row([ft.Text("期限:"), ft.Text(str(getattr(vm, "due_date", "") or "-"))]),
                        ft.Row([ft.Text("完了:"), ft.Text(str(getattr(vm, "completed_at", "") or "-"))]),
                        ft.Row([ft.Text("プロジェクトID:"), ft.Text(str(getattr(vm, "project_id", "") or "-"))]),
                        ft.Row([ft.Text("メモID:"), ft.Text(str(getattr(vm, "memo_id", "") or "-"))]),
                        ft.Row(
                            [
                                ft.Text("繰り返し:"),
                                ft.Text("あり" if getattr(vm, "is_recurring", False) else "なし"),
                            ]
                        ),
                        ft.Row([ft.Text("RRULE:"), ft.Text(str(getattr(vm, "recurrence_rule", "") or "-"))]),
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
                [ft.Text("タスクを選択して詳細を表示", color=ft.Colors.GREY_600)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
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
