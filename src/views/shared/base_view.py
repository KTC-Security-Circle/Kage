"""共通のベースViewクラスと関連ミックスイン群。

OpenSpec `organize-view-layer` の `base-view-contract` 仕様に準拠した
標準インターフェイス (state / notify_error / with_loading / lifecycle) を提供する。
各 View はビジネスロジックを保持せず Application Service 経由で操作する前提。

提供機能:
    - エラーハンドリング (統一経路 notify_error)
    - ローディング状態管理 (state.loading + with_loading)
    - ライフサイクルフック (did_mount / will_unmount)
    - クリーンアップ (非同期タスクキャンセル)
    - Header生成ヘルパー（統一されたヘッダー作成）

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

from views.shared.components import Header, HeaderButtonData, HeaderData
from views.theme import get_dark_color, get_grey_color, get_light_color

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
        is_dark = getattr(page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=get_dark_color("error") if is_dark else get_light_color("error"),
        )
        page.open(snack_bar)
        page.update()

    def show_info_snackbar(self, message: str = "情報") -> None:
        """情報スナックバーを表示する。"""
        is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=get_dark_color("primary") if is_dark else get_light_color("primary"),
        )
        self.page.open(snack_bar)
        self.page.update()

    def show_success_snackbar(self, message: str = "成功しました") -> None:
        """成功スナックバーを表示する。"""
        is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=get_dark_color("success") if is_dark else get_light_color("success"),
        )
        self.page.open(snack_bar)
        self.page.update()

    def show_snack_bar(self, message: str, bgcolor: str | None = None) -> None:
        """汎用スナックバーを表示する。"""
        if bgcolor is None:
            is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
            bgcolor = get_dark_color("primary") if is_dark else get_light_color("primary")
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor)
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
            page.close(dialog_obj)
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
            is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
            error_color = get_dark_color("error") if is_dark else get_light_color("error")
            text_secondary_color = get_dark_color("text_secondary") if is_dark else get_light_color("text_secondary")
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=error_color, size=48),
                        ft.Text(
                            "ビューの読み込み中にエラーが発生しました",
                            size=16,
                            color=error_color,
                        ),
                        ft.Text(
                            str(e),
                            size=12,
                            color=text_secondary_color,
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
        is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
        error_color = get_dark_color("error") if is_dark else get_light_color("error")
        self.show_snack_bar(message=message, bgcolor=error_color)
        self.safe_update()

    # ---------------------------------------------------------------------
    # Spec: with_loading (sync/async 両対応)
    # ---------------------------------------------------------------------
    def with_loading(
        self,
        fn_or_coro: Callable[[], object] | Awaitable[object],
        user_error_message: str = "処理に失敗しました",
    ) -> object:
        """処理を loading 状態でラップし UI フリーズを防ぐ。

        Args:
            fn_or_coro: 実行する関数またはコルーチン
            user_error_message: エラー時のユーザー向けメッセージ

        Returns:
            同期関数の場合は関数の戻り値、非同期の場合はNone
        """
        self.state = replace(self.state, loading=True)
        self.safe_update()

        async def _runner_async(coro: Awaitable[object]) -> None:
            try:
                await coro
            except Exception as e:
                # 既知例外判定: user_message 属性があれば使用
                msg = getattr(e, "user_message", user_error_message)
                self.notify_error(msg, details=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
            finally:
                self.state = replace(self.state, loading=False)
                self.safe_update()

        def _runner_sync(fn: Callable[[], object]) -> object:
            try:
                return fn()
            except Exception as e:
                msg = getattr(e, "user_message", user_error_message)
                self.notify_error(msg, details=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
                return None
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
            return None
        return _runner_sync(fn_or_coro)  # type: ignore[arg-type]

    # Convenience: 明示的に state.error_message をクリア
    def clear_error(self) -> None:
        if self.state.error_message:
            self.state = replace(self.state, error_message=None)
            self.safe_update()

    # ---------------------------------------------------------------------
    # Header生成ヘルパー
    # ---------------------------------------------------------------------
    def create_header(  # noqa: PLR0913
        self,
        *,
        title: str,
        subtitle: str,
        search_placeholder: str = "検索...",
        on_search: Callable[[str], None] | None = None,
        action_buttons: list[HeaderButtonData] | None = None,
        leading_buttons: list[HeaderButtonData] | None = None,
        show_search: bool = True,
    ) -> Header:
        """汎用Headerを生成する。

        Args:
            title: メインタイトル
            subtitle: サブタイトル
            search_placeholder: 検索フィールドのプレースホルダー
            on_search: 検索入力のコールバック
            action_buttons: 右側のアクションボタンのリスト
            leading_buttons: 左側のボタンのリスト（戻るボタン等）
            show_search: 検索フィールドを表示するか

        Returns:
            構築されたHeader
        """
        header_data = HeaderData(
            title=title,
            subtitle=subtitle,
            search_placeholder=search_placeholder,
            on_search=on_search,
            action_buttons=action_buttons,
            leading_buttons=leading_buttons,
            show_search=show_search,
        )
        return Header(header_data)

    # ---------------------------------------------------------------------
    # 統一レイアウトヘルパー
    # ---------------------------------------------------------------------
    def create_standard_layout(
        self,
        *,
        header: ft.Control,
        content: ft.Control,
        status_tabs: ft.Control | None = None,
    ) -> ft.Container:
        """標準的な画面レイアウトを生成する。

        全ビューで統一されたレイアウト構造（padding=24, spacing=16）を提供します。

        Args:
            header: ヘッダーコントロール（通常はcreate_headerで生成）
            content: メインコンテンツコントロール
            status_tabs: ステータスタブコントロール（オプション）

        Returns:
            統一されたレイアウトのContainer

        Example:
            >>> header = self.create_header(title="タスク", subtitle="タスク管理")
            >>> content = ft.ResponsiveRow([...])
            >>> return self.create_standard_layout(header=header, content=content)
        """
        controls = [header]
        if status_tabs is not None:
            controls.append(status_tabs)
        controls.extend([content])

        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def create_two_column_layout(
        self,
        *,
        left_content: ft.Control,
        right_content: ft.Control,
        left_col_size: dict[str, Any] | None = None,
        right_col_size: dict[str, Any] | None = None,
    ) -> ft.ResponsiveRow:
        """2カラムレスポンシブレイアウトを生成する。

        全ビューで統一された2カラム構造を提供します。
        デフォルトは左5:右7の比率で、レスポンシブ対応（xs=12でモバイル時は縦積み）。

        Args:
            left_content: 左カラムのコンテンツ
            right_content: 右カラムのコンテンツ
            left_col_size: 左カラムのサイズ指定（デフォルト: {"xs": 12, "lg": 5}）
            right_col_size: 右カラムのサイズ指定（デフォルト: {"xs": 12, "lg": 7}）

        Returns:
            2カラムのResponsiveRow

        Example:
            >>> list_view = ft.Column([...])
            >>> detail_view = ft.Column([...])
            >>> layout = self.create_two_column_layout(left_content=list_view, right_content=detail_view)
        """
        if left_col_size is None:
            left_col_size = {"xs": 12, "lg": 5}
        if right_col_size is None:
            right_col_size = {"xs": 12, "lg": 7}

        return ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=left_content,
                    col=left_col_size,
                    padding=ft.padding.only(right=12),
                ),
                ft.Container(
                    content=right_content,
                    col=right_col_size,
                ),
            ],
            expand=True,
        )


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
            bgcolor=ft.Colors.with_opacity(0.7, get_grey_color(900)),
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
