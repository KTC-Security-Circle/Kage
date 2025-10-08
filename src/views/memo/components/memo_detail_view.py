"""メモ詳細表示コンポーネントモジュール."""

from __future__ import annotations

import urllib.parse
import uuid
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from logic.application.memo_application_service import MemoApplicationService
from logic.queries.memo_queries import GetMemoByIdQuery
from views.shared import BaseView, ErrorHandlingMixin

if TYPE_CHECKING:
    from models import MemoRead


class MemoDetailView(BaseView, ErrorHandlingMixin):
    """メモ詳細表示画面のメインビューコンポーネント

    IDで指定されたメモの詳細情報を表示する。
    """

    def __init__(self, page: ft.Page) -> None:
        """MemoDetailViewの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__(page)

        # 依存性注入
        self.memo_app_service: MemoApplicationService = self.container.get_service(MemoApplicationService)

        # 状態管理
        self.memo_id: str | None = None
        self.memo: MemoRead | None = None

    def mount(self) -> None:
        """コンポーネントのマウント処理をオーバーライド"""
        # [AI GENERATED] URLからメモIDを取得
        self._extract_memo_id_from_route()

        # [AI GENERATED] メモデータを読み込み
        if self.memo_id:
            self._load_memo()

        # [AI GENERATED] データ読み込み後に親クラスのマウント処理を実行
        super().mount()

    def build_content(self) -> ft.Control:
        """メモ詳細画面のコンテンツを構築

        Returns:
            ft.Control: 構築されたコンテンツ
        """
        # [AI GENERATED] デバッグログでメモの状態を確認
        logger.info(f"build_content: memo_id={self.memo_id}, memo={self.memo is not None}")
        if self.memo:
            logger.info(f"build_content: memo content length={len(self.memo.content)}")

        if not self.memo:
            logger.warning("build_content: メモが見つからないため、エラー画面を表示")
            return ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.SEARCH_OFF,
                                    size=64,
                                    color=ft.Colors.GREY_400,
                                ),
                                ft.Text(
                                    "メモが見つかりません",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "指定されたIDのメモが存在しないか、削除された可能性があります。",
                                    size=14,
                                    color=ft.Colors.GREY_500,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        alignment=ft.alignment.center,
                        padding=40,
                    ),
                    ft.ElevatedButton(
                        text="メモ一覧に戻る",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=self._handle_back_to_list,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_600,
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )

        # ヘッダー部分
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.DESCRIPTION,
                                size=28,
                                color=ft.Colors.BLUE_600,
                            ),
                            ft.Text(
                                "メモ詳細",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.PRIMARY,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Markdown",
                                    size=12,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=ft.Colors.BLUE_600,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12,
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.ElevatedButton(
                        text="一覧に戻る",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=self._handle_back_to_list,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_600,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(vertical=10),
        )

        # メモ情報カード
        memo_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        # メモID
                        ft.Row(
                            [
                                ft.Text(
                                    "ID:",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_700,
                                ),
                                ft.Text(
                                    str(self.memo.id),
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(),
                        # メモ内容
                        ft.Text(
                            "内容:",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Container(
                            content=ft.Markdown(
                                value=self.memo.content,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                code_theme=ft.MarkdownCodeTheme.GITHUB,
                                code_style_sheet=ft.MarkdownStyleSheet(
                                    code_text_style=ft.TextStyle(
                                        font_family="monospace",
                                        size=14,
                                    )
                                ),
                            ),
                            padding=15,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            expand=True,
                        ),
                        ft.Divider(),
                        # タスクID（もしあれば）
                        ft.Row(
                            [
                                ft.Text(
                                    "関連タスクID:",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_700,
                                ),
                                ft.Text(
                                    str(self.memo.task_id) if self.memo.task_id else "なし",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True,
            ),
            elevation=3,
            expand=True,
        )

        return ft.Column(
            [
                header,
                ft.Divider(),
                ft.Container(
                    content=memo_card,
                    expand=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=20,
            expand=True,
        )

    def _extract_memo_id_from_route(self) -> None:
        """ルートからメモIDを抽出"""
        # [AI GENERATED] URLクエリパラメータからmemo_idを取得
        try:
            # [AI GENERATED] self.page.routeからクエリパラメータを抽出
            if "?" in self.page.route:
                _, query_string = self.page.route.split("?", 1)
                query_params = urllib.parse.parse_qs(query_string)
                memo_ids = query_params.get("id", [])
                if memo_ids:
                    self.memo_id = memo_ids[0]
                    logger.debug(f"ルートからメモIDを取得: {self.memo_id}")
                else:
                    logger.warning("URLからメモIDを取得できませんでした")
            else:
                logger.warning("URLにクエリパラメータが見つかりません")
        except Exception as e:
            logger.exception("メモIDの抽出に失敗しました")
            self.show_error("メモIDの取得に失敗しました", str(e))

    def _load_memo(self) -> None:
        """メモデータを読み込み"""
        if not self.memo_id:
            logger.warning("メモIDが設定されていません")
            self.show_error("メモIDが指定されていません", "URLを確認してください")
            return

        try:
            logger.info(f"メモ詳細取得開始: ID {self.memo_id}")
            query = GetMemoByIdQuery(memo_id=uuid.UUID(self.memo_id))
            self.memo = self.memo_app_service.get_memo_by_id(query)

            if not self.memo:
                logger.warning(f"メモが見つかりません: ID {self.memo_id}")
                self.show_error("メモが見つかりません", f"ID: {self.memo_id}")
            else:
                logger.info(f"メモを読み込みました: ID {self.memo.id}, content: {self.memo.content[:100]}...")
                logger.info(f"メモを読み込みました: ID {self.memo.id}, content_length: {len(self.memo.content)}")
                # [AI GENERATED] データ読み込み後にコンテンツを再構築
                self._rebuild_content()
                # [AI GENERATED] データ読み込み後にページを更新
                if hasattr(self, "page") and self.page:
                    logger.info("メモデータ読み込み完了後にページを更新します")
                    self.page.update()
        except Exception as e:
            logger.exception("メモの読み込みに失敗しました")
            self.show_error("メモの読み込みに失敗しました", str(e))

    def _rebuild_content(self) -> None:
        """メモデータ読み込み後にコンテンツを再構築"""
        # [AI GENERATED] 新しいコンテンツでself.contentを置き換える
        try:
            new_content = self.build_content()
            self.content = new_content
            logger.info("コンテンツを再構築しました")
        except Exception as e:
            logger.exception("コンテンツの再構築に失敗しました")
            self.content = ft.Text(
                f"コンテンツの更新に失敗しました: {e}",
                color=ft.Colors.RED,
            )

    def refresh(self) -> None:
        """ビューの再読み込み - ルート変更時に呼ばれる"""
        logger.info("MemoDetailView リフレッシュ開始")

        # [AI GENERATED] 現在のメモIDを保存
        previous_memo_id = self.memo_id

        # [AI GENERATED] URLから新しいメモIDを取得
        self._extract_memo_id_from_route()

        # [AI GENERATED] メモIDが変更された場合のみデータを再読み込み
        if self.memo_id != previous_memo_id:
            logger.info(f"メモIDが変更されました: {previous_memo_id} -> {self.memo_id}")
            if self.memo_id:
                self._load_memo()
            else:
                # [AI GENERATED] メモIDがない場合はメモデータをクリア
                self.memo = None
                self._rebuild_content()
                if hasattr(self, "page") and self.page:
                    self.page.update()
        else:
            logger.info(f"メモIDは変更されていません: {self.memo_id}")

        # [AI GENERATED] 親クラスのrefreshを呼び出し
        super().refresh()

    def _handle_back_to_list(self, _: ft.ControlEvent) -> None:
        """メモ一覧への戻る処理

        Args:
            _: イベントオブジェクト
        """
        self.page.go("/memo")


def create_memo_detail_view(page: ft.Page) -> ft.Container:
    """メモ詳細画面ビューを作成する関数

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Container: 構築されたメモ詳細画面ビュー
    """
    memo_detail_view = MemoDetailView(page)
    memo_detail_view.mount()  # コンテンツを構築
    return memo_detail_view
