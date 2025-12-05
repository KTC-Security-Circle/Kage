"""共通のベースダイアログクラス。

このモジュールは、全てのダイアログコンポーネントが継承する基底クラスを提供します。
一貫性のあるデザイン、アニメーション、キーボード操作を統一的に実装します。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import flet as ft
from loguru import logger

from views.theme import BORDER_RADIUS, SPACING, get_dark_color, get_error_color, get_light_color

if TYPE_CHECKING:
    from collections.abc import Callable


class BaseDialog(ft.AlertDialog, ABC):
    """全ダイアログの共通基底クラス。

    このクラスは、ダイアログの共通機能（テーマ統合、アニメーション、
    キーボード操作、ライフサイクル管理）を提供します。

    Attributes:
        page: Fletページオブジェクト
        title_text: ダイアログのタイトル
        on_result: 結果コールバック関数
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        *,
        modal: bool = True,
        on_result: Callable[[Any], None] | None = None,
    ) -> None:
        """BaseDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            title: ダイアログのタイトル
            modal: モーダル表示するかどうか
            on_result: 結果を受け取るコールバック関数
        """
        super().__init__()

        self.page = page
        self.title_text = title
        self.on_result = on_result

        # ダイアログの基本設定
        self.modal = modal
        self.title = ft.Text(
            title,
            size=20,
            weight=ft.FontWeight.BOLD,
        )

        # テーマに応じたスタイリング
        self._apply_theme_styling()

        # コンテンツとアクションを構築
        self.content = self._build_content()
        self.actions = self._build_actions()

        # ダイアログのサイズ設定
        self.content_padding = ft.padding.all(SPACING.lg)
        self.actions_padding = ft.padding.symmetric(
            horizontal=SPACING.lg,
            vertical=SPACING.md,
        )

        logger.debug(f"BaseDialog created: {title}")

    @abstractmethod
    def _build_content(self) -> ft.Control:
        """ダイアログのコンテンツを構築する。

        Returns:
            ダイアログのメインコンテンツ

        Notes:
            サブクラスで必ずオーバーライドしてください。
        """

    @abstractmethod
    def _build_actions(self) -> list[ft.Control]:
        """ダイアログのアクションボタンを構築する。

        Returns:
            アクションボタンのリスト

        Notes:
            サブクラスで必ずオーバーライドしてください。
        """

    def _apply_theme_styling(self) -> None:
        """テーマに応じたスタイリングを適用する。"""
        # TODO: 統合フェーズでユーザー設定からテーマモードを取得
        # 理由: 設定管理システムが未実装のため
        # 暫定的にライトテーマを使用

        is_dark_mode = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK

        if is_dark_mode:
            self.bgcolor = get_dark_color("surface")
            # TODO: titleのcolorプロパティ設定は統合フェーズで対応
        else:
            self.bgcolor = get_light_color("surface")
            # TODO: titleのcolorプロパティ設定は統合フェーズで対応

        # 影とボーダーの設定
        self.surface_tint_color = ft.Colors.TRANSPARENT  # Transparent is theme-independent
        self.elevation = 24

    def _setup_keyboard_handling(self) -> None:
        """キーボードイベントの設定を行う。

        ESCキーでダイアログを閉じる、Enterキーで確定等の
        標準的なキーボード操作を設定します。
        """
        # TODO: 統合フェーズでキーボードイベントハンドリングを実装
        # 理由: Fletのキーボードイベント処理方法を調査中
        # 置換先: page.on_keyboard_event の設定

    def show(self) -> None:
        """ダイアログを表示する。"""
        if self.page is None:
            logger.warning(f"Cannot show dialog '{self.title_text}': page is None")
            return
        try:
            # Flet のダイアログ表示は page.open(dialog) を利用する
            self.page.open(self)
            self.page.update()
            logger.debug(f"Dialog shown: {self.title_text}")
        except Exception:
            # 互換性がない環境ではダイアログの open フラグを立てて更新を試みる
            self.open = True
            if hasattr(self.page, "update"):
                self.page.update()
            logger.debug(f"Dialog shown (fallback open): {self.title_text}")

    def hide(self) -> None:
        """ダイアログを閉じる。"""
        self.open = False
        if self.page is not None and hasattr(self.page, "update"):
            self.page.update()
        logger.debug(f"Dialog hidden: {self.title_text}")

    def _on_confirm(self, result: dict[str, Any] | str | None) -> None:
        """確定ボタンが押された時の処理。

        Args:
            result: ダイアログの結果データ
        """
        self.hide()
        if self.on_result:
            self.on_result(result)

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理。"""
        self.hide()
        if self.on_result:
            self.on_result(None)

    def _create_button(
        self,
        text: str,
        *,
        on_click: Callable[..., None],
        style: ft.ButtonStyle | None = None,
        is_primary: bool = False,
    ) -> ft.TextButton:
        """統一されたスタイルのボタンを作成する。

        Args:
            text: ボタンのテキスト
            on_click: クリック時のコールバック
            style: カスタムスタイル
            is_primary: プライマリボタンかどうか

        Returns:
            作成されたボタン
        """
        if style is None:
            if is_primary:
                style = ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: get_light_color("on_primary"),
                    },
                    bgcolor={
                        ft.ControlState.DEFAULT: get_light_color("primary"),
                    },
                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS.md),
                )
            else:
                style = ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: get_light_color("primary"),
                    },
                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS.md),
                )

        return ft.TextButton(
            text=text,
            on_click=on_click,
            style=style,
        )


class BaseFormDialog(BaseDialog):
    """フォーム要素を含むダイアログの基底クラス。

    入力フォームや設定変更等、ユーザー入力を伴うダイアログで使用します。
    バリデーション機能やフォーカス管理等の共通機能を提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        *,
        modal: bool = True,
        on_result: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        """BaseFormDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            title: ダイアログのタイトル
            modal: モーダル表示するかどうか
            on_result: 結果を受け取るコールバック関数
        """
        self._form_fields: dict[str, ft.Control] = {}
        self._validation_errors: dict[str, str] = {}

        super().__init__(page, title, modal=modal, on_result=on_result)

    def _add_form_field(self, name: str, field: ft.Control) -> None:
        """フォームフィールドを追加する。

        Args:
            name: フィールド名
            field: フォームコントロール
        """
        self._form_fields[name] = field

    def _validate_form(self) -> bool:
        """フォームのバリデーションを実行する。

        Returns:
            バリデーション成功時True

        Notes:
            サブクラスでオーバーライドして具体的なバリデーションを実装。
        """
        self._validation_errors.clear()
        return True

    def _get_form_data(self) -> dict[str, Any]:
        """フォームデータを取得する。

        Returns:
            フォームの入力データ

        Notes:
            サブクラスでオーバーライドして具体的なデータ取得を実装。
        """
        return {}

    def _show_validation_errors(self) -> None:
        """バリデーションエラーを表示する。"""
        if not self._validation_errors:
            return

        error_messages = "\n".join(self._validation_errors.values())
        if self.page is not None and hasattr(self.page, "snack_bar"):
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(error_messages),
                    bgcolor=get_error_color(),
                )
            )
            if hasattr(self.page, "update"):
                self.page.update()

    def _on_form_submit(self) -> None:
        """フォーム送信時の処理。"""
        if self._validate_form():
            form_data = self._get_form_data()
            self._on_confirm(form_data)
        else:
            self._show_validation_errors()
