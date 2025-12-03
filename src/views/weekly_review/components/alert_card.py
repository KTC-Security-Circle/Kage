"""週次レビューコンポーネント - アラートカード

重要な通知や警告を表示するカードコンポーネント。
"""

from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True, slots=True)
class AlertCardProps:
    """アラートカードのプロパティ"""

    title: str
    message: str
    action_label: str
    icon_name: str
    on_action: Callable[[], None]


class AlertCard(ft.Container):
    """アラート表示カードコンポーネント

    重要な通知や警告を表示する。
    """

    def __init__(self, props: AlertCardProps) -> None:
        """アラートカードを初期化

        Args:
            props: カードのプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()

    def _build_content(self) -> ft.Card:
        """カードコンテンツを構築

        Returns:
            構築されたカード
        """
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=self.props.icon_name,
                                size=20,
                                color=ft.Colors.ORANGE_600,
                            ),
                            ft.Text(
                                self.props.title,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        self.props.message,
                        size=12,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        text=self.props.action_label,
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=lambda _: self.props.on_action(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.ORANGE_100,
                            color=ft.Colors.ORANGE_900,
                        ),
                    ),
                ],
                spacing=8,
            ),
            padding=20,
        )

        self.bgcolor = ft.Colors.ORANGE_50
        return ft.Card(
            content=card_content,
            elevation=2,
        )

    def set_props(self, new_props: AlertCardProps) -> None:
        """プロパティを更新してカードを再構築

        Args:
            new_props: 新しいプロパティ
        """
        self.props = new_props
        self.content = self._build_content()
        with suppress(Exception):
            self.update()
