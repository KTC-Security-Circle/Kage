"""タスク作成・編集ダイアログ

タスクのCRUD操作のためのダイアログコンポーネント。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

from views_new.shared.dialogs.base import BaseDialog


class TaskDialog(BaseDialog):
    """タスク作成・編集用のダイアログ。

    BaseDialogを継承し、タスクの詳細情報を入力するフォームを提供。
    """

    def __init__(
        self,
        page: ft.Page,  # type: ignore[name-defined]
        title: str,
        task_data: dict[str, str] | None = None,
        on_submit: Callable[[dict[str, str]], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        """TaskDialogを初期化する。

        Args:
            page: Fletページインスタンス
            title: ダイアログのタイトル
            task_data: 編集時の既存タスクデータ
            on_submit: 送信時のコールバック
            on_cancel: キャンセル時のコールバック
        """
        super().__init__(page, title)

        self.task_data = task_data or {}
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel

        # フォームフィールド
        self.title_field: ft.TextField | None = None  # type: ignore[name-defined]
        self.description_field: ft.TextField | None = None  # type: ignore[name-defined]
        self.status_dropdown: ft.Dropdown | None = None  # type: ignore[name-defined]
        self.priority_dropdown: ft.Dropdown | None = None  # type: ignore[name-defined]
        self.due_date_field: ft.TextField | None = None  # type: ignore[name-defined]
        self.assignee_field: ft.TextField | None = None  # type: ignore[name-defined]

        # ダイアログの設定
        self.modal = True
        self.title = ft.Text(title, size=20, weight=ft.FontWeight.BOLD)  # type: ignore[name-defined]
        self.content = self._build_content()
        self.actions = self._build_actions()

    def _build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """ダイアログのコンテンツを構築する。

        Returns:
            ダイアログのメインコンテンツ
        """
        import flet as ft

        form_controls = self._build_form_content()

        return ft.Container(
            content=ft.Column(
                controls=form_controls,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                height=500,
            ),
            width=600,
            padding=ft.padding.all(20),
        )

    def _build_actions(self) -> list[ft.Control]:  # type: ignore[name-defined]
        """ダイアログのアクションボタンを構築する。

        Returns:
            アクションボタンのリスト
        """
        import flet as ft

        return [
            ft.TextButton("キャンセル", on_click=self._handle_cancel),
            ft.ElevatedButton(
                "保存",
                on_click=self._handle_submit,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600,
                ),
            ),
        ]

    def _build_form_content(self) -> list[ft.Control]:  # type: ignore[name-defined]
        """フォームコンテンツを構築する。

        Returns:
            フォームコントロールのリスト
        """
        import flet as ft

        # タイトルフィールド
        self.title_field = ft.TextField(
            label="タスクタイトル",
            hint_text="タスクの名前を入力してください",
            value=self.task_data.get("title", ""),
            autofocus=True,
            max_length=100,
            helper_text="必須項目",
        )

        # 説明フィールド
        self.description_field = ft.TextField(
            label="説明",
            hint_text="タスクの詳細説明を入力してください",
            value=self.task_data.get("description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            max_length=500,
        )

        # ステータスドロップダウン
        self.status_dropdown = ft.Dropdown(
            label="ステータス",
            value=self.task_data.get("status", "計画中"),
            options=[
                ft.dropdown.Option("計画中"),
                ft.dropdown.Option("進行中"),
                ft.dropdown.Option("完了"),
                ft.dropdown.Option("保留"),
                ft.dropdown.Option("キャンセル"),
            ],
        )

        # 優先度ドロップダウン
        self.priority_dropdown = ft.Dropdown(
            label="優先度",
            value=self.task_data.get("priority", "medium"),
            options=[
                ft.dropdown.Option("high", "高"),
                ft.dropdown.Option("medium", "中"),
                ft.dropdown.Option("low", "低"),
            ],
        )

        # 期限日フィールド
        self.due_date_field = ft.TextField(
            label="期限日",
            hint_text="YYYY-MM-DD",
            value=self.task_data.get("due_date", ""),
            helper_text="形式: 2024-12-31",
        )

        # 担当者フィールド
        self.assignee_field = ft.TextField(
            label="担当者",
            hint_text="担当者名を入力してください",
            value=self.task_data.get("assignee", ""),
        )

        return [
            # 基本情報セクション
            ft.Text(
                "基本情報",
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                color=ft.Colors.GREY_800,
                weight=ft.FontWeight.BOLD,
            ),
            self.title_field,
            self.description_field,
            ft.Divider(height=20),
            # ステータス・優先度セクション
            ft.Text(
                "ステータス・優先度",
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                color=ft.Colors.GREY_800,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                controls=[
                    ft.Container(content=self.status_dropdown, expand=True),
                    ft.Container(content=self.priority_dropdown, expand=True),
                ],
                spacing=16,
            ),
            ft.Divider(height=20),
            # その他の情報セクション
            ft.Text(
                "その他の情報",
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                color=ft.Colors.GREY_800,
                weight=ft.FontWeight.BOLD,
            ),
            self.due_date_field,
            self.assignee_field,
        ]

    def _validate_form(self) -> tuple[bool, str]:
        """フォームのバリデーションを実行する。

        Returns:
            バリデーション結果のタプル（成功/失敗, エラーメッセージ）
        """
        # タイトルの必須チェック
        if not self.title_field or not self.title_field.value or not self.title_field.value.strip():
            return False, "タスクタイトルは必須です"

        # 期限日の形式チェック
        if self.due_date_field and self.due_date_field.value:
            date_value = self.due_date_field.value.strip()
            if date_value:
                try:
                    import re

                    # 簡単な正規表現による日付形式チェック
                    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_value):
                        return False, "期限日は YYYY-MM-DD 形式で入力してください"
                except Exception:
                    return False, "期限日の形式が正しくありません"

        return True, ""

    def _get_form_data(self) -> dict[str, str]:
        """フォームデータを取得する。

        Returns:
            フォームの入力値を含む辞書
        """
        return {
            "id": self.task_data.get("id", ""),
            "title": self.title_field.value.strip() if self.title_field and self.title_field.value else "",
            "description": (
                self.description_field.value.strip() if self.description_field and self.description_field.value else ""
            ),
            "status": self.status_dropdown.value if self.status_dropdown and self.status_dropdown.value else "計画中",
            "priority": (
                self.priority_dropdown.value if self.priority_dropdown and self.priority_dropdown.value else "medium"
            ),
            "due_date": (
                self.due_date_field.value.strip() if self.due_date_field and self.due_date_field.value else ""
            ),
            "assignee": (
                self.assignee_field.value.strip() if self.assignee_field and self.assignee_field.value else ""
            ),
        }

    def _handle_submit(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """送信処理を実行する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # バリデーション実行
        is_valid, error_message = self._validate_form()
        if not is_valid:
            # エラースナックバーを表示
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_message),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        # フォームデータを取得してコールバック実行
        form_data = self._get_form_data()
        if self.on_submit_callback:
            self.on_submit_callback(form_data)

        # ダイアログを閉じる
        self._close_dialog()

    def _handle_cancel(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """キャンセル処理を実行する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        if self.on_cancel_callback:
            self.on_cancel_callback()

        self._close_dialog()

    def _close_dialog(self) -> None:
        """ダイアログを閉じる。"""
        if self.page:
            self.open = False
            if self in self.page.overlay:
                self.page.overlay.remove(self)
            self.page.update()


def create_task_dialog(
    page: ft.Page,  # type: ignore[name-defined]
    title: str = "新規タスク作成",
    task_data: dict[str, str] | None = None,
    on_submit: Callable[[dict[str, str]], None] | None = None,
    on_cancel: Callable[[], None] | None = None,
) -> TaskDialog:
    """タスクダイアログを作成する。

    Args:
        page: Fletページインスタンス
        title: ダイアログのタイトル
        task_data: 編集時の既存タスクデータ
        on_submit: 送信時のコールバック
        on_cancel: キャンセル時のコールバック

    Returns:
        TaskDialogインスタンス
    """
    return TaskDialog(
        page=page,
        title=title,
        task_data=task_data,
        on_submit=on_submit,
        on_cancel=on_cancel,
    )
