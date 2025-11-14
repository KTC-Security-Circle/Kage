"""共通のベースViewクラスと関連ミックスイン群。

OpenSpec `organize-view-layer` の `base-view-contract` 仕様に準拠した
標準インターフェイス (state / notify_error / with_loading / lifecycle) を提供する。
各 View はビジネスロジックを保持せず Application Service 経由で操作する前提。

提供機能:
    - エラーハンドリング (統一経路 notify_error)
    - ローディング状態管理 (state.loading + with_loading)
    - ライフサイクルフック (did_mount / will_unmount)
    - クリーンアップ (非同期タスクキャンセル)

今後の拡張ポイント:
    - グローバルメッセージ購読
    - AsyncExecutor 改善 (現在は簡易実装)
"""

from __future__ import annotations

import inspect
import traceback
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from asyncio import Task
    from collections.abc import Awaitable, Callable

    from logic.application.apps import ApplicationServices


class ErrorHandlingMixin:
    """エラーハンドリング機能を提供するミックスイン。

    BaseView から利用される前提で `self.page` を持つ。Flet Page には
    dialog/snack_bar を動的に設定するため安全に ``setattr`` を使用する。
    """

    page: ft.Page

    def show_error_dialog(
        self,
        page: ft.Page,
        title: str = "エラー",
        message: str = "予期しないエラーが発生しました。",
    ) -> None:
        """エラーダイアログを表示する。"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(page)),
            ],
        )
        page.open(dialog)
        page.update()

    def show_error_snackbar(self, page: ft.Page, message: str = "エラーが発生しました") -> None:
        """エラースナックバーを表示する。"""
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.ERROR)
        page.open(snack_bar)
        page.update()

    def show_info_snackbar(self, message: str = "情報") -> None:
        """情報スナックバーを表示する。"""
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.BLUE)
        self.page.open(snack_bar)
        self.page.update()

    def show_success_snackbar(self, message: str = "成功しました") -> None:
        """成功スナックバーを表示する。"""
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREEN)
        self.page.open(snack_bar)
        self.page.update()

    def show_snack_bar(self, message: str, bgcolor: str | None = None) -> None:
        """汎用スナックバーを表示する。"""
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor or ft.Colors.PRIMARY)
        self.page.open(snack_bar)
        self.page.update()

    def handle_exception_with_dialog(
        self, page: ft.Page, exception: Exception, user_message: str | None = None
    ) -> None:
        """例外を処理し、ダイアログでユーザーに通知する。"""
        logger.error(
            f"Exception occurred: {type(exception).__name__}: {exception}\nTraceback: {traceback.format_exc()}"
        )
        display_message = user_message or f"エラーが発生しました: {exception!s}"
        self.show_error_dialog(page, message=display_message)

    def handle_exception_with_snackbar(
        self, page: ft.Page, exception: Exception, user_message: str | None = None
    ) -> None:
        """例外を処理し、スナックバーでユーザーに通知する。"""
        logger.error(
            f"Exception occurred: {type(exception).__name__}: {exception}\nTraceback: {traceback.format_exc()}"
        )
        display_message = user_message or f"エラーが発生しました: {exception!s}"
        self.show_error_snackbar(page, message=display_message)

    def _close_dialog(self, page: ft.Page) -> None:
        """ダイアログを閉じる。"""
        dialog_obj = getattr(page, "dialog", None)
        if dialog_obj:
            dialog_obj.open = False
            page.update()


@dataclass(slots=True)
class BaseViewState:
    """View 共通状態 (spec: base-view-contract).

    loading: 非同期/重い処理中かどうか
    error_message: ユーザ表示用の最新エラーメッセージ (None で非表示)
    """

    loading: bool = False
    error_message: str | None = None


@dataclass(slots=True)
class BaseViewProps:
    """View 共通プロパティ.

    - page: Flet ページインスタンス
    - apps: アプリケーションサービスのコンテナ
    """

    page: ft.Page
    apps: ApplicationServices


class BaseView(ft.Container, ErrorHandlingMixin):
    """全 View の共通基底クラス (spec: base-view-contract).

    - `state`: dataclass で loading / error_message を保持
    - `notify_error()`: ログ + ユーザ通知単一経路
    - `with_loading()`: 処理ラップ (同期/非同期両対応)
    - Lifecycle: did_mount / will_unmount
    - Cleanup: 実行中タスクキャンセル
    """

    def __init__(self, props: BaseViewProps) -> None:
        super().__init__()
        self.page: ft.Page = props.page
        self.is_mounted: bool = False
        self.state: BaseViewState = BaseViewState()
        self.apps = props.apps
        # 実行中タスク (async) を保持し unmount 時にキャンセル
        # 非同期タスク保持 (TYPE_CHECKING で Task インポート)
        self._running_tasks: list[Task[Any]] = []

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
        """アンマウント時のクリーンアップ (spec: Cleanup On Unmount)."""
        self.is_mounted = False
        # 実行中タスクをキャンセル
        for task in list(self._running_tasks):
            if not task.done():
                task.cancel()
        self._running_tasks.clear()
        logger.debug(f"{self.__class__.__name__} unmounted & tasks cancelled")
        # 追加予定: グローバル購読解除

    def build(self) -> ft.Control:
        """UIを構築する。

        Returns:
            構築されたコントロール

        Notes:
            サブクラスでbuild_contentをオーバーライドしてください。
        """
        try:
            return self.build_content()
        except Exception as e:
            logger.error(f"Error building view {self.__class__.__name__}: {e}")
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR, size=48),
                        ft.Text(
                            "ビューの読み込み中にエラーが発生しました",
                            size=16,
                            color=ft.Colors.ERROR,
                        ),
                        ft.Text(
                            str(e),
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=ft.padding.all(32),
                alignment=ft.alignment.center,
            )

    def build_content(self) -> ft.Control:
        """サブクラスでオーバーライドされるべきコンテンツ構築関数。"""
        return ft.Text("BaseView - サブクラスでbuild_contentをオーバーライドしてください")

    def safe_update(self) -> None:
        """安全にページを更新する (内部 state 変更後)。"""
        if not (self.is_mounted and self.page):
            return
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

    # ---------------------------------------------------------------------
    # Spec: notify_error (Logging & User Messaging Policy)
    # ---------------------------------------------------------------------
    def notify_error(self, message: str, details: str | None = None) -> None:
        """エラー通知とログ出力を単一経路で実行する。

        Args:
            message: ユーザに表示するメッセージ (内部情報を含めない)
            details: ログ専用の追加詳細 (例外トレースなど)
        """
        # state 更新
        self.state = replace(self.state, error_message=message)
        logger.error(details or message)
        # SnackBar で通知 (ダイアログ等への差し替えは将来拡張)
        self.show_snack_bar(message=message, bgcolor=ft.Colors.ERROR)
        self.safe_update()

    # ---------------------------------------------------------------------
    # Spec: with_loading (sync/async 両対応)
    # ---------------------------------------------------------------------
    def with_loading(
        self,
        fn_or_coro: Callable[[], Any] | Awaitable[Any],
        user_error_message: str = "処理に失敗しました",
    ) -> None:
        """処理を loading 状態でラップし UI フリーズを防ぐ。"""
        self.state = replace(self.state, loading=True)
        self.safe_update()

        async def _runner_async(coro: Awaitable[Any]) -> None:
            try:
                await coro
            except Exception as e:
                # 既知例外判定: user_message 属性があれば使用
                msg = getattr(e, "user_message", user_error_message)
                self.notify_error(msg, details=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
            finally:
                self.state = replace(self.state, loading=False)
                self.safe_update()

        def _runner_sync(fn: Callable[[], Any]) -> None:
            try:
                fn()
            except Exception as e:
                msg = getattr(e, "user_message", user_error_message)
                self.notify_error(msg, details=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
            finally:
                self.state = replace(self.state, loading=False)
                self.safe_update()

        if inspect.isawaitable(fn_or_coro):
            # Adapter 経由でスケジュール（将来差し替えを容易にするため）
            from views.shared.async_executor import AsyncExecutor

            task = AsyncExecutor.run(_runner_async(fn_or_coro))
            self._running_tasks.append(task)
            # タスク終了後クリーンアップ
            task.add_done_callback(lambda t: self._running_tasks.remove(t) if t in self._running_tasks else None)
        else:
            _runner_sync(fn_or_coro)  # type: ignore[arg-type]

    # Convenience: 明示的に state.error_message をクリア
    def clear_error(self) -> None:
        if self.state.error_message:
            self.state = replace(self.state, error_message=None)
            self.safe_update()


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
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
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
