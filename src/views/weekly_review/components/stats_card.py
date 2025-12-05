"""週次レビューコンポーネント - 統計カード

統計情報を表示するカードコンポーネント。
"""

from contextlib import suppress
from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True, slots=True)
class StatsCardProps:
    """統計カードのプロパティ"""

    title: str
    value: str
    subtitle: str
    icon_name: str


class StatsCard(ft.Container):
    """統計表示カードコンポーネント

    週次レビューの統計情報を表示するカード。
    """

    def __init__(self, props: StatsCardProps) -> None:
        """統計カードを初期化

        Args:
            props: カードのプロパティ
        """
        super().__init__()
        self.props = props
        self.content = self._build_content()
        self.expand = True

    def _build_content(self) -> ft.Card:
        """カードコンテンツを構築

        Returns:
            構築されたカード
        """
        # ヘッダー（タイトルとアイコン）
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        self.props.title,
                        size=14,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Icon(
                        name=self.props.icon_name,
                        size=16,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=8),
        )

        # メイン値
        value_text = ft.Text(
            self.props.value,
            size=24,
            weight=ft.FontWeight.BOLD,
        )

        # サブタイトル
        subtitle_text = ft.Text(
            self.props.subtitle,
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )

        # カードコンテンツ
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    value_text,
                    subtitle_text,
                ],
                spacing=4,
            ),
            padding=ft.padding.all(16),
        )

        return ft.Card(
            content=card_content,
            elevation=1,
        )

    def set_props(self, new_props: StatsCardProps) -> None:
        """プロパティを更新してカードを再構築

        Args:
            new_props: 新しいプロパティ
        """
        self.props = new_props
        self.content = self._build_content()
        with suppress(Exception):
            self.update()
