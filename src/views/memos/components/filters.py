"""メモフィルタコンポーネント

メモの絞り込み機能を提供するフィルタコンポーネント。
日付範囲、タグ、AI提案状態等によるフィルタリングをサポート。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date


# ========================================
# データモデル
# ========================================


@dataclass(frozen=True, slots=True)
class FilterConfig:
    """フィルタ表示設定

    Attributes:
        show_date_filter: 日付フィルタの表示有無
        show_ai_status_filter: AI状態フィルタの表示有無
        show_tag_filter: タグフィルタの表示有無
    """

    show_date_filter: bool = True
    show_ai_status_filter: bool = True
    show_tag_filter: bool = False


@dataclass(frozen=True, slots=True)
class FilterData:
    """フィルタコンポーネント表示用データ

    Attributes:
        config: フィルタ表示設定
        on_filter_change: フィルタ変更時のコールバック
    """

    config: FilterConfig
    on_filter_change: Callable[[dict[str, object]], None] | None = None


# ========================================
# コンポーネント
# ========================================


class MemoFilters(ft.Container):
    """メモフィルタコンポーネント。

    様々な条件でメモをフィルタリングする機能を提供。
    日付範囲、AI提案状態、タグ等による絞り込みをサポート。
    """

    def __init__(
        self,
        *,
        on_filter_change: Callable[[dict[str, object]], None] | None = None,
        show_date_filter: bool = True,
        show_ai_status_filter: bool = True,
        show_tag_filter: bool = False,  # 将来の拡張用
    ) -> None:
        """メモフィルタを初期化。

        Args:
            on_filter_change: フィルタ変更時のコールバック
            show_date_filter: 日付フィルタの表示
            show_ai_status_filter: AI状態フィルタの表示
            show_tag_filter: タグフィルタの表示
        """
        self.on_filter_change = on_filter_change
        self.show_date_filter = show_date_filter
        self.show_ai_status_filter = show_ai_status_filter
        self.show_tag_filter = show_tag_filter

        # フィルタ状態
        self.date_from: date | None = None
        self.date_to: date | None = None
        self.ai_status_filter: str | None = None
        self.selected_tags: set[str] = set()

        # UI要素の参照
        self._date_from_field: ft.TextField | None = None
        self._date_to_field: ft.TextField | None = None
        self._ai_status_dropdown: ft.Dropdown | None = None

        super().__init__(
            content=self._build_filters(),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=8,
            visible=False,  # 初期状態では非表示
        )

    def _build_filters(self) -> ft.Control:
        """フィルタUIを構築。

        Returns:
            構築されたフィルタコントロール
        """
        filter_sections = []

        # タイトル
        filter_sections.append(
            ft.Row(
                controls=[
                    ft.Text(
                        "フィルタ",
                        style=ft.TextThemeStyle.TITLE_SMALL,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        on_click=self._handle_close,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # 日付フィルタ
        if self.show_date_filter:
            filter_sections.append(self._build_date_filter())

        # AI状態フィルタ
        if self.show_ai_status_filter:
            filter_sections.append(self._build_ai_status_filter())

        # TODO: タグフィルタを統合フェーズで実装
        # 理由: Tag連携仕様が未確定のため
        if self.show_tag_filter:
            filter_sections.append(self._build_tag_filter())

        # リセットボタン
        filter_sections.append(
            ft.Row(
                controls=[
                    ft.OutlinedButton(
                        "リセット",
                        on_click=self._handle_reset,
                        expand=True,
                    ),
                ],
            ),
        )

        return ft.Column(
            controls=filter_sections,
            spacing=16,
            tight=True,
        )

    def _build_date_filter(self) -> ft.Control:
        """日付フィルタセクションを構築。

        Returns:
            日付フィルタコントロール
        """
        self._date_from_field = ft.TextField(
            label="開始日",
            hint_text="YYYY-MM-DD",
            width=150,
            on_change=self._handle_date_change,
        )

        self._date_to_field = ft.TextField(
            label="終了日",
            hint_text="YYYY-MM-DD",
            width=150,
            on_change=self._handle_date_change,
        )

        return ft.Column(
            controls=[
                ft.Text("作成日", style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[self._date_from_field, self._date_to_field],
                    spacing=12,
                ),
            ],
            spacing=8,
            tight=True,
        )

    def _build_ai_status_filter(self) -> ft.Control:
        """AI状態フィルタセクションを構築。

        Returns:
            AI状態フィルタコントロール
        """
        self._ai_status_dropdown = ft.Dropdown(
            label="AI提案状態",
            options=[
                ft.dropdown.Option(key="", text="すべて"),
                ft.dropdown.Option(key="not_requested", text="未要求"),
                ft.dropdown.Option(key="pending", text="処理中"),
                ft.dropdown.Option(key="available", text="提案あり"),
                ft.dropdown.Option(key="reviewed", text="確認済み"),
                ft.dropdown.Option(key="failed", text="失敗"),
            ],
            value="",
            width=200,
            on_change=self._handle_ai_status_change,
        )

        return ft.Column(
            controls=[
                ft.Text("AI提案", style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                self._ai_status_dropdown,
            ],
            spacing=8,
            tight=True,
        )

    def _build_tag_filter(self) -> ft.Control:
        """タグフィルタセクションを構築。

        Returns:
            タグフィルタコントロール

        Note:
            将来の拡張用プレースホルダー実装
        """
        return ft.Column(
            controls=[
                ft.Text("タグ", style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "タグフィルタは統合フェーズで実装予定",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=8,
            tight=True,
        )

    def _handle_date_change(self, _: ft.ControlEvent) -> None:
        """日付変更時のハンドラー。"""
        # TODO: 日付バリデーションを追加
        self._notify_filter_change()

    def _handle_ai_status_change(self, _: ft.ControlEvent) -> None:
        """AI状態変更時のハンドラー。"""
        if self._ai_status_dropdown:
            self.ai_status_filter = self._ai_status_dropdown.value
        self._notify_filter_change()

    def _handle_close(self, _: ft.ControlEvent) -> None:
        """フィルタ閉じるボタンのハンドラー。"""
        self.visible = False
        self.update()

    def _handle_reset(self, _: ft.ControlEvent) -> None:
        """リセットボタンのハンドラー。"""
        # フィールドをクリア
        if self._date_from_field:
            self._date_from_field.value = ""
        if self._date_to_field:
            self._date_to_field.value = ""
        if self._ai_status_dropdown:
            self._ai_status_dropdown.value = ""

        # 状態をリセット
        self.date_from = None
        self.date_to = None
        self.ai_status_filter = None
        self.selected_tags.clear()

        self.update()
        self._notify_filter_change()

    def _notify_filter_change(self) -> None:
        """フィルタ変更を通知。"""
        if self.on_filter_change:
            filter_data = self.get_filter_data()
            self.on_filter_change(filter_data)

    def get_filter_data(self) -> dict[str, object]:
        """現在のフィルタデータを取得。

        Returns:
            フィルタデータ辞書
        """
        return {
            "date_from": self._date_from_field.value if self._date_from_field else None,
            "date_to": self._date_to_field.value if self._date_to_field else None,
            "ai_status": self.ai_status_filter,
            "tags": list(self.selected_tags),
        }

    def show_filters(self) -> None:
        """フィルタを表示。"""
        self.visible = True
        self.update()

    def hide_filters(self) -> None:
        """フィルタを非表示。"""
        self.visible = False
        self.update()

    def toggle_filters(self) -> None:
        """フィルタの表示/非表示を切り替え。"""
        self.visible = not self.visible
        self.update()

    def has_active_filters(self) -> bool:
        """アクティブなフィルタがあるかチェック。

        Returns:
            アクティブなフィルタがある場合True
        """
        filter_data = self.get_filter_data()
        return any(value for key, value in filter_data.items() if value and (key != "tags" or value))


class MemoFilterButton(ft.IconButton):
    """メモフィルタ表示ボタン。

    フィルタの表示/非表示切り替えとアクティブ状態の表示。
    """

    def __init__(
        self,
        memo_filters: MemoFilters,
        *,
        tooltip: str = "フィルタ",
    ) -> None:
        """フィルタボタンを初期化。

        Args:
            memo_filters: 関連するフィルタコンポーネント
            tooltip: ボタンのツールチップ
        """
        self.memo_filters = memo_filters
        self._update_icon()

        super().__init__(
            icon=self._icon,
            tooltip=tooltip,
            on_click=self._handle_click,
        )

    def _update_icon(self) -> None:
        """アイコンを更新。"""
        has_filters = self.memo_filters.has_active_filters()
        self._icon = ft.Icons.FILTER_ALT if has_filters else ft.Icons.FILTER_ALT_OUTLINED

    def _handle_click(self, _: ft.ControlEvent) -> None:
        """ボタンクリック時のハンドラー。"""
        self.memo_filters.toggle_filters()
        self._update_icon()
        self.icon = self._icon
        self.update()

    def update_state(self) -> None:
        """ボタンの状態を更新。"""
        self._update_icon()
        self.icon = self._icon
        self.update()
