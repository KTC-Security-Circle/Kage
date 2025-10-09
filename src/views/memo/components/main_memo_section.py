"""メインメモセクションコンポーネントモジュール."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from logic.application.memo_application_service import MemoApplicationService

from .memo_stats_card import MemoStatsCard


class MainMemoSection(ft.Column):
    """メインメモセクションコンポーネント.

    新規メモ作成ボタンと統計情報を表示するセクション。
    """

    def __init__(self, page: ft.Page, memo_app_service: MemoApplicationService) -> None:
        """MainMemoSectionの初期化.

        Args:
            page: Fletのページオブジェクト
            memo_app_service: メモアプリケーションサービスインスタンス
        """
        super().__init__()
        self._page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.memo_app_service = memo_app_service

        # コンポーネントを構築
        self._build_components()

    def _build_components(self) -> None:
        """コンポーネントを構築して追加."""
        self.controls = [
            ft.ElevatedButton(
                text="新規メモ作成",
                icon=ft.Icons.ADD,
                width=200,
                height=50,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16),
                ),
                on_click=self._show_new_memo_dialog,
            ),
            MemoStatsCard(memo_count=self.get_total_memo_count()),
        ]

    def _show_new_memo_dialog(self, _: ft.ControlEvent) -> None:
        """新規メモ作成ダイアログを表示.

        Args:
            _: イベントオブジェクト
        """
        # [AI GENERATED] 新規メモ作成ダイアログの実装
        # 今後、ダイアログまたは専用画面で実装予定
        msg = "新規メモ作成ダイアログは未実装です"
        snack_bar = ft.SnackBar(ft.Text(msg))
        self._page.overlay.append(snack_bar)
        snack_bar.open = True
        self._page.update()

    def get_total_memo_count(self) -> int:
        """総メモ件数を取得.

        Returns:
            総メモ件数
        """
        from logic.queries.memo_queries import GetAllMemosQuery

        query = GetAllMemosQuery()
        memos = self.memo_app_service.get_all_memos(query)
        return len(memos)
