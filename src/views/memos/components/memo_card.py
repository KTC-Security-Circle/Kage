"""メモカードコンポーネント

個別のメモを表示するためのカードコンポーネント。
Reactテンプレートの機能を参考に、AI提案状態、タグ、日付を含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import MemoRead

# 定数
MAX_CONTENT_PREVIEW_LENGTH = 200


class MemoCard(ft.Container):
    """メモを表示するカードコンポーネント。

    テンプレートのMemosScreen.tsxのメモリスト表示機能を参考に実装。
    AI提案状態、タグ、作成日、選択状態の表示をサポート。
    """

    def __init__(
        self,
        memo: MemoRead,
        *,
        is_selected: bool = False,
        on_click: Callable[[MemoRead], None] | None = None,
        show_ai_badge: bool = True,
        max_content_lines: int = 3,
    ) -> None:
        """メモカードを初期化。

        Args:
            memo: 表示するメモデータ
            is_selected: 選択状態
            on_click: クリック時のコールバック
            show_ai_badge: AI提案バッジの表示
            max_content_lines: 内容の最大表示行数
        """
        self.memo = memo
        self.is_selected = is_selected
        self.memo_click_handler = on_click
        self.show_ai_badge = show_ai_badge
        self.max_content_lines = max_content_lines

        super().__init__(
            content=self._build_card_content(),
            padding=ft.padding.all(12),
            margin=ft.margin.symmetric(vertical=4),
            border_radius=8,
            border=ft.border.all(
                width=2 if is_selected else 1,
                color=ft.Colors.BLUE_400 if is_selected else ft.Colors.OUTLINE,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if is_selected else ft.Colors.SURFACE,
            on_click=self._handle_click if on_click else None,
            ink=True,
            key=str(self.memo.id),
        )

    def _build_card_content(self) -> ft.Control:
        """カードの内容を構築。

        Returns:
            構築されたコントロール
        """
        # ヘッダー部分（タイトルと選択インジケーター）
        header_controls: list[ft.Control] = [
            ft.Text(
                self.memo.title or "無題のメモ",
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                weight=ft.FontWeight.BOLD,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True,
            ),
        ]

        if self.is_selected:
            header_controls.append(
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.BLUE_400, size=20),
            )

        header = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # 内容部分
        content_text = ft.Text(
            self.memo.content[:MAX_CONTENT_PREVIEW_LENGTH]
            + ("..." if len(self.memo.content) > MAX_CONTENT_PREVIEW_LENGTH else ""),
            style=ft.TextThemeStyle.BODY_MEDIUM,
            color=ft.Colors.ON_SURFACE_VARIANT,
            max_lines=self.max_content_lines,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        # フッター部分（バッジと日付）
        footer_controls = []

        # TODO: AI提案状態バッジを統合フェーズで実装
        # 理由: AIサービスとの連携仕様が未確定のため
        if self.show_ai_badge:
            footer_controls.append(self._create_status_badge())

        # タグ表示（将来の拡張用）
        # TODO: タグバッジを統合フェーズで実装
        # 理由: Tag連携仕様が未確定のため

        # 作成日（型上は存在しない可能性があるためガード）
        created_at = getattr(self.memo, "created_at", None)
        created_at_text = created_at.strftime("%Y/%m/%d") if created_at else "—"
        footer_controls.append(
            ft.Text(
                created_at_text,
                style=ft.TextThemeStyle.BODY_SMALL,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
        )

        footer = ft.Row(
            controls=footer_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=8,
        )

        return ft.Column(
            controls=[header, content_text, footer],
            spacing=8,
            tight=True,
        )

    def _create_status_badge(self) -> ft.Container:
        """メモステータスバッジを作成。

        Returns:
            ステータスバッジ
        """
        # TODO: MemoStatusエンタムが追加されたら適切な状態表示に変更
        # 現在は仮の実装
        status_text = "新規"
        status_color = ft.Colors.BLUE_100
        text_color = ft.Colors.BLUE_700

        return ft.Container(
            content=ft.Text(
                status_text,
                size=10,
                color=text_color,
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            bgcolor=status_color,
            border_radius=12,
        )

    def _handle_click(self, _: ft.ControlEvent) -> None:
        """クリックイベントのハンドラー。"""
        if self.memo_click_handler:
            self.memo_click_handler(self.memo)

    def update_selection(self, *, is_selected: bool) -> None:
        """選択状態を更新。

        Args:
            is_selected: 新しい選択状態
        """
        self.is_selected = is_selected
        self.border = ft.border.all(
            width=2 if is_selected else 1,
            color=ft.Colors.BLUE_400 if is_selected else ft.Colors.OUTLINE,
        )
        self.bgcolor = ft.Colors.SECONDARY_CONTAINER if is_selected else ft.Colors.SURFACE

        # ヘッダーのアイコンを更新
        self.content = self._build_card_content()
        self.update()

    def refresh(self, memo: MemoRead, *, is_selected: bool) -> None:
        """メモ内容と選択状態をまとめて更新する。

        Args:
            memo: 最新のメモデータ
            is_selected: 選択状態
        """
        self.memo = memo
        self.update_selection(is_selected=is_selected)

    @classmethod
    def preview(cls) -> MemoCard:
        """単体プレビュー用のインスタンスを生成する。

        Args:
            なし（インスタンス生成に必要な情報は内部で完結）

        Returns:
            サンプルデータを含む MemoCard
        """
        from uuid import uuid4

        from models import MemoRead

        sample = MemoRead(
            id=uuid4(),
            title="プレビュー用メモ",
            content="これは MemoCard 単体プレビューのダミーコンテンツです。",
        )
        return cls(memo=sample, is_selected=True)
