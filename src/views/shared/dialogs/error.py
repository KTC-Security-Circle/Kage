"""エラーダイアログコンポーネント。

エラー情報の表示、例外の詳細表示等に使用するダイアログです。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.theme import SPACING, get_error_color, get_surface_variant_color

from .base import BaseDialog

if TYPE_CHECKING:
    from collections.abc import Callable


class ErrorDialog(BaseDialog):
    """エラー表示ダイアログクラス。

    エラーメッセージや例外の詳細を表示するダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        title: str,
        message: str,
        *,
        details: str | None = None,
        show_details: bool = False,
        on_result: Callable[[None], None] | None = None,
    ) -> None:
        """ErrorDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            title: エラーダイアログのタイトル
            message: エラーメッセージ
            details: エラーの詳細情報（スタックトレース等）
            show_details: 詳細情報を初期表示するかどうか
            on_result: 結果を受け取るコールバック関数
        """
        self.message = message
        self.details = details
        self.show_details_flag = show_details
        self.details_visible = show_details

        super().__init__(page, title, on_result=on_result)

    def _build_content(self) -> ft.Control:
        """エラーダイアログのコンテンツを構築する。

        Returns:
            エラーメッセージと詳細情報を含むコンテンツ
        """
        content_controls: list[ft.Control] = [
            # エラーアイコンとメッセージ
            ft.Row(
                [
                    ft.Icon(
                        ft.Icons.ERROR,
                        color=get_error_color(),
                        size=32,
                    ),
                    ft.Text(
                        self.message,
                        size=16,
                        text_align=ft.TextAlign.LEFT,
                        expand=True,
                        selectable=True,
                    ),
                ],
                spacing=SPACING.md,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ]

        # 詳細情報がある場合は詳細表示ボタンを追加
        if self.details:
            self.details_button = ft.TextButton(
                text="詳細を表示" if not self.details_visible else "詳細を非表示",
                on_click=lambda _: self._toggle_details(),
            )

            details_button_container: ft.Control = ft.Container(
                content=self.details_button,
                margin=ft.margin.only(top=SPACING.sm),
            )
            content_controls.append(details_button_container)

            # 詳細情報コンテナ
            self.details_container = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "詳細情報:",
                            weight=ft.FontWeight.BOLD,
                            size=14,
                        ),
                        ft.Container(
                            content=ft.Text(
                                self.details,
                                size=12,
                                font_family="monospace",
                                selectable=True,
                                no_wrap=False,
                            ),
                            bgcolor=get_surface_variant_color(),
                            border_radius=4,
                            padding=ft.padding.all(SPACING.sm),
                            width=500,
                            height=200,
                        ),
                    ],
                    spacing=SPACING.sm,
                    tight=True,
                ),
                visible=self.details_visible,
                margin=ft.margin.only(top=SPACING.sm),
            )

            details_ctrl: ft.Control = self.details_container
            content_controls.append(details_ctrl)

        return ft.Container(
            content=ft.Column(
                content_controls,
                spacing=SPACING.md,
                tight=True,
            ),
            padding=ft.padding.all(SPACING.sm),
        )

    def _build_actions(self) -> list[ft.Control]:
        """エラーダイアログのアクションボタンを構築する。

        Returns:
            OKボタンのリスト
        """
        return [
            self._create_button(
                "OK",
                on_click=lambda _: self._on_ok_clicked(),
                is_primary=True,
            ),
        ]

    def _toggle_details(self) -> None:
        """詳細情報の表示/非表示を切り替える。"""
        self.details_visible = not self.details_visible
        self.details_container.visible = self.details_visible
        self.details_button.text = "詳細を非表示" if self.details_visible else "詳細を表示"
        if self.page is not None and hasattr(self.page, "update"):
            self.page.update()

    def _on_ok_clicked(self) -> None:
        """OKボタンがクリックされた時の処理。"""
        self._on_confirm(None)


class CriticalErrorDialog(ErrorDialog):
    """致命的エラー表示ダイアログ。

    アプリケーションの継続が困難な致命的エラーを表示するダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        message: str,
        *,
        details: str | None = None,
        on_result: Callable[[None], None] | None = None,
    ) -> None:
        """CriticalErrorDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            message: エラーメッセージ
            details: エラーの詳細情報
            on_result: 結果を受け取るコールバック関数
        """
        super().__init__(
            page,
            "致命的エラー",
            message,
            details=details,
            show_details=True,
            on_result=on_result,
        )

    def _build_content(self) -> ft.Control:
        """致命的エラー専用のコンテンツを構築する。

        Returns:
            警告色のアイコンと強調されたメッセージ
        """
        content = super()._build_content()

        # アイコンを致命的エラー用に変更
        if (
            isinstance(content, ft.Container)
            and isinstance(content.content, ft.Column)
            and content.content.controls
            and isinstance(content.content.controls[0], ft.Row)
        ):
            first_row = content.content.controls[0]
            if first_row.controls and len(first_row.controls) > 0:
                first_row.controls[0] = ft.Icon(
                    ft.Icons.DANGEROUS,
                    color=ft.Colors.RED,
                    size=40,
                )

        return content


class ValidationErrorDialog(ErrorDialog):
    """バリデーションエラー表示ダイアログ。

    フォーム入力のバリデーションエラーを表示するダイアログです。
    """

    def __init__(
        self,
        page: ft.Page,
        errors: dict[str, str],
        *,
        on_result: Callable[[None], None] | None = None,
    ) -> None:
        """ValidationErrorDialogを初期化する。

        Args:
            page: Fletページオブジェクト
            errors: フィールド名とエラーメッセージのマッピング
            on_result: 結果を受け取るコールバック関数
        """
        # エラーメッセージを整形
        error_list = [f"• {error}" for error in errors.values()]
        message = "入力内容に以下のエラーがあります:\n\n" + "\n".join(error_list)

        super().__init__(
            page,
            "入力エラー",
            message,
            on_result=on_result,
        )

    def _build_content(self) -> ft.Control:
        """バリデーションエラー専用のコンテンツを構築する。

        Returns:
            警告アイコンとエラーリスト
        """
        content = super()._build_content()

        # アイコンを警告用に変更
        if (
            isinstance(content, ft.Container)
            and isinstance(content.content, ft.Column)
            and content.content.controls
            and isinstance(content.content.controls[0], ft.Row)
        ):
            first_row = content.content.controls[0]
            if first_row.controls and len(first_row.controls) > 0:
                first_row.controls[0] = ft.Icon(
                    ft.Icons.WARNING,
                    color=ft.Colors.ORANGE,
                    size=32,
                )

        return content
