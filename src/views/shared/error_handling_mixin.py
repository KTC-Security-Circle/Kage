"""エラーハンドリングミックスイン

Viewクラスで統一されたエラーハンドリング機能を提供するミックスインクラス。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable


class ErrorHandlingMixin:
    """エラーハンドリングの共通機能を提供するミックスイン

    このミックスインを継承することで、統一されたエラー表示機能を利用できます。
    Fletのページオブジェクトへのアクセスが必要なため、_pageまたはpageプロパティを持つクラスで使用してください。
    """

    def show_error(self, message: str, details: str | None = None) -> None:
        """エラーメッセージを表示

        統一されたスタイルでエラーメッセージをSnackBarで表示します。

        Args:
            message: 表示するエラーメッセージ
            details: 詳細情報（省略可能）
        """
        page = self._get_page()
        if not page:
            logger.error(f"ページが見つからないため、エラーメッセージを表示できません: {message}")
            return

        try:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_400,
                action="詳細" if details else None,
                action_color=ft.Colors.WHITE,
                on_action=lambda _: self._show_error_details(details) if details else None,
            )
            page.open(snack_bar)
            logger.error(f"エラー表示: {message}")

        except Exception as e:
            logger.error(f"エラーメッセージの表示に失敗: {e}")

    def show_success(self, message: str) -> None:
        """成功メッセージを表示

        統一されたスタイルで成功メッセージをSnackBarで表示します。

        Args:
            message: 表示する成功メッセージ
        """
        page = self._get_page()
        if not page:
            logger.error(f"ページが見つからないため、成功メッセージを表示できません: {message}")
            return

        try:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_400,
            )
            page.open(snack_bar)
            logger.info(f"成功メッセージ表示: {message}")

        except Exception as e:
            logger.error(f"成功メッセージの表示に失敗: {e}")

    def show_warning(self, message: str) -> None:
        """警告メッセージを表示

        統一されたスタイルで警告メッセージをSnackBarで表示します。

        Args:
            message: 表示する警告メッセージ
        """
        page = self._get_page()
        if not page:
            logger.error(f"ページが見つからないため、警告メッセージを表示できません: {message}")
            return

        try:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ORANGE_400,
            )
            page.open(snack_bar)
            logger.warning(f"警告メッセージ表示: {message}")

        except Exception as e:
            logger.error(f"警告メッセージの表示に失敗: {e}")

    def show_info(self, message: str) -> None:
        """情報メッセージを表示

        統一されたスタイルで情報メッセージをSnackBarで表示します。

        Args:
            message: 表示する情報メッセージ
        """
        page = self._get_page()
        if not page:
            logger.error(f"ページが見つからないため、情報メッセージを表示できません: {message}")
            return

        try:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_400,
            )
            page.open(snack_bar)
            logger.info(f"情報メッセージ表示: {message}")

        except Exception as e:
            logger.error(f"情報メッセージの表示に失敗: {e}")

    def show_confirm_dialog(
        self,
        title: str,
        content: str,
        on_confirm: Callable[[ft.ControlEvent], None] | None = None,
        on_cancel: Callable[[ft.ControlEvent], None] | None = None,
        confirm_text: str = "確認",
        cancel_text: str = "キャンセル",
    ) -> None:
        """確認ダイアログを表示

        統一されたスタイルで確認ダイアログを表示します。

        Args:
            title: ダイアログのタイトル
            content: ダイアログの内容
            on_confirm: 確認ボタンクリック時のコールバック
            on_cancel: キャンセルボタンクリック時のコールバック
            confirm_text: 確認ボタンのテキスト
            cancel_text: キャンセルボタンのテキスト
        """
        page = self._get_page()
        if not page:
            logger.error(f"ページが見つからないため、確認ダイアログを表示できません: {title}")
            return

        def handle_confirm(e: ft.ControlEvent) -> None:
            page.close(confirm_dialog)
            if on_confirm:
                on_confirm(e)

        def handle_cancel(e: ft.ControlEvent) -> None:
            page.close(confirm_dialog)
            if on_cancel:
                on_cancel(e)

        try:
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(content),
                actions=[
                    ft.TextButton(
                        text=cancel_text,
                        on_click=handle_cancel,
                    ),
                    ft.ElevatedButton(
                        text=confirm_text,
                        icon=ft.Icons.CHECK,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_500,
                        on_click=handle_confirm,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.open(confirm_dialog)
            logger.info(f"確認ダイアログ表示: {title}")

        except Exception as e:
            logger.error(f"確認ダイアログの表示に失敗: {e}")

    def _show_error_details(self, details: str) -> None:
        """エラーの詳細情報を表示

        Args:
            details: 表示する詳細情報
        """
        page = self._get_page()
        if not page or not details:
            return

        try:
            details_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("エラー詳細"),
                content=ft.Container(
                    content=ft.Text(details, selectable=True),
                    width=400,
                    height=200,
                ),
                actions=[
                    ft.TextButton(
                        text="閉じる",
                        on_click=lambda _: page.close(details_dialog),
                    ),
                ],
            )

            page.open(details_dialog)

        except Exception as e:
            logger.error(f"エラー詳細の表示に失敗: {e}")

    def _get_page(self) -> ft.Page | None:
        """Fletページオブジェクトを取得

        _pageまたはpageプロパティからページオブジェクトを取得します。

        Returns:
            ft.Page | None: Fletのページオブジェクト、見つからない場合はNone
        """
        # 複数のプロパティ名をチェック
        for attr_name in ["_page", "page"]:
            if hasattr(self, attr_name):
                page = getattr(self, attr_name)
                if isinstance(page, ft.Page):
                    return page

        logger.error(f"{self.__class__.__name__}にページオブジェクトが見つかりません")
        return None
