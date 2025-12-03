"""メモカードリストコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.memos import presenter
from views.theme import get_outline_color, get_text_secondary_color

from .memo_card import MemoCard

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import MemoRead

    # データモデルは components/types.py の MemoListData を使用


# ========================================
# 定数
# ========================================

_EMPTY_ICON_SIZE = 48
_EMPTY_PADDING = 40


# ========================================
# コンポーネント
# ========================================


class MemoCardList(ft.Column):
    """メモカードを一覧表示する親制御型リスト。"""

    def __init__(
        self,
        memos: list[MemoRead],
        *,
        on_memo_select: Callable[[MemoRead], None] | None = None,
        empty_message: str = "メモがありません",
        selected_memo_id: str | None = None,
    ) -> None:
        self.memos = memos
        self.on_memo_select = on_memo_select
        self.empty_message = empty_message
        self.selected_memo_id = selected_memo_id
        self._memo_index: dict[str, MemoRead] = {}

        super().__init__(
            controls=self._build_controls(),
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_controls(self) -> list[ft.Control]:
        self._memo_index.clear()
        if not self.memos:
            return [self._build_empty_state()]
        cards: list[ft.Control] = []
        for memo in self.memos:
            card = self._create_card(memo)
            self._memo_index[str(memo.id)] = memo
            cards.append(card)
        return cards

    def _build_empty_state(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.NOTE_ADD, size=_EMPTY_ICON_SIZE, color=get_outline_color()),
                    ft.Text(
                        self.empty_message,
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        color=get_text_secondary_color(),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.padding.all(_EMPTY_PADDING),
        )

    def _create_card(self, memo: MemoRead) -> MemoCard:
        card_data = presenter.create_memo_card_data(
            memo=memo,
            is_selected=self.selected_memo_id == str(memo.id),
            on_click=lambda: self._handle_memo_select(memo),
        )
        return MemoCard(card_data)

    def _handle_memo_select(self, memo: MemoRead) -> None:
        if self.on_memo_select:
            self.on_memo_select(memo)

    def update_memos(self, memos: list[MemoRead], *, selected_memo_id: str | None = None) -> None:
        self.memos = memos
        if selected_memo_id is not None:
            self.selected_memo_id = selected_memo_id

        if not memos:
            self.controls = [self._build_empty_state()]
            self._memo_index.clear()
        else:
            # 全てのカードを再作成（MemoCardは不変なので）
            updated_controls: list[ft.Control] = []
            new_index: dict[str, MemoRead] = {}
            for memo in memos:
                memo_id = str(memo.id)
                card = self._create_card(memo)
                updated_controls.append(card)
                new_index[memo_id] = memo
            self.controls = updated_controls
            self._memo_index = new_index

        if getattr(self, "page", None) is not None:
            self.update()

    def set_selected_memo(self, memo_id: str | None) -> None:
        """選択されたメモを変更（全カードを再構築）。"""
        self.selected_memo_id = memo_id
        # 全カードを再作成（MemoCardは不変なので）
        self.controls = [self._create_card(memo) for memo in self.memos] if self.memos else [self._build_empty_state()]
        if getattr(self, "page", None) is not None:
            self.update()

    def _find_card(self, memo_id: str) -> MemoCard | None:
        """指定されたIDのメモカードを検索（MemoReadから再作成）。"""
        memo = self._memo_index.get(memo_id)
        if memo:
            return self._create_card(memo)
        return None
