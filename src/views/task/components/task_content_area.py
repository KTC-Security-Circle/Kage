"""タスクコンテンツエリアコンポーネント

メインのタスク表示・編集エリアを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from models.new_task import TaskStatus

if TYPE_CHECKING:
    from logic.services.project_service import ProjectService
    from logic.services.task_service import TaskService
    from models.new_task import TaskRead


class TaskContentArea(ft.Column):
    """タスクコンテンツエリアコンポーネント

    タスクの一覧表示、詳細表示、編集機能を提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        task_service: TaskService,
        project_service: ProjectService,
    ) -> None:
        """TaskContentAreaのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            task_service: タスクサービス
            project_service: プロジェクトサービス
        """
        super().__init__()
        self._page = page
        self.task_service = task_service
        self.project_service = project_service
        self.spacing = 10
        self.expand = True

        # 現在の表示モード
        self.current_mode = "list"  # "list", "detail", "edit", "quick_add"
        self.current_tasks: list[TaskRead] = []
        self.selected_task: TaskRead | None = None
        self.current_filter_status: TaskStatus | None = None  # [AI GENERATED] 現在のフィルタリング状態を保持

        # コンポーネントの初期化
        self._build_content_area()

    def _build_content_area(self) -> None:
        """コンテンツエリアのレイアウトを構築"""
        self.controls = [
            # ヘッダー部分
            self._build_header(),
            ft.Divider(),
            # メインコンテンツ
            self._build_main_content(),
        ]

    def _build_header(self) -> ft.Row:
        """ヘッダー部分を構築"""
        return ft.Row(
            [
                ft.Text(
                    "タスク一覧",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="更新",
                    on_click=self._refresh_content,
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="新しいタスク",
                    on_click=self._show_add_task_form,
                ),
            ]
        )

    def _build_main_content(self) -> ft.Container:
        """メインコンテンツエリアを構築"""
        if self.current_mode == "list":
            return self._build_task_list()
        if self.current_mode == "quick_add":
            return self._build_quick_add_form()
        if self.current_mode == "detail":
            return self._build_task_detail()
        if self.current_mode == "edit":
            return self._build_task_edit_form()
        return ft.Container(
            content=ft.Text("表示モードが無効です", size=16),
            alignment=ft.alignment.center,
        )

    def _build_task_list(self) -> ft.Container:
        """タスク一覧を構築"""
        if not self.current_tasks:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.TASK_ALT, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "タスクがありません",
                            size=18,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )

        task_list = ft.ListView(
            spacing=8,
            padding=ft.padding.all(10),
            expand=True,
        )

        for task in self.current_tasks:
            task_list.controls.append(self._create_task_card(task))

        return ft.Container(content=task_list, expand=True)

    def _create_task_card(self, task: TaskRead) -> ft.Card:
        """タスクカードを作成

        Args:
            task: タスクオブジェクト

        Returns:
            タスクカード
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        # チェックボックス
                        ft.Checkbox(
                            value=task.status == TaskStatus.COMPLETED,
                            on_change=lambda e, t=task: self._toggle_task_completion(t, is_completed=e.control.value),
                        ),
                        # タスク内容
                        ft.Column(
                            [
                                ft.Text(
                                    task.title,
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Row(
                                    [
                                        # ステータス変更ドロップダウン
                                        ft.Dropdown(
                                            value=task.status.value,
                                            options=[
                                                ft.dropdown.Option("inbox", "📥 Inbox"),
                                                ft.dropdown.Option("next_action", "🎯 Next Action"),
                                                ft.dropdown.Option("waiting_for", "⏳ Waiting"),
                                                ft.dropdown.Option("someday_maybe", "💭 Someday"),
                                                ft.dropdown.Option("delegated", "👥 Delegated"),
                                                ft.dropdown.Option("completed", "✅ Completed"),
                                                ft.dropdown.Option("cancelled", "❌ Cancelled"),
                                            ],
                                            width=150,
                                            on_change=lambda e, t=task: self._change_task_status(t, e.control.value),
                                        ),
                                        # 期限表示
                                        ft.Text(
                                            f"期限: {task.due_date}" if task.due_date else "期限なし",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                        )
                                        if hasattr(task, "due_date")
                                        else ft.Container(),
                                    ]
                                ),
                            ],
                            expand=True,
                        ),
                        # アクションボタン
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=16,
                            tooltip="編集",
                            on_click=lambda _, t=task: self._show_task_detail(t),
                        ),
                    ]
                ),
                padding=15,
                on_click=lambda _, t=task: self._show_task_detail(t),
            ),
            elevation=2,
        )

    def _build_quick_add_form(self) -> ft.Container:
        """クイック追加フォームを構築"""
        self.title_field = ft.TextField(
            label="タスクタイトル",
            expand=True,
            autofocus=True,
        )

        self.description_field = ft.TextField(
            label="説明（任意）",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("新しいタスクを追加", size=20, weight=ft.FontWeight.BOLD),
                    self.title_field,
                    self.description_field,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "追加",
                                icon=ft.Icons.ADD,
                                on_click=self._add_task,
                            ),
                            ft.TextButton(
                                "キャンセル",
                                on_click=self._cancel_add_task,
                            ),
                        ]
                    ),
                ]
            ),
            padding=20,
        )

    def _build_task_detail(self) -> ft.Container:
        """タスク詳細表示を構築"""
        if not self.selected_task:
            return ft.Container(
                content=ft.Text("選択されたタスクがありません"),
                alignment=ft.alignment.center,
            )

        task = self.selected_task
        status_color = self._get_status_color(task.status)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("タスク詳細", size=20, weight=ft.FontWeight.BOLD, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="編集",
                                on_click=self._show_edit_form,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                tooltip="閉じる",
                                on_click=self._close_detail,
                            ),
                        ]
                    ),
                    ft.Text(task.title, size=18, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=ft.Text(
                            task.status.value.replace("_", " ").title(),
                            size=12,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=12,
                        width=None,
                    ),
                    ft.Text(task.description or "説明なし", size=14),
                    ft.Text(
                        f"期限: {task.due_date}" if hasattr(task, "due_date") and task.due_date else "期限なし",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ]
            ),
            padding=20,
        )

    def _build_task_edit_form(self) -> ft.Container:
        """タスク編集フォームを構築"""
        # [AI GENERATED] 編集フォームの実装は後の段階で追加
        return ft.Container(
            content=ft.Text("編集フォーム（未実装）"),
            alignment=ft.alignment.center,
        )

    def _get_status_color(self, status: TaskStatus) -> str:
        """ステータスに応じた色を取得

        Args:
            status: タスクステータス

        Returns:
            色文字列
        """
        color_map = {
            TaskStatus.INBOX: ft.Colors.GREY_600,
            TaskStatus.NEXT_ACTION: ft.Colors.BLUE_600,
            TaskStatus.WAITING_FOR: ft.Colors.ORANGE_600,
            TaskStatus.SOMEDAY_MAYBE: ft.Colors.PURPLE_600,
            TaskStatus.DELEGATED: ft.Colors.CYAN_600,
            TaskStatus.COMPLETED: ft.Colors.GREEN_600,
            TaskStatus.CANCELLED: ft.Colors.RED_600,
        }
        return color_map.get(status, ft.Colors.GREY_600)

    def show_tasks_by_status(self, status: TaskStatus) -> None:
        """ステータス別タスク表示

        Args:
            status: 表示するタスクステータス
        """
        try:
            self.current_filter_status = status  # [AI GENERATED] 現在のフィルタ状態を保存
            self.current_tasks = self.task_service.get_tasks_by_status(status)
            self.current_mode = "list"
            self._build_content_area()
            self.update()
        except Exception:
            self._show_error("タスクの取得に失敗しました")

    def show_tasks_by_project(self, project_id: str) -> None:
        """プロジェクト別タスク表示

        Args:
            project_id: プロジェクトID
        """
        try:
            import uuid

            project_uuid = uuid.UUID(project_id)
            self.current_tasks = self.task_service.get_tasks_by_project_id(project_uuid)
            self.current_mode = "list"
            self._build_content_area()
            self.update()
        except Exception:
            self._show_error("プロジェクトのタスク取得に失敗しました")

    def show_quick_add_form(self, default_status: TaskStatus) -> None:
        """クイック追加フォーム表示

        Args:
            default_status: デフォルトのタスクステータス
        """
        self.default_status = default_status
        self.current_mode = "quick_add"
        self._build_content_area()
        self.update()

    def _show_task_detail(self, task: TaskRead) -> None:
        """タスク詳細表示"""
        self.selected_task = task
        self.current_mode = "detail"
        self._build_content_area()
        self.update()

    def _show_edit_form(self, _: ft.ControlEvent | None = None) -> None:
        """編集フォーム表示"""
        self.current_mode = "edit"
        self._build_content_area()
        self.update()

    def _show_add_task_form(self, _: ft.ControlEvent) -> None:
        """タスク追加フォーム表示"""
        self.current_mode = "quick_add"
        self.default_status = TaskStatus.INBOX
        self._build_content_area()
        self.update()

    def _close_detail(self, _: ft.ControlEvent) -> None:
        """詳細画面を閉じる"""
        self.current_mode = "list"
        self.selected_task = None
        self._build_content_area()
        self.update()

    def _refresh_content(self, _: ft.ControlEvent) -> None:
        """コンテンツを更新"""
        if self.current_mode == "list":
            self._build_content_area()
            self.update()

    def _toggle_task_completion(self, task: TaskRead, *, is_completed: bool) -> None:
        """タスクの完了状態を切り替え

        Args:
            task: 対象タスク
            is_completed: 完了状態
        """
        try:
            from models.new_task import TaskUpdate

            if is_completed:
                # [AI GENERATED] タスクを完了状態に変更
                update_data = TaskUpdate(status=TaskStatus.COMPLETED)
                self.task_service.update_task(task.id, update_data)
            else:
                # [AI GENERATED] タスクを未完了状態に変更（前のステータスまたはINBOXに戻す）
                # 完了状態から戻す場合は、とりあえずINBOXに戻す
                update_data = TaskUpdate(status=TaskStatus.INBOX)
                self.task_service.update_task(task.id, update_data)

            # タスクリストを更新
            self.refresh()
        except Exception:
            self._show_error("タスクの更新に失敗しました")

    def _change_task_status(self, task: TaskRead, new_status: str) -> None:
        """タスクのステータスを変更

        Args:
            task: 対象タスク
            new_status: 新しいステータス（文字列値）
        """
        try:
            from models.new_task import TaskUpdate

            # [AI GENERATED] 文字列値をTaskStatusに変換
            status_map = {
                "inbox": TaskStatus.INBOX,
                "next_action": TaskStatus.NEXT_ACTION,
                "waiting_for": TaskStatus.WAITING_FOR,
                "someday_maybe": TaskStatus.SOMEDAY_MAYBE,
                "delegated": TaskStatus.DELEGATED,
                "completed": TaskStatus.COMPLETED,
                "cancelled": TaskStatus.CANCELLED,
            }

            if new_status not in status_map:
                self._show_error(f"無効なステータス: {new_status}")
                return

            new_task_status = status_map[new_status]

            # タスクのステータスを更新
            update_data = TaskUpdate(status=new_task_status)
            self.task_service.update_task(task.id, update_data)

            # タスクリストを更新
            self.refresh()
        except Exception:
            self._show_error("タスクステータスの変更に失敗しました")

    def _add_task(self, _: ft.ControlEvent) -> None:
        """タスクを追加"""
        if not self.title_field.value:
            self._show_error("タイトルを入力してください")
            return

        try:
            from models.new_task import TaskCreate

            task_data = TaskCreate(
                title=self.title_field.value,
                description=self.description_field.value or "",
                status=getattr(self, "default_status", TaskStatus.INBOX),
            )

            self.task_service.create_task(task_data)
            self._cancel_add_task(None)
            self.refresh()
        except Exception:
            self._show_error("タスクの作成に失敗しました")

    def _cancel_add_task(self, _: ft.ControlEvent | None) -> None:
        """タスク追加をキャンセル"""
        self.current_mode = "list"
        self._build_content_area()
        self.update()

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示

        Args:
            message: エラーメッセージ
        """
        from loguru import logger

        # [AI GENERATED] エラー表示の実装は後で追加
        logger.error(f"UI Error: {message}")

    def refresh(self) -> None:
        """コンテンツを再読み込み"""
        # [AI GENERATED] 現在のフィルタ状態に基づいてタスクリストを再読み込み
        if self.current_filter_status is not None:
            try:
                self.current_tasks = self.task_service.get_tasks_by_status(self.current_filter_status)
            except Exception:
                self._show_error("タスクの再読み込みに失敗しました")

        self._build_content_area()
        self.update()
