"""設定画面のメインビュークラス。

アプリケーション設定の表示・編集機能を提供します。
新レイヤー構造（state/query/presenter/controller）に準拠。
"""

from __future__ import annotations

import flet as ft
from loguru import logger

from logic.services.settings_service import SettingsService
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.dialogs import ConfirmDialog
from views.theme import SPACING, get_light_color

from .components.appearance_section import AppearanceSection
from .components.database_section import DatabaseSection
from .components.window_section import WindowSection
from .controller import SettingsController
from .state import SettingsViewState


class SettingsView(BaseView):
    """設定画面のメインビュークラス。

    新レイヤー構造に準拠：
    - State: 表示状態の保持
    - Controller: イベント処理とロジック実行
    - View: UI構築とハンドラ注入
    """

    # 型ヒントで具体的なStateを宣言
    state: SettingsViewState

    def __init__(self, props: BaseViewProps) -> None:
        """SettingsViewを初期化する。

        Args:
            props: View共通プロパティ。BaseViewPropsとしてFletの``page``と
                アプリケーションサービス``apps``を受け取ります。
        """
        super().__init__(props)

        # State層とController層の初期化
        self.state = SettingsViewState()
        self._settings_service = SettingsService.build_service()
        self.controller = SettingsController(
            state=self.state,
            service=self._settings_service,
        )

        # セクションコンポーネント（ハンドラ注入）
        self.appearance_section = AppearanceSection(self.page, self._on_setting_changed)
        self.window_section = WindowSection(self.page, self._on_setting_changed)
        self.database_section = DatabaseSection(self.page, self._on_setting_changed)

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
        # 状態変更は自動的にhas_unsaved_changesで検知される
        self.save_button.disabled = not self.state.has_unsaved_changes
        self.reset_button.disabled = not self.state.has_unsaved_changes
        if hasattr(self.page, "update"):
            self.page.update()

    def _on_save_settings(self, _: ft.ControlEvent) -> None:
        """設定保存ボタンがクリックされた時の処理。"""
        try:
            # Controllerに保存処理を委譲
            self.controller.save_settings()

            # UI更新
            self.save_button.disabled = True
            self.reset_button.disabled = True
            self.show_success_snackbar("設定を保存しました")

            # ページ設定の適用（Controllerに委譲）
            self.controller.apply_runtime_effects(self.page)

            logger.info("設定を正常に保存しました")

        except Exception as e:
            logger.error(f"設定保存時にエラーが発生しました: {e}")
            self.notify_error(f"設定の保存に失敗しました: {e}")

    def _on_reset_settings(self, _: ft.ControlEvent) -> None:
        """リセットボタンがクリックされた時の処理。"""

        def on_confirm_reset() -> None:
            """リセット確認時の処理。"""
            try:
                # Controllerにリセット処理を委譲
                self.controller.reset_settings()

                # セクションUIを更新
                self._update_sections_from_state()

                # UI更新
                self.save_button.disabled = True
                self.reset_button.disabled = True
                self.show_info_snackbar("設定をリセットしました")

                if self.page:
                    self.page.update()

            except Exception as e:
                logger.error(f"設定のリセットに失敗しました: {e}")
                self.notify_error(f"設定のリセットに失敗しました: {e}")

        # 確認ダイアログを表示
        if not self.page:
            return

        dialog = ConfirmDialog(
            self.page,
            "設定のリセット",
            "未保存の変更を破棄し、保存済みの設定値に戻しますか？",
            on_result=lambda confirmed: on_confirm_reset() if confirmed else None,
        )
        dialog.show()

    def _update_sections_from_state(self) -> None:
        """Stateの値からセクションUIを更新する。"""
        if self.state.current is None:
            return

        # TODO: セクションコンポーネントに値を反映する実装
        # 現在のセクションコンポーネントはまだ古い実装のため、統合は後で行う

    def did_mount(self) -> None:
        """ビューがマウントされた時の処理。"""
        super().did_mount()

        # Controllerを使って設定値を読み込む
        try:
            self.controller.load_settings()

            # セクションUIを更新
            self._update_sections_from_state()

            logger.debug("設定画面を初期化しました")

        except Exception as e:
            logger.error(f"設定画面の初期化でエラーが発生しました: {e}")
            self.notify_error(f"設定の読み込みに失敗しました: {e}")

    def will_unmount(self) -> None:
        """ビューがアンマウントされる時の処理。"""
        # 未保存の変更がある場合の確認は上位の画面遷移制御に委ねる
        super().will_unmount()
