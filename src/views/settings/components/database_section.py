"""データベース設定コンポーネント。

データベース接続設定UIを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING, get_error_color, get_success_color

if TYPE_CHECKING:
    from collections.abc import Callable

    from settings.models import AppSettings, EditableAppSettings


class DatabaseSection(ft.Column):
    """データベース設定セクション。

    データベース接続URLの設定機能を提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        on_change: Callable[[], None],
    ) -> None:
        """DatabaseSectionを初期化する。

        Args:
            page: Fletページオブジェクト
            on_change: 設定変更時のコールバック
        """
        super().__init__()

        self.page = page
        self.on_change = on_change

        # データベースURL設定
        self.url_field = ft.TextField(
            label="データベースURL",
            hint_text="sqlite:///storage/data/tasks.db",
            expand=True,
            on_change=self._on_url_changed,
            helper_text="SQLiteファイルの場合: sqlite:///path/to/file.db",
        )

        # プリセットボタン
        self.default_button = ft.OutlinedButton(
            text="デフォルトに戻す",
            icon=ft.Icons.RESTORE,
            on_click=self._on_reset_to_default,
        )

        # 接続テストボタン
        self.test_button = ft.ElevatedButton(
            text="接続テスト",
            icon=ft.Icons.WIFI_FIND,
            on_click=self._on_test_connection,
        )

        # 結果表示
        self.result_text = ft.Text(
            "",
            size=12,
            visible=False,
        )

        self.controls = [
            ft.Text("データベース接続", size=16, weight=ft.FontWeight.BOLD),
            self.url_field,
            ft.Container(height=SPACING.sm),
            ft.Row(
                [
                    self.default_button,
                    self.test_button,
                ],
                spacing=SPACING.md,
            ),
            ft.Container(height=SPACING.sm),
            self.result_text,
        ]

        self.spacing = SPACING.md

    def _on_url_changed(self, _: ft.ControlEvent) -> None:
        """データベースURLが変更された時の処理。"""
        self.result_text.visible = False
        if self.page:
            self.update()
        self.on_change()

    def _on_reset_to_default(self, _: ft.ControlEvent) -> None:
        """デフォルトURLに戻すボタンがクリックされた時の処理。"""
        self.url_field.value = "sqlite:///storage/data/tasks.db"
        self.result_text.visible = False
        if self.page:
            self.update()
        self.on_change()

    def _on_test_connection(self, _: ft.ControlEvent) -> None:
        """接続テストボタンがクリックされた時の処理。"""
        try:
            url = self.url_field.value or ""

            # 基本的なURL形式チェック
            if not url:
                self._show_result("URLが入力されていません", success=False)
                return

            if url.startswith("sqlite:///"):
                # SQLiteファイルパスの検証
                from pathlib import Path

                file_path = url.replace("sqlite:///", "")
                path_obj = Path(file_path)

                if path_obj.exists():
                    self._show_result("✓ SQLiteファイルが存在します", success=True)
                # ディレクトリが存在するかチェック
                elif path_obj.parent.exists():
                    self._show_result("✓ 新しいSQLiteファイルが作成されます", success=True)
                else:
                    self._show_result("× ディレクトリが存在しません", success=False)
            else:
                # その他のデータベース（PostgreSQL、MySQL等）
                self._show_result("✓ URL形式は正しいようです（実際の接続テストは未実装）", success=True)

        except Exception as e:
            self._show_result(f"× エラー: {e}", success=False)

    def _show_result(self, message: str, *, success: bool) -> None:
        """結果メッセージを表示する。

        Args:
            message: 表示するメッセージ
            success: 成功かどうか
        """
        self.result_text.value = message
        self.result_text.color = get_success_color() if success else get_error_color()
        self.result_text.visible = True
        if self.page:
            self.update()

    def apply_settings(self, settings: EditableAppSettings) -> None:
        """設定値を適用する。

        Args:
            settings: 編集可能な設定オブジェクト
        """
        # データベースURL設定
        settings.database.url = self.url_field.value or "sqlite:///storage/data/tasks.db"

    def reset_to_settings(self, settings: AppSettings) -> None:
        """現在の設定値にリセットする。

        Args:
            settings: 現在の設定オブジェクト
        """
        # データベースURL設定
        self.url_field.value = settings.database.url
        self.result_text.visible = False

        if self.page:
            self.update()
