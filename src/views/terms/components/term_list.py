"""用語リストコンポーネント。

【責務】
    用語カードのリスト表示を担当。
    - Props駆動のカードリスト描画
    - 空状態の表示
    - カードのクリックイベントハンドリング
    - 差分更新による効率的な再描画

【非責務】
    - データ取得・変換 → Presenter
    - 状態管理 → State/Controller
    - ビジネスロジック → Controller
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from collections.abc import Callable

    from .term_card import TermCardData


@dataclass(frozen=True, slots=True)
class TermListProps:
    """TermList初期化プロパティ。

    Attributes:
        on_item_click: アイテムクリック時のコールバック（用語IDを引数にとる）
        empty_message: 空状態時のメッセージ
    """

    on_item_click: Callable[[str], None] | None = None
    empty_message: str = "用語がありません"


class TermList:
    """用語リスト表示コンポーネント（非継承パターン）。"""

    def __init__(self, props: TermListProps) -> None:
        """Initialize term list.

        Args:
            props: 初期化プロパティ
        """
        self._props = props
        self._cards: list[ft.Control] = []
        self._list = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    @property
    def control(self) -> ft.Control:
        """コントロールを取得する。

        Returns:
            リストコントロール
        """
        return self._list

    def set_cards(self, cards: list[TermCardData]) -> None:
        """カードリストを設定して再描画する。

        Args:
            cards: 表示するカードデータのリスト
        """
        from .term_card import TermCard

        self._cards = []
        self._list.controls = []

        if not cards:
            self._list.controls = [self._build_empty_state()]
        else:
            for data in cards:
                card = TermCard(data)
                self._cards.append(card)
                self._list.controls.append(card)

        with contextlib.suppress(AssertionError):
            self._list.update()

    def _build_empty_state(self) -> ft.Control:
        """空状態の表示を構築する。

        Returns:
            空状態コントロール
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE_OUTLINED,
                        size=48,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Text(
                        self._props.empty_message,
                        size=16,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=32,
            alignment=ft.alignment.center,
        )

    def update_props(self, props: TermListProps) -> None:
        """プロパティを更新する。

        Args:
            props: 新しいプロパティ
        """
        self._props = props
