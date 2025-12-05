"""週次レビューコンポーネント - チェックリスト

GTD週次レビューのチェックリストコンポーネント。
"""

from collections.abc import Callable, Sequence
from contextlib import suppress
from dataclasses import dataclass

import flet as ft

from views.weekly_review.presenter import ChecklistItemData


@dataclass(frozen=True, slots=True)
class ReviewChecklistProps:
    """レビューチェックリストのプロパティ"""

    items: Sequence[ChecklistItemData]
    on_toggle: Callable[[str], None]


class ReviewChecklist(ft.Container):
    """週次レビューチェックリストコンポーネント"""

    def __init__(self, props: ReviewChecklistProps) -> None:
        """チェックリストを初期化

        Args:
            props: チェックリストのプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()
        self.expand = True

    def _build_content(self) -> ft.Card:
        """チェックリストコンテンツを構築

        Returns:
            構築されたカード
        """
        checklist_items = []

        for item_data in self.props.items:
            # チェックボックス
            checkbox = ft.Checkbox(
                value=item_data.completed,
                on_change=lambda _e, item_id=item_data.id: self._handle_toggle(item_id),
            )

            # ラベル
            label = ft.Text(
                item_data.label,
                size=14,
                color=ft.Colors.ON_SURFACE if not item_data.completed else ft.Colors.OUTLINE,
                weight=ft.FontWeight.NORMAL if not item_data.completed else ft.FontWeight.W_300,
            )

            # 行コンテナ
            row_container = ft.Container(
                content=ft.Row(
                    controls=[checkbox, label],
                    spacing=12,
                    tight=True,
                ),
                padding=12,
                border_radius=8,
                # on_hover=self._on_hover,  # TODO: HoverEvent型の問題を解決
            )

            checklist_items.append(row_container)

        # カード内容
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_OUTLINE,
                                size=20,
                                color=ft.Colors.PRIMARY,
                            ),
                            ft.Text(
                                "週次レビューチェックリスト",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        "GTDの週次レビュープロセスに従って、システムを整理しましょう",
                        size=12,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Divider(height=20),
                    ft.Column(
                        controls=checklist_items,
                        spacing=4,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=12,
            ),
            padding=20,
        )

        return ft.Card(
            content=card_content,
            elevation=2,
        )

    def _handle_toggle(self, item_id: str) -> None:
        """チェックボックストグル処理

        Args:
            item_id: 項目ID
        """
        self.props.on_toggle(item_id)

    def _on_hover(self, e: ft.HoverEvent) -> None:
        """ホバー時の処理

        Args:
            e: ホバーイベント
        """
        e.control.bgcolor = ft.Colors.SURFACE if e.data == "true" else None
        with suppress(Exception):
            e.control.update()

    def update_items(self, new_items: Sequence[ChecklistItemData]) -> None:
        """チェックリスト項目を更新

        Args:
            new_items: 新しい項目リスト
        """
        self.props = ReviewChecklistProps(
            items=new_items,
            on_toggle=self.props.on_toggle,
        )
        self.content = self._build_content()
        with suppress(Exception):
            self.update()
