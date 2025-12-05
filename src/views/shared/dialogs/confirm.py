"""確認ダイアログモジュール

ユーザーの確認が必要な操作で使用するダイアログを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import get_error_color, get_grey_color, get_on_primary_color

from .base import BaseDialog

if TYPE_CHECKING:
    from collections.abc import Callable


# SPACINGの定数定義
class SPACING:
    sm = 8
    md = 16
    lg = 24


class ConfirmDialog(BaseDialog):
    """確認ダイアログクラス。

    ユーザーの確認が必要な操作（削除、変更の取り消し等）で使用します。
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        message: str,
        *,
        confirm_text: str = "確認",
        cancel_text: str = "キャンセル",
        on_result: Callable[[bool], None] | None = None,
    ) -> None:
        """ConfirmDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            title: ダイアログのタイトル
            message: 確認メッセージ
            confirm_text: 確認ボタンのテキスト
            cancel_text: キャンセルボタンのテキスト
            confirm_color: 確認ボタンの色（危険な操作の場合はget_error_color()等）
            on_result: 結果を受け取るコールバック関数（True: 確認, False: キャンセル）
        """
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = None  # デフォルト値

        super().__init__(page, title, on_result=on_result)

    def _build_content(self) -> ft.Control:
        """ダイアログのコンテンツを構築する。

        Returns:
            確認メッセージを表示するコンテンツ
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        self.message,
                        size=16,
                        text_align=ft.TextAlign.LEFT,
                    ),
                ],
                spacing=SPACING.md,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.sm),
        )

    def _build_actions(self) -> list[ft.Control]:
        """ダイアログのアクションボタンを構築する。

        Returns:
            キャンセルと確認ボタンのリスト
        """
        # キャンセルボタン
        cancel_button = self._create_button(
            self.cancel_text,
            on_click=lambda _: self._on_cancel_clicked(),
        )

        # 確認ボタン
        confirm_button = self._create_button(
            self.confirm_text,
            on_click=lambda _: self._on_confirm_clicked(),
            is_primary=True,
        )

        # 危険な操作の場合は赤色にする
        if self.confirm_color:
            confirm_button.style = ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: get_on_primary_color()},
                bgcolor={ft.ControlState.DEFAULT: self.confirm_color},
            )

        return [cancel_button, confirm_button]

    def _on_confirm(self, *, result: bool) -> None:
        """確定ボタンが押された時の処理（ConfirmDialog専用）。

        Args:
            result: ダイアログの結果（True: 確認, False: キャンセル）
        """
        self.hide()
        if self.on_result:
            self.on_result(result)

    def _on_confirm_clicked(self) -> None:
        """確認ボタンがクリックされた時の処理。"""
        self._on_confirm(result=True)

    def _on_cancel_clicked(self) -> None:
        """キャンセルボタンがクリックされた時の処理。"""
        self._on_confirm(result=False)


class DeleteConfirmDialog(ConfirmDialog):
    """削除確認専用ダイアログ。

    削除操作に特化した確認ダイアログです。
    危険性を表すため赤色のボタンと警告アイコンを使用します。
    """

    def __init__(
        self,
        page: ft.Page,
        item_name: str,
        *,
        item_type: str = "項目",
        on_result: Callable[[bool], None] | None = None,
    ) -> None:
        """DeleteConfirmDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            item_name: 削除対象の名前
            item_type: 削除対象の種類（プロジェクト、タスク、タグ等）
            on_result: 結果を受け取るコールバック関数
        """
        title = f"{item_type}の削除"
        message = f"「{item_name}」を削除しますか？\n\nこの操作は取り消すことができません。"

        super().__init__(
            page,
            title,
            message,
            confirm_text="削除",
            cancel_text="キャンセル",
            on_result=on_result,
        )

    def _build_content(self) -> ft.Control:
        """削除確認専用のコンテンツを構築する。

        Returns:
            警告アイコン付きの確認メッセージ
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.WARNING,
                                color=get_error_color(),
                                size=32,
                            ),
                            ft.Text(
                                self.message,
                                size=16,
                                text_align=ft.TextAlign.LEFT,
                                expand=True,
                            ),
                        ],
                        spacing=SPACING.md,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=SPACING.md,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.sm),
        )


class UnsavedChangesDialog(ConfirmDialog):
    """未保存変更確認ダイアログ。

    フォームの変更が未保存のまま画面を離れる際の確認ダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        *,
        on_result: Callable[[bool], None] | None = None,
    ) -> None:
        """UnsavedChangesDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            on_result: 結果を受け取るコールバック関数
        """
        title = "未保存の変更があります"
        message = "変更内容が保存されていません。\n保存せずに続行しますか？"

        super().__init__(
            page,
            title,
            message,
            confirm_text="続行",
            cancel_text="キャンセル",
            on_result=on_result,
        )

    def _build_content(self) -> ft.Control:
        """未保存変更確認専用のコンテンツを構築する。

        Returns:
            情報アイコン付きの確認メッセージ
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INFO,
                                color=get_grey_color(600),
                                size=32,
                            ),
                            ft.Text(
                                self.message,
                                size=16,
                                text_align=ft.TextAlign.LEFT,
                                expand=True,
                            ),
                        ],
                        spacing=SPACING.md,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=SPACING.md,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.sm),
        )
