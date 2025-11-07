"""タスク管理画面

カンバンボード形式でのタスク管理機能を提供するメインビュー。
ドラッグ&ドロップ、フィルタ、検索、CRUD機能を含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from models import TaskStatus

if TYPE_CHECKING:
    import flet as ft

from logic.application.task_application_service import TaskApplicationService
from models import TaskStatus
from views.shared.base_view import BaseView
from views.shared.components import create_page_header

from .components import (
    create_action_bar,
    create_kanban_board,
    create_task_dialog,
)


class TasksView(BaseView):
    """タスク管理画面のメインビュー。

    カンバンボード形式でのタスク表示、CRUD操作、検索・フィルタ機能を提供。
    BaseViewを継承し、エラーハンドリングとローディング機能を活用。
    """

    def __init__(self, page: ft.Page) -> None:  # type: ignore[name-defined]
        """TasksViewを初期化する。

        Args:
            page: Fletページインスタンス
        """
        super().__init__(page)

        # TaskApplicationServiceを直接インスタンス化
        self._task_app_service = TaskApplicationService()

        self.tasks_data: dict[str, list[dict[str, any]]] = {}
        self.search_query: str = ""
        self.selected_project: str = ""
        self.selected_tags: set[str] = set()

    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """タスク画面のコンテンツを構築する。

        Returns:
            タスク画面のメインコンテンツ
        """
        import flet as ft

        # 実際のデータを読み込み
        self._load_tasks_data()

        return ft.Container(
            content=ft.Column(
                controls=[
                    create_page_header(
                        title="タスク管理",
                        subtitle=f"合計 {self._get_total_tasks_count()} 件のタスク",
                    ),
                    create_action_bar(
                        on_create=self._handle_create_task,
                        on_search=self._handle_search,
                        on_filter=self._handle_filter,
                        on_refresh=self._handle_refresh,
                    ),
                    create_kanban_board(
                        tasks_data=self.tasks_data,
                        on_task_click=self._handle_task_click,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def _load_tasks_data(self) -> None:
        """TaskApplicationServiceから実際のタスクデータを読み込む。"""
        try:
            # 一時的にモックデータを使用
            self._initialize_mock_data()
            return

            # 各ステータスごにタスクを取得
            status_mapping = {
                "計画中": TaskStatus.TODO,
                "進行中": TaskStatus.PROGRESS,
                "完了": TaskStatus.COMPLETED,
            }

            self.tasks_data = {}

            for display_status, task_status in status_mapping.items():
                tasks = self._task_app_service.list_by_status(task_status)
                self.tasks_data[display_status] = [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description or "",
                        "priority": "medium",  # TODO: 優先度フィールドを追加
                        "project": "",  # TODO: プロジェクト名を取得
                        "tags": [],  # TODO: タグを取得
                        "assignee": "未割当",  # TODO: 担当者フィールドを追加
                        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else "未設定",
                        "created_at": (
                            task.created_at.strftime("%Y-%m-%d")
                            if hasattr(task, "created_at") and task.created_at
                            else ""
                        ),
                    }
                    for task in tasks
                ]

        except Exception as e:
            # エラーが発生した場合はモックデータにフォールバック
            if self.page:
                self.show_snack_bar(f"データ読み込みエラー: {e}")
            self._initialize_mock_data()

    def _initialize_mock_data(self) -> None:
        """開発用のモックデータを初期化する。"""
        self.tasks_data = {
            "計画中": [
                {
                    "id": "1",
                    "title": "新機能の要件定義",
                    "description": "ユーザーからの要望を整理し、機能仕様を策定する",
                    "priority": "high",
                    "project": "ウェブサイトリニューアル",
                    "tags": ["要件定義", "設計"],
                    "assignee": "田中",
                    "due_date": "2024-11-01",
                    "created_at": "2024-10-20",
                },
                {
                    "id": "2",
                    "title": "デザインモックアップ作成",
                    "description": "UI/UXデザインの初期案を作成",
                    "priority": "medium",
                    "project": "モバイルアプリ開発",
                    "tags": ["デザイン", "UI/UX"],
                    "assignee": "佐藤",
                    "due_date": "2024-10-30",
                    "created_at": "2024-10-22",
                },
            ],
            "進行中": [
                {
                    "id": "3",
                    "title": "フロントエンド実装",
                    "description": "Reactコンポーネントの実装",
                    "priority": "high",
                    "project": "ウェブサイトリニューアル",
                    "tags": ["開発", "React"],
                    "assignee": "鈴木",
                    "due_date": "2024-11-05",
                    "created_at": "2024-10-18",
                },
                {
                    "id": "4",
                    "title": "API仕様書作成",
                    "description": "バックエンドAPIの詳細仕様を文書化",
                    "priority": "medium",
                    "project": "データベース最適化",
                    "tags": ["文書化", "API"],
                    "assignee": "高橋",
                    "due_date": "2024-10-28",
                    "created_at": "2024-10-21",
                },
            ],
            "完了": [
                {
                    "id": "5",
                    "title": "環境構築",
                    "description": "開発環境のセットアップ完了",
                    "priority": "low",
                    "project": "モバイルアプリ開発",
                    "tags": ["環境構築"],
                    "assignee": "山田",
                    "due_date": "2024-10-25",
                    "created_at": "2024-10-15",
                },
            ],
        }

    def _get_total_tasks_count(self) -> int:
        """全タスク数を取得する。

        Returns:
            全タスクの総数
        """
        return sum(len(tasks) for tasks in self.tasks_data.values())

    def _handle_create_task(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規タスク作成を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        if not self.page:
            return

        def on_submit(form_data: dict[str, str]) -> None:
            """タスク作成の送信処理。

            Args:
                form_data: フォームから送信されたデータ
            """
            try:
                # TaskApplicationServiceを使用してタスクを作成
                import contextlib

                from models import TaskStatus

                # ステータスの変換
                status_mapping = {
                    "計画中": TaskStatus.TODO,
                    "進行中": TaskStatus.PROGRESS,
                    "完了": TaskStatus.COMPLETED,
                    "保留": TaskStatus.WAITING,
                    "キャンセル": TaskStatus.CANCELED,
                }

                task_status = status_mapping.get(form_data.get("status", "計画中"), TaskStatus.TODO)

                # 期限日の変換 - 日付のみなのでタイムゾーンは不要
                due_date = None
                if form_data.get("due_date"):
                    import re

                    date_str = form_data["due_date"]
                    # 簡単な日付形式チェック
                    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                        with contextlib.suppress(ValueError):
                            year, month, day = map(int, date_str.split("-"))
                            from datetime import date

                            due_date = date(year, month, day)

                # タスクを作成
                task_data = {
                    "title": form_data["title"],
                    "description": form_data.get("description", ""),
                    "status": task_status,
                    "due_date": due_date,
                }

                created_task = self._task_app_service.create(**task_data)

                if created_task:
                    self.show_success_snackbar(f"タスク「{form_data['title']}」を作成しました")
                    # データを再読み込み
                    self._load_tasks_data()
                    if self.page:
                        self.page.update()
                else:
                    self.show_snack_bar("タスクの作成に失敗しました")

            except Exception as e:
                self.show_snack_bar(f"タスク作成エラー: {e}")

        def on_cancel() -> None:
            """キャンセル処理。"""

        # タスク作成ダイアログを表示
        dialog = create_task_dialog(
            page=self.page,
            title="新規タスク作成",
            on_submit=on_submit,
            on_cancel=on_cancel,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _handle_search(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索を処理する。

        Args:
            e: イベントオブジェクト
        """
        # TODO: 検索機能を実装
        search_text = e.control.value if e.control.value else ""  # type: ignore[attr-defined]
        self.search_query = search_text
        if search_text:
            self.show_info_snackbar(f"「{search_text}」の検索機能は準備中です")

    def _handle_filter(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """フィルターを処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: フィルターダイアログを表示
        self.show_info_snackbar("フィルター機能は準備中です")

    def _handle_refresh(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """データ更新を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: 実際のデータ再読み込み
        self._load_tasks_data()
        self.show_info_snackbar("タスクデータを更新しました")
        if self.page:
            self.page.update()

    def _convert_status_to_enum(self, status_str: str) -> TaskStatus:
        """文字列ステータスをTaskStatusに変換する。

        Args:
            status_str: ステータス文字列

        Returns:
            TaskStatus enum値
        """
        from models import TaskStatus

        status_mapping = {
            "計画中": TaskStatus.TODO,
            "進行中": TaskStatus.PROGRESS,
            "完了": TaskStatus.COMPLETED,
            "保留": TaskStatus.WAITING,
            "キャンセル": TaskStatus.CANCELED,
        }
        return status_mapping.get(status_str, TaskStatus.TODO)

    def _parse_due_date(self, date_str: str) -> date | None:
        """期限日文字列をdateオブジェクトに変換する。

        Args:
            date_str: 日付文字列（YYYY-MM-DD形式）

        Returns:
            dateオブジェクト、変換できない場合はNone
        """
        import contextlib
        import re
        from datetime import date

        if not date_str or not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return None

        with contextlib.suppress(ValueError):
            year, month, day = map(int, date_str.split("-"))
            return date(year, month, day)
        return None

    def _update_task_with_data(self, form_data: dict[str, str]) -> bool:
        """フォームデータでタスクを更新する。

        Args:
            form_data: フォームから送信されたデータ

        Returns:
            更新に成功した場合True
        """
        import uuid

        task_id = form_data.get("id")
        if not task_id:
            if self.page:
                self.show_snack_bar("タスクIDが見つかりません")
            return False

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            if self.page:
                self.show_snack_bar("無効なタスクIDです")
            return False

        task_status = self._convert_status_to_enum(form_data.get("status", "計画中"))
        due_date = self._parse_due_date(form_data.get("due_date", ""))

        update_data = {
            "title": form_data["title"],
            "description": form_data.get("description", ""),
            "status": task_status,
            "due_date": due_date,
        }

        updated_task = self._task_app_service.update(task_uuid, **update_data)

        if updated_task:
            if self.page:
                self.show_success_snackbar(f"タスク「{form_data['title']}」を更新しました")
            self._load_tasks_data()
            if self.page:
                self.page.update()
            return True

        if self.page:
            self.show_snack_bar("タスクの更新に失敗しました")
        return False

    def _handle_task_click(self, _: ft.ControlEvent, task: dict[str, str]) -> None:  # type: ignore[name-defined]
        """タスククリックを処理する。

        Args:
            _: イベントオブジェクト（未使用）
            task: クリックされたタスク
        """
        if not self.page:
            return

        def on_submit(form_data: dict[str, str]) -> None:
            """タスク更新の送信処理。

            Args:
                form_data: フォームから送信されたデータ
            """
            try:
                self._update_task_with_data(form_data)
            except Exception as e:
                if self.page:
                    self.show_snack_bar(f"タスク更新エラー: {e}")

        def on_cancel() -> None:
            """キャンセル処理。"""

        # タスク編集ダイアログを表示
        dialog = create_task_dialog(
            page=self.page,
            title=f"タスク編集: {task['title']}",
            task_data=task,
            on_submit=on_submit,
            on_cancel=on_cancel,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _handle_task_move(self, task: dict[str, str], from_status: str, to_status: str) -> None:
        """タスクの移動を処理する。

        Args:
            task: 移動するタスク
            from_status: 移動元のステータス
            to_status: 移動先のステータス
        """
        # TODO: 実際のデータ更新
        if from_status in self.tasks_data and to_status in self.tasks_data:
            # タスクを移動元から削除
            self.tasks_data[from_status] = [t for t in self.tasks_data[from_status] if t["id"] != task["id"]]
            # タスクを移動先に追加
            self.tasks_data[to_status].append(task)

            self.show_info_snackbar(f"タスク「{task['title']}」を{to_status}に移動しました")
            if self.page:
                self.page.update()
