"""メモカードリストコンポーネント。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from .memo_card import MemoCard

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import MemoRead

_EMPTY_ICON_SIZE = 48
_EMPTY_PADDING = 40


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
        self._index: dict[str, MemoCard] = {}

        super().__init__(
            controls=self._build_controls(),
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_controls(self) -> list[ft.Control]:
        self._index.clear()
        if not self.memos:
            return [self._build_empty_state()]
        cards: list[ft.Control] = []
        for memo in self.memos:
            card = self._create_card(memo)
            self._index[str(memo.id)] = card
            cards.append(card)
        return cards

    def _build_empty_state(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.NOTE_ADD, size=_EMPTY_ICON_SIZE, color=ft.Colors.OUTLINE),
                    ft.Text(
                        self.empty_message,
                        style=ft.TextThemeStyle.BODY_LARGE,
                        color=ft.Colors.ON_SURFACE_VARIANT,
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
        return MemoCard(
            memo=memo,
            is_selected=self.selected_memo_id == str(memo.id),
            on_click=self._handle_memo_select,
        )

    def _handle_memo_select(self, memo: MemoRead) -> None:
        if self.on_memo_select:
            self.on_memo_select(memo)

    def update_memos(self, memos: list[MemoRead], *, selected_memo_id: str | None = None) -> None:
        self.memos = memos
        if selected_memo_id is not None:
            self.selected_memo_id = selected_memo_id

        if not memos:
            self.controls = [self._build_empty_state()]
            self._index.clear()
        else:
            updated_controls: list[ft.Control] = []
            new_index: dict[str, MemoCard] = {}
            for memo in memos:
                memo_id = str(memo.id)
                existing_card = self._index.get(memo_id)
                if existing_card is not None:
                    existing_card.refresh(memo, is_selected=self.selected_memo_id == memo_id)
                    updated_controls.append(existing_card)
                    new_index[memo_id] = existing_card
                else:
                    new_card = self._create_card(memo)
                    updated_controls.append(new_card)
                    new_index[memo_id] = new_card
            self.controls = updated_controls
            self._index = new_index

        if getattr(self, "page", None) is not None:
            self.update()

    def set_selected_memo(self, memo_id: str | None) -> None:
        self.selected_memo_id = memo_id
        # まず全てのカードの選択状態を更新（数が多い場合の最適化余地あり）
        for card in self._index.values():
            is_selected = memo_id is not None and str(card.memo.id) == memo_id
            card.update_selection(is_selected=is_selected)
        if getattr(self, "page", None) is not None:
            self.update()

    def _find_card(self, memo_id: str) -> MemoCard | None:
        for control in self.controls:
            if isinstance(control, MemoCard) and str(control.memo.id) == memo_id:
                return control
        return None
