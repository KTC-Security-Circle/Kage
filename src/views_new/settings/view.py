"""設定画面のメインビュークラス。

アプリケーション設定の表示・編集機能を提供します。
"""

from __future__ import annotations

import flet as ft
from loguru import logger

from settings.manager import get_config_manager
from views_new.shared.base_view import BaseView
from views_new.shared.dialogs import ConfirmDialog, ErrorDialog
from views_new.theme import SPACING, get_light_color

from .components.appearance_section import AppearanceSection
from .components.database_section import DatabaseSection
from .components.window_section import WindowSection


class SettingsView(BaseView):
    """設定画面のメインビュークラス。

    アプリケーション設定の表示・編集機能を提供します。
    変更は即座に適用され、設定ファイルに保存されます。
    """

    def __init__(self, page: ft.Page) -> None:
        """SettingsViewを初期化する。

        Args:
            page: Fletページオブジェクト
        """
        super().__init__(page)

        # 設定管理
        self.config_manager = get_config_manager()
        self.has_unsaved_changes = False

        # セクションコンポーネント
        self.appearance_section = AppearanceSection(page, self._on_setting_changed)
        self.window_section = WindowSection(page, self._on_setting_changed)
        self.database_section = DatabaseSection(page, self._on_setting_changed)

        # 保存・リセットボタン
        self.save_button = ft.ElevatedButton(
            text="設定を保存",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: get_light_color("primary")},
                color={ft.ControlState.DEFAULT: get_light_color("on_primary")},
            ),
            on_click=self._on_save_settings,
            disabled=True,
        )

        self.reset_button = ft.OutlinedButton(
            text="リセット",
            icon=ft.Icons.REFRESH,
            on_click=self._on_reset_settings,
            disabled=True,
        )

    def build(self) -> ft.Control:
        """設定画面のUIを構築する。

        Returns:
            構築されたUIコントロール
        """
        return ft.Container(
            content=ft.Column(
                [
                    # ページヘッダー
                    self._create_page_header(),
                    # メインコンテンツ
                    ft.Container(
                        content=ft.Column(
                            [
                                # 外観設定
                                self._create_section_card(
                                    "外観",
                                    "テーマとUI設定",
                                    ft.Icons.PALETTE,
                                    self.appearance_section,
                                ),
                                # ウィンドウ設定
                                self._create_section_card(
                                    "ウィンドウ",
                                    "サイズと位置の設定",
                                    ft.Icons.WINDOW,
                                    self.window_section,
                                ),
                                # データベース設定
                                self._create_section_card(
                                    "データベース",
                                    "データベース接続設定",
                                    ft.Icons.STORAGE,
                                    self.database_section,
                                ),
                                # アクションボタン
                                self._create_action_buttons(),
                            ],
                            spacing=SPACING.lg,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                    ),
                ],
                spacing=SPACING.lg,
            ),
            padding=ft.padding.all(SPACING.lg),
            expand=True,
        )

    def _create_page_header(self) -> ft.Container:
        """ページヘッダーを作成する。

        Returns:
            ページヘッダーコンテナ
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SETTINGS, size=32),
                    ft.Text(
                        "設定",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SPACING.md,
            ),
            margin=ft.margin.only(bottom=SPACING.md),
        )

    def _create_section_card(
        self,
        title: str,
        description: str,
        icon: str,
        content: ft.Control,
    ) -> ft.Card:
        """設定セクションカードを作成する。

        Args:
            title: セクションタイトル
            description: セクション説明
            icon: アイコン
            content: セクションコンテンツ

        Returns:
            設定セクションカード
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        # セクションヘッダー
                        ft.Row(
                            [
                                ft.Icon(icon, size=24),
                                ft.Column(
                                    [
                                        ft.Text(
                                            title,
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            description,
                                            size=14,
                                            color=ft.Colors.OUTLINE,
                                        ),
                                    ],
                                    spacing=2,
                                    tight=True,
                                ),
                            ],
                            spacing=SPACING.md,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Divider(),
                        # セクションコンテンツ
                        content,
                    ],
                    spacing=SPACING.md,
                ),
                padding=ft.padding.all(SPACING.lg),
            ),
            elevation=2,
        )

    def _create_action_buttons(self) -> ft.Container:
        """アクションボタンエリアを作成する。

        Returns:
            アクションボタンコンテナ
        """
        return ft.Container(
            content=ft.Row(
                [
                    self.reset_button,
                    self.save_button,
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=SPACING.md,
            ),
            margin=ft.margin.only(top=SPACING.lg),
        )

    def _on_setting_changed(self) -> None:
        """設定値が変更された時の処理。"""
        self.has_unsaved_changes = True
        self.save_button.disabled = False
        self.reset_button.disabled = False
        if hasattr(self.page, "update"):
            self.page.update()

    def _on_save_settings(self, _: ft.ControlEvent) -> None:
        """設定保存ボタンがクリックされた時の処理。"""
        try:
            with self.config_manager.edit() as editable_settings:
                # 各セクションから設定値を取得して適用
                self.appearance_section.apply_settings(editable_settings)
                self.window_section.apply_settings(editable_settings)
                self.database_section.apply_settings(editable_settings)

            # 保存成功
            self.has_unsaved_changes = False
            self.save_button.disabled = True
            self.reset_button.disabled = True

            self.show_success_snackbar("設定を保存しました")

            # ページ設定の適用（テーマ変更等）
            self._apply_page_settings()

            logger.info("設定を正常に保存しました")

        except Exception as e:
            logger.error(f"設定保存時にエラーが発生しました: {e}")
            self._show_error_dialog("設定の保存に失敗しました", str(e))

    def _on_reset_settings(self, _: ft.ControlEvent) -> None:
        """リセットボタンがクリックされた時の処理。"""

        def on_confirm_reset() -> None:
            """リセット確認時の処理。"""
            self._reset_to_current_settings()
            self.has_unsaved_changes = False
            self.save_button.disabled = True
            self.reset_button.disabled = True
            self.show_info_snackbar("設定をリセットしました")
            if self.page:
                self.page.update()

        def on_cancel_reset() -> None:
            """リセットキャンセル時の処理。"""

        # 確認処理を分離してBoolean引数を回避
        if not self.page:
            return

        # ラムダを使って直接呼び出しを処理
        dialog = ConfirmDialog(
            self.page,
            "設定のリセット",
            "未保存の変更を破棄し、保存済みの設定値に戻しますか？",
            on_result=lambda confirmed: on_confirm_reset() if confirmed else None,
        )
        dialog.show()

    def _reset_to_current_settings(self) -> None:
        """現在の保存済み設定値にリセットする。"""
        current_settings = self.config_manager.settings

        # 各セクションを現在の設定値でリセット
        self.appearance_section.reset_to_settings(current_settings)
        self.window_section.reset_to_settings(current_settings)
        self.database_section.reset_to_settings(current_settings)

    def _apply_page_settings(self) -> None:
        """ページに設定を適用する。"""
        try:
            # テーマの適用
            theme = self.config_manager.theme
            if hasattr(self.page, "theme_mode"):
                self.page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT

            # ウィンドウサイズの適用（デスクトップアプリの場合）
            window_size = self.config_manager.window_size
            if hasattr(self.page, "window_width") and hasattr(self.page, "window_height"):
                self.page.window_width = window_size[0]
                self.page.window_height = window_size[1]

            if hasattr(self.page, "update"):
                self.page.update()

        except Exception as e:
            logger.warning(f"ページ設定の適用に失敗しました: {e}")

    def _show_error_dialog(self, title: str, message: str) -> None:
        """エラーダイアログを表示する。

        Args:
            title: エラータイトル
            message: エラーメッセージ
        """
        dialog = ErrorDialog(
            self.page,
            title,
            message,
        )
        dialog.show()

    def did_mount(self) -> None:
        """ビューがマウントされた時の処理。"""
        super().did_mount()

        # 現在の設定値で各セクションを初期化
        try:
            current_settings = self.config_manager.settings
            self.appearance_section.reset_to_settings(current_settings)
            self.window_section.reset_to_settings(current_settings)
            self.database_section.reset_to_settings(current_settings)

            logger.debug("設定画面を初期化しました")

        except Exception as e:
            logger.error(f"設定画面の初期化でエラーが発生しました: {e}")
            self._show_error_dialog("初期化エラー", f"設定の読み込みに失敗しました: {e}")

    def will_unmount(self) -> None:
        """ビューがアンマウントされる時の処理。"""
        # 未保存の変更がある場合の確認は上位の画面遷移制御に委ねる
        super().will_unmount()
