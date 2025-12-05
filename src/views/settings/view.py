"""設定画面のメインビュークラス。

アプリケーション設定の表示・編集機能を提供します。
新レイヤー構造（state/query/presenter/controller）に準拠。
"""

from __future__ import annotations

import flet as ft

from views.shared.base_view import BaseView, BaseViewProps
from views.shared.dialogs import ConfirmDialog
from views.theme import SPACING, get_light_color, get_text_secondary_color

from .components.agent_section import AgentSection
from .components.appearance_section import AppearanceSection
from .components.database_section import DatabaseSection
from .components.window_section import WindowSection
from .controller import SettingsController
from .query import SettingsQuery
from .state import SettingsSnapshot, SettingsViewState

TEMPERATURE_EPSILON = 0.01


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
            props: ビュー共通プロパティ (page, apps などを含む)
        """
        super().__init__(props)

        # UI更新中フラグ（イベント発火を抑制）
        self._updating_ui = False

        # State層とController層の初期化
        self.state = SettingsViewState()
        # ApplicationServices経由でSettingsApplicationServiceを取得
        self._query = SettingsQuery(app_service=self.apps.settings)
        self.controller = SettingsController(
            state=self.state,
            query=self._query,
        )

        # セクションコンポーネント（ハンドラ注入）
        self.appearance_section = AppearanceSection(props.page, self._on_setting_changed)
        self.window_section = WindowSection(props.page, self._on_setting_changed)
        self.database_section = DatabaseSection(props.page, self._on_setting_changed)
        self.agent_section = AgentSection(self._on_setting_changed)

        # 保存・リセットボタン（常時有効）
        self.save_button = ft.ElevatedButton(
            text="設定を保存",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: get_light_color("primary")},
                color={ft.ControlState.DEFAULT: get_light_color("on_primary")},
            ),
            on_click=self._on_save_settings,
        )

        self.reset_button = ft.OutlinedButton(
            text="リセット",
            icon=ft.Icons.REFRESH,
            on_click=self._on_reset_settings,
        )

    def build_content(self) -> ft.Control:
        """設定画面のUIを構築する。

        Returns:
            構築されたUIコントロール
        """
        # 初回構築時に設定をロード
        if self.state.current is None:
            self.controller.load_settings()
            self._update_sections_from_state()

        header = self._create_page_header()

        # メインコンテンツ
        content = ft.Column(
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
                # AIエージェント設定
                self._create_section_card(
                    "AIエージェント",
                    "LLM モデルやデバッグモードの設定",
                    ft.Icons.AUTO_AWESOME,
                    self.agent_section,
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
            expand=True,
        )

        return self.create_standard_layout(
            header=header,
            content=content,
        )

    def _create_page_header(self) -> ft.Control:
        """ページヘッダーを作成する。

        Returns:
            ページヘッダーコントロール
        """
        return self.create_header(
            title="設定",
            subtitle="アプリケーションの設定を管理",
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
                                            color=get_text_secondary_color(),
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
        # UI更新中は処理をスキップ
        if self._updating_ui:
            return

        if self.state.current is None:
            return

        # UIから値を取得してControllerの状態を更新（値が変更された場合のみ）
        current = self.state.current

        # 外観設定
        if (
            self.appearance_section.theme_radio.value
            and self.appearance_section.theme_radio.value != current.appearance.theme
        ):
            self.controller.update_theme(self.appearance_section.theme_radio.value)

        if (
            self.appearance_section.user_name_field.value is not None
            and self.appearance_section.user_name_field.value != current.appearance.user_name
        ):
            self.controller.update_user_name(self.appearance_section.user_name_field.value)

        # ウィンドウ設定
        try:
            width = int(self.window_section.width_field.value or "1280")
            height = int(self.window_section.height_field.value or "720")
            if [width, height] != current.window.size:
                self.controller.update_window_size(width, height)

            x = int(self.window_section.x_field.value or "100")
            y = int(self.window_section.y_field.value or "100")
            if [x, y] != current.window.position:
                self.controller.update_window_position(x, y)
        except ValueError:
            # 不正な数値の場合は何もしない
            pass

        # データベース設定
        if self.database_section.url_field.value and self.database_section.url_field.value != current.database_url:
            self.controller.update_database_url(self.database_section.url_field.value)
        self._sync_agent_settings(current)

    def _sync_agent_settings(self, snapshot: SettingsSnapshot) -> None:
        provider_value = self.agent_section.provider_dropdown.value
        if provider_value and provider_value != snapshot.agent_provider.value:
            self.controller.update_agent_provider(provider_value)

        model_value = self.agent_section.model_field.value or ""
        if model_value != (snapshot.agent.model or ""):
            self.controller.update_agent_model(model_value)

        temp_value = float(self.agent_section.temperature_slider.value or snapshot.agent.temperature)
        if abs(temp_value - snapshot.agent.temperature) >= TEMPERATURE_EPSILON:
            self.controller.update_agent_temperature(temp_value)

        debug_value = bool(self.agent_section.debug_switch.value)
        if debug_value != snapshot.agent.debug_mode:
            self.controller.update_agent_debug_mode(debug_mode=debug_value)

        device_value = self.agent_section.device_value
        if device_value != snapshot.agent.device.value:
            self.controller.update_agent_device(device_value)

    def _on_save_settings(self, _: ft.ControlEvent) -> None:
        """設定保存ボタンがクリックされた時の処理。"""

        def save_and_apply_settings() -> None:
            """設定を保存し、ランタイム設定を適用する。"""
            self.controller.save_settings()
            self.controller.apply_runtime_effects(self.page)
            self.show_success_snackbar("設定を保存しました")

        self.with_loading(
            fn_or_coro=save_and_apply_settings,
            user_error_message="設定の保存に失敗しました",
        )

    def _on_reset_settings(self, _: ft.ControlEvent) -> None:
        """リセットボタンがクリックされた時の処理。"""

        def on_confirm_reset() -> None:
            """リセット確認時の処理。"""

            def reset_and_update() -> None:
                """設定をリセットし、UIを更新する。"""
                self.controller.reset_settings()
                self._update_sections_from_state()
                self.show_info_snackbar("設定をリセットしました")

                if self.page:
                    self.page.update()

            self.with_loading(
                fn_or_coro=reset_and_update,
                user_error_message="設定のリセットに失敗しました",
            )

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

        snapshot = self.state.current

        # UI更新中フラグを立てる（イベント発火を抑制）
        self._updating_ui = True
        try:
            # 外観設定セクションの更新
            self.appearance_section.theme_radio.value = snapshot.appearance.theme
            self.appearance_section.user_name_field.value = snapshot.appearance.user_name

            # ウィンドウ設定セクションの更新
            self.window_section.width_field.value = str(snapshot.window.size[0])
            self.window_section.height_field.value = str(snapshot.window.size[1])
            self.window_section.x_field.value = str(snapshot.window.position[0])
            self.window_section.y_field.value = str(snapshot.window.position[1])

            # データベース設定セクションの更新
            self.database_section.url_field.value = snapshot.database_url

            # エージェント設定セクション
            self.agent_section.set_values(
                provider=snapshot.agent_provider.value,
                model=snapshot.agent.model,
                temperature=snapshot.agent.temperature,
                debug_mode=snapshot.agent.debug_mode,
                device=snapshot.agent.device.value,
            )

            # UIを更新
            if self.page:
                self.page.update()
        finally:
            # フラグを戻す
            self._updating_ui = False

    def will_unmount(self) -> None:
        """ビューがアンマウントされる時の処理。"""
        # 未保存の変更がある場合の確認は上位の画面遷移制御に委ねる
        super().will_unmount()
