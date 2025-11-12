"""タグ管理画面

タグの一覧表示、作成、編集、削除機能と色選択機能を提供するメインビュー。
BaseViewパターンを採用し、一貫したUIと機能を提供する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from views.shared.base_view import BaseView, BaseViewProps
from views.theme import get_tag_color_palette

from .components import (
    create_action_bar,
    create_empty_state,
    create_page_header,
    create_tag_card,
)


class TagsView(BaseView):
    """タグ管理画面のメインビュー。

    タグの一覧表示（色付きチップ）、CRUD操作、検索・フィルタ、
    カラーパレット機能を提供。BaseViewを継承し、エラーハンドリングと
    ローディング機能を活用。
    """

    def __init__(self, props: BaseViewProps) -> None:  # type: ignore[name-defined]
        """TagsViewを初期化する。

        Args:
            props: View共通プロパティ
        """
        super().__init__(props)
        self.tags_data: list[dict[str, str]] = []  # TODO: 実際のデータバインディング
        self.available_colors = get_tag_color_palette()

    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """タグ画面のコンテンツを構築する。

        Returns:
            タグ画面のメインコンテンツ
        """
        import flet as ft

        # Mock data for development
        self.tags_data = [
            {
                "id": "1",
                "name": "緊急",
                "color": "#f44336",
                "description": "緊急度の高いタスク用",
                "task_count": "15",
                "created_at": "2024-01-15",
            },
            {
                "id": "2",
                "name": "開発",
                "color": "#2196f3",
                "description": "開発関連のタスク",
                "task_count": "32",
                "created_at": "2024-01-10",
            },
            {
                "id": "3",
                "name": "デザイン",
                "color": "#e91e63",
                "description": "UI/UXデザイン関連",
                "task_count": "8",
                "created_at": "2024-01-20",
            },
            {
                "id": "4",
                "name": "レビュー",
                "color": "#ff9800",
                "description": "コードレビューやドキュメントレビュー",
                "task_count": "5",
                "created_at": "2024-02-01",
            },
            {
                "id": "5",
                "name": "バグ修正",
                "color": "#f44336",
                "description": "バグ修正タスク",
                "task_count": "12",
                "created_at": "2024-01-25",
            },
        ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    create_page_header(len(self.tags_data)),
                    create_action_bar(
                        on_create=self._handle_create_tag,
                        on_search=self._handle_search,
                        on_color_filter=self._handle_color_filter,
                        on_refresh=self._handle_refresh,
                    ),
                    self._build_tags_list(),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def _build_tags_list(self) -> ft.Control:  # type: ignore[name-defined]
        """タグ一覧を構築する。

        Returns:
            タグ一覧コンテンツ
        """
        import flet as ft

        if not self.tags_data:
            return create_empty_state(on_create=self._handle_create_tag)

        tags_cards = [
            create_tag_card(
                tag=tag,
                on_edit=self._handle_edit_tag,
                on_delete=self._handle_delete_tag,
            )
            for tag in self.tags_data
        ]

        return ft.Container(
            content=ft.Column(
                controls=tags_cards,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )

    def _handle_create_tag(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規タグ作成を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: タグ作成ダイアログを表示
        self.show_info_snackbar("新規タグ作成機能は準備中です")

    def _handle_edit_tag(self, _: ft.ControlEvent, tag: dict[str, str]) -> None:  # type: ignore[name-defined]
        """タグ編集を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            tag: 編集対象のタグ
        """
        # TODO: タグ編集ダイアログを表示
        self.show_info_snackbar(f"タグ「{tag['name']}」の編集機能は準備中です")

    def _handle_delete_tag(self, _: ft.ControlEvent, tag: dict[str, str]) -> None:  # type: ignore[name-defined]
        """タグ削除を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            tag: 削除対象のタグ
        """
        # TODO: 削除確認ダイアログを表示
        self.show_info_snackbar(f"タグ「{tag['name']}」の削除機能は準備中です")

    def _handle_search(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索を処理する。

        Args:
            e: イベントオブジェクト
        """
        # TODO: 検索機能を実装
        search_text = e.control.value if e.control.value else ""  # type: ignore[attr-defined]
        if search_text:
            self.show_info_snackbar(f"「{search_text}」の検索機能は準備中です")

    def _handle_color_filter(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """色フィルターを処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: 色フィルターダイアログを表示
        self.show_info_snackbar("色フィルター機能は準備中です")

    def _handle_refresh(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """データ更新を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: 実際のデータ再読み込み
        self.show_success_snackbar("タグデータを更新しました")
        self.page.update()
