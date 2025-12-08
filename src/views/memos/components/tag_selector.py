"""Tag Selector Component.

テンプレートの EditMemoScreen.tsx のタグ選択UIを参考にした、
タグ選択用のコンポーネント。

設計方針:
- ft.Container を継承し、タグのトグル選択を提供
- Props dataclass で表示データとコールバックを受け取る
- 選択中/未選択のタグを Badge で表示し、クリックでトグル
- タグの色を考慮した視覚的なフィードバック
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.theme import get_grey_color, get_on_primary_color, get_text_secondary_color

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import TagRead


@dataclass(frozen=True, slots=True)
class TagSelectorProps:
    """タグ選択UIの表示データ。

    Attributes:
        all_tags: 選択可能な全タグ
        selected_tag_names: 現在選択されているタグ名のリスト
        on_tag_toggle: タグがクリックされた時のコールバック
    """

    all_tags: list[TagRead]
    selected_tag_names: list[str]
    on_tag_toggle: Callable[[str], None]


class TagSelector(ft.Container):
    """タグ選択UI。

    テンプレートの EditMemoScreen.tsx に従い、タグのトグル選択を提供する。
    """

    def __init__(self, props: TagSelectorProps) -> None:
        """タグ選択UIを初期化する。

        Args:
            props: 表示データとコールバック
        """
        super().__init__()
        self.props = props
        self._build_ui()

    def _build_ui(self) -> None:
        """UIコンポーネントを構築する。"""
        if not self.props.all_tags:
            self.content = ft.Column(
                [
                    ft.Text("タグ", weight=ft.FontWeight.BOLD),
                    ft.Text("タグがありません", size=12, color=get_text_secondary_color()),
                ],
                spacing=6,
            )
            return

        # タグバッジのグリッド
        tag_badges: list[ft.Container] = []
        for tag in self.props.all_tags:
            is_selected = tag.name in self.props.selected_tag_names
            badge = self._create_tag_badge(tag, is_selected=is_selected)
            tag_badges.append(badge)

        # 選択中のタグ表示
        selected_section = self._build_selected_tags_section()

        self.content = ft.Column(
            [
                ft.Text("タグ", weight=ft.FontWeight.BOLD),
                ft.Text("メモにタグを付けて整理", size=12, color=get_text_secondary_color()),
                ft.Container(
                    content=ft.Row(tag_badges, wrap=True, spacing=8, run_spacing=8),
                    padding=ft.padding.only(top=8),
                ),
                selected_section,
            ],
            spacing=8,
        )

    def _create_tag_badge(self, tag: TagRead, *, is_selected: bool) -> ft.Container:
        """タグバッジを作成する。

        Args:
            tag: タグデータ
            is_selected: 選択状態

        Returns:
            タグバッジコンテナ
        """
        color = tag.color or get_grey_color(600)

        if is_selected:
            # 選択中: 背景色を適用
            badge = ft.Container(
                content=ft.Text(tag.name, size=12, color=get_on_primary_color()),
                bgcolor=color,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda _: self.props.on_tag_toggle(tag.name),
                tooltip=tag.description or tag.name,
            )
        else:
            # 未選択: アウトライン表示
            badge = ft.Container(
                content=ft.Text(tag.name, size=12, color=color),
                border=ft.border.all(1, color),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda _: self.props.on_tag_toggle(tag.name),
                tooltip=tag.description or tag.name,
            )

        return badge

    def _build_selected_tags_section(self) -> ft.Container:
        """選択中のタグ一覧セクションを構築する。

        Returns:
            選択中タグのコンテナ
        """
        if not self.props.selected_tag_names:
            return ft.Container()

        selected_badges = []
        for tag_name in self.props.selected_tag_names:
            tag = next((t for t in self.props.all_tags if t.name == tag_name), None)
            if tag is None:
                continue

            color = tag.color or get_grey_color(600)
            badge = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(tag_name, size=12, color=get_on_primary_color()),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=14,
                            icon_color=get_on_primary_color(),
                            on_click=lambda _, tn=tag_name: self.props.on_tag_toggle(tn),
                            tooltip=f"{tag_name}を削除",
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=color,
                border_radius=12,
                padding=ft.padding.only(left=12, right=4, top=4, bottom=4),
            )
            selected_badges.append(badge)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Divider(),
                    ft.Text("選択中のタグ:", size=12, color=get_text_secondary_color()),
                    ft.Row(selected_badges, wrap=True, spacing=8, run_spacing=8),
                ],
                spacing=8,
            ),
            padding=ft.padding.only(top=8),
        )

    def set_props(self, new_props: TagSelectorProps) -> None:
        """新しいPropsで再構築する。

        Args:
            new_props: 新しい表示データ
        """
        self.props = new_props
        self._build_ui()
        try:
            self.update()
        except Exception as e:
            logger.warning(f"Failed to update TagSelector: {e}")

    def rebuild(self) -> None:
        """UIを完全に再構築する。"""
        self._build_ui()
        try:
            self.update()
        except Exception as e:
            logger.warning(f"Failed to rebuild TagSelector: {e}")
