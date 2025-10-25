"""共通のベースViewクラスとエラーハンドリングミックスイン。

このモジュールは、全てのViewクラスが継承する基底クラスと、
エラーハンドリング、ライフサイクル管理等の共通機能を提供します。
"""

from __future__ import annotations

import traceback

import flet as ft
from loguru import logger


class ErrorHandlingMixin:
    """エラーハンドリング機能を提供するミックスイン。

    このミックスインは、統一されたエラー表示とログ記録機能を提供します。
    例外処理、ユーザー通知、デバッグログの出力を一元化します。
    """

    def show_error_dialog(
        self,
        page: ft.Page,
        title: str = "エラー",
        message: str = "予期しないエラーが発生しました。",
    ) -> None:
        """エラーダイアログを表示する。

        Args:
            page: Fletページオブジェクト
            title: ダイアログのタイトル
            message: エラーメッセージ
        """
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda _: self._close_dialog(page),
                ),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def show_error_snackbar(
        self,
        page: ft.Page,
        message: str = "エラーが発生しました",
    ) -> None:
        """エラースナックバーを表示する。

        Args:
            page: Fletページオブジェクト
            message: エラーメッセージ
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.ERROR,
        )
        page.snack_bar = snack_bar
        snack_bar.open = True
        page.update()

    def show_info_snackbar(
        self,
        message: str = "情報",
    ) -> None:
        """情報スナックバーを表示する。

        Args:
            message: 情報メッセージ
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.BLUE,
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def show_success_snackbar(
        self,
        message: str = "成功しました",
    ) -> None:
        """成功スナックバーを表示する。

        Args:
            message: 成功メッセージ
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN,
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def handle_exception_with_dialog(
        self,
        page: ft.Page,
        exception: Exception,
        user_message: str | None = None,
    ) -> None:
        """例外を処理し、ダイアログでユーザーに通知する。

        Args:
            page: Fletページオブジェクト
            exception: 発生した例外
            user_message: ユーザーに表示するメッセージ
        """
        # ログ記録
        logger.error(
            f"Exception occurred: {type(exception).__name__}: {exception}\nTraceback: {traceback.format_exc()}"
        )

        # ダイアログでユーザー通知
        display_message = user_message or f"エラーが発生しました: {exception!s}"
        self.show_error_dialog(page, message=display_message)

    def handle_exception_with_snackbar(
        self,
        page: ft.Page,
        exception: Exception,
        user_message: str | None = None,
    ) -> None:
        """例外を処理し、スナックバーでユーザーに通知する。

        Args:
            page: Fletページオブジェクト
            exception: 発生した例外
            user_message: ユーザーに表示するメッセージ
        """
        # ログ記録
        logger.error(
            f"Exception occurred: {type(exception).__name__}: {exception}\nTraceback: {traceback.format_exc()}"
        )

        # スナックバーでユーザー通知
        display_message = user_message or f"エラーが発生しました: {exception!s}"
        self.show_error_snackbar(page, message=display_message)

    def _close_dialog(self, page: ft.Page) -> None:
        """ダイアログを閉じる。

        Args:
            page: Fletページオブジェクト
        """
        if page.dialog:
            page.dialog.open = False
            page.update()


class BaseView(ft.Container, ErrorHandlingMixin):
    """全Viewの共通基底クラス。

    このクラスは、ライフサイクル管理、エラーハンドリング、
    共通のUI管理機能を提供します。全てのViewはこのクラスを継承します。

    Attributes:
        page: Fletページオブジェクト
        is_mounted: マウント状態を表すフラグ
    """

    def __init__(self, page: ft.Page) -> None:
        """BaseViewを初期化する。

        Args:
            page: Fletページオブジェクト
        """
        super().__init__()
        self.page = page
        self.is_mounted = False

    def did_mount(self) -> None:  # type: ignore[override]
        """マウント時に呼び出される。

        ViewがUIツリーに追加された際の初期化処理を行います。
        必要に応じてサブクラスでオーバーライドしてください。
        """
        self.is_mounted = True
        logger.debug(f"{self.__class__.__name__} mounted")

        # TODO: グローバルメッセージ購読機能を統合フェーズで追加
        # 理由: Pub/Subシステムが未実装のため
        # 置換先: page.pubsub.subscribe(self._on_global_message)

    def will_unmount(self) -> None:  # type: ignore[override]
        """アンマウント時に呼び出される。

        ViewがUIツリーから削除される際のクリーンアップ処理を行います。
        必要に応じてサブクラスでオーバーライドしてください。
        """
        self.is_mounted = False
        logger.debug(f"{self.__class__.__name__} unmounted")

        # TODO: グローバルメッセージ購読解除機能を統合フェーズで追加
        # 理由: Pub/Subシステムが未実装のため
        # 置換先: page.pubsub.unsubscribe(self._on_global_message)

    def build(self) -> ft.Control:
        """UIを構築する。

        Returns:
            構築されたコントロール

        Notes:
            サブクラスで必ずオーバーライドしてください。
        """
        return ft.Text("BaseView - サブクラスでオーバーライドしてください")

    def safe_update(self) -> None:
        """安全にページを更新する。

        マウント状態をチェックしてからページ更新を実行します。
        """
        if self.is_mounted and self.page:
            try:
                self.page.update()
            except Exception as e:
                logger.error(f"Failed to update page: {e}")

    def _on_global_message(self, message: object) -> None:
        """グローバルメッセージを受信する。

        Args:
            message: 受信したメッセージ

        Notes:
            必要に応じてサブクラスでオーバーライドしてください。
        """
        # TODO: 統合フェーズで実装
        # 理由: グローバル通信仕様が未定義のため
        # 置換先: 具体的なメッセージハンドリングロジック
        logger.debug(f"Global message received: {message}")


class LoadingMixin:
    """ローディング状態管理を提供するミックスイン。

    このミックスインは、非同期処理中のローディング表示機能を提供します。
    """

    def __init__(self) -> None:
        """LoadingMixinを初期化する。"""
        self._is_loading = False
        self._loading_overlay: ft.Control | None = None

    @property
    def is_loading(self) -> bool:
        """ローディング状態を取得する。

        Returns:
            ローディング中の場合True
        """
        return self._is_loading

    def show_loading(self, page: ft.Page, message: str = "読み込み中...") -> None:
        """ローディング表示を開始する。

        Args:
            page: Fletページオブジェクト
            message: ローディングメッセージ
        """
        self._is_loading = True

        self._loading_overlay = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(message),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),
            expand=True,
        )

        # TODO: より適切なローディングオーバーレイ表示方法を統合フェーズで実装
        # 理由: 現在は単純な実装のため、より高度なUX改善が必要
        # 置換先: モーダルオーバーレイやプログレスバー等の実装

        page.update()

    def hide_loading(self, page: ft.Page) -> None:
        """ローディング表示を終了する。

        Args:
            page: Fletページオブジェクト
        """
        self._is_loading = False
        self._loading_overlay = None
        page.update()
