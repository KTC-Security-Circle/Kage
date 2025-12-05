"""タグ詳細パネルコンポーネント (Props駆動)

選択されたタグの詳細情報と関連アイテム（メモ・タスク）を表示するパネル。
`src/views_old/template/src/components/TagsScreen.tsx` の詳細パネルを参考に実装。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from views.theme import (
    get_grey_color,
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_tag_icon_bg_opacity,
    get_task_status_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class RelatedItem:
    """関連アイテム（メモ・タスク）の表示データ"""

    id: str
    title: str
    description: str
    status: str | None = None
    status_label: str | None = None


@dataclass(frozen=True, slots=True)
class TagDetailData:
    """タグ詳細の表示データ"""

    tag_id: str
    name: str
    color: str
    description: str
    created_at: str
    updated_at: str
    total_count: int
    memo_count: int
    task_count: int
    related_memos: list[RelatedItem]
    related_tasks: list[RelatedItem]


@dataclass(frozen=True, slots=True)
class TagDetailPanelProps:
    """タグ詳細パネルのProps"""

    detail_data: TagDetailData | None
    on_edit: Callable[[ft.ControlEvent], None]
    on_memo_click: Callable[[ft.ControlEvent, str], None]
    on_task_click: Callable[[ft.ControlEvent, str], None]


class TagDetailPanel(ft.Container):
    """Propsで駆動されるタグ詳細パネル"""

    def __init__(self, props: TagDetailPanelProps) -> None:
        super().__init__()
        self._props = props
        self.content = self._build(props)
        self.padding = 16
        self.expand = True

    def _build(self, props: TagDetailPanelProps) -> ft.Control:
        """パネルコンテンツを構築する"""
        if not props.detail_data:
            return self._build_empty_state()

        data = props.detail_data

        # タグヘッダーカード
        header_card = self._build_header_card(data, props.on_edit)

        # 関連メモセクション
        memos_section = self._build_related_items_section(
            title="メモ",
            icon=ft.Icons.FILE_PRESENT,
            items=data.related_memos,
            count=data.memo_count,
            on_item_click=props.on_memo_click,
        )

        # 関連タスクセクション
        tasks_section = self._build_related_items_section(
            title="タスク",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            items=data.related_tasks,
            count=data.task_count,
            on_item_click=props.on_task_click,
        )

        # 関連セクションの表示（0件の場合も表示）
        sections = [memos_section, tasks_section]

        # メモ・タスク両方が0の場合は未使用メッセージも追加
        if data.memo_count == 0 and data.task_count == 0:
            sections.append(self._build_no_items_message())

        return ft.Column(
            controls=[header_card, *sections],
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_empty_state(self) -> ft.Control:
        """空状態の表示（プロジェクトパターン準拠）"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.LABEL_OUTLINE,
                            size=48,
                            color=get_outline_color(),
                        ),
                        ft.Text(
                            "タグを選択して詳細を表示",
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=get_text_secondary_color(),
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=48,
            ),
            expand=True,
        )

    def _build_no_items_message(self) -> ft.Control:
        """タグが未使用の場合のメッセージ"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.INFO_OUTLINE,
                            size=32,
                            color=get_primary_color(),
                        ),
                        ft.Text(
                            "このタグはまだ使用されていません",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=get_text_secondary_color(),
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "タスクやメモに付与すると、ここに表示されます",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=get_text_secondary_color(),
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=40,
                alignment=ft.alignment.center,
            ),
            elevation=1,
        )

    def _build_header_card(self, data: TagDetailData, on_edit: Callable[[ft.ControlEvent], None]) -> ft.Control:
        """ヘッダーカードを構築する"""
        # カラー付きアイコン
        color_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.LABEL,
                size=24,
                color=data.color,
            ),
            width=48,
            height=48,
            border_radius=ft.border_radius.all(24),
            bgcolor=ft.Colors.with_opacity(get_tag_icon_bg_opacity(), data.color),
            alignment=ft.alignment.center,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # ヘッダー（タイトル + ステータス）
                        ft.Row(
                            controls=[
                                color_icon,
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            data.name,
                                            theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{data.created_at} 作成",
                                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                            color=get_text_secondary_color(),
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="編集",
                                    on_click=on_edit,
                                    icon_color=get_text_secondary_color(),
                                ),
                            ],
                            spacing=12,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # Divider
                        ft.Divider(height=1, color=get_outline_color()),
                        # 説明セクション
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "説明",
                                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                                    color=get_text_secondary_color(),
                                ),
                                ft.Text(
                                    data.description or "（説明なし）",
                                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                ),
                            ],
                            spacing=8,
                        ),
                        # 統計情報
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "統計",
                                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                                    color=get_text_secondary_color(),
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.DESCRIPTION_OUTLINED,
                                                    size=16,
                                                    color=get_text_secondary_color(),
                                                ),
                                                ft.Text(
                                                    f"{data.memo_count} メモ",
                                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                                    color=get_text_secondary_color(),
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.TASK_ALT,
                                                    size=16,
                                                    color=get_text_secondary_color(),
                                                ),
                                                ft.Text(
                                                    f"{data.task_count} タスク",
                                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                                    color=get_text_secondary_color(),
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                f"合計 {data.total_count}",
                                                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                                                color=get_on_primary_color(),
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            bgcolor=get_primary_color(),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            border_radius=12,
                                        ),
                                    ],
                                    spacing=16,
                                ),
                            ],
                            spacing=8,
                        ),
                        # メタデータ
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CALENDAR_TODAY,
                                            size=16,
                                            color=get_text_secondary_color(),
                                        ),
                                        ft.Text(
                                            f"作成: {data.created_at}",
                                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                                            color=get_text_secondary_color(),
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.UPDATE,
                                            size=16,
                                            color=get_text_secondary_color(),
                                        ),
                                        ft.Text(
                                            f"更新: {data.updated_at}",
                                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                                            color=get_text_secondary_color(),
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=20,
                ),
                padding=24,
            ),
            elevation=2,
        )

    def _build_related_items_section(
        self,
        title: str,
        icon: str,
        items: list[RelatedItem],
        count: int,
        on_item_click: Callable[[ft.ControlEvent, str], None],
    ) -> ft.Control:
        """関連アイテムセクションを構築する"""
        # 0件の場合も明示的にセクションを表示
        if count == 0:
            empty_message = ft.Text(
                "関連なし",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=get_grey_color(500),
                italic=True,
            )
            item_widgets = [empty_message]
        else:
            item_widgets = [self._build_related_item_card(item, on_item_click) for item in items]

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # セクションヘッダー
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(icon, size=20, color=get_primary_color()),
                                    ft.Text(
                                        f"{title} ({count})",
                                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=8),
                        ),
                        ft.Divider(height=1),
                        # アイテムリスト
                        ft.Column(
                            controls=item_widgets,
                            spacing=8,
                        ),
                    ],
                    spacing=8,
                ),
                padding=16,
            ),
            elevation=1,
        )

    def _build_related_item_card(
        self,
        item: RelatedItem,
        on_click: Callable[[ft.ControlEvent, str], None],
    ) -> ft.Control:
        """関連アイテムカードを構築する"""
        # TODO: 関連アイテムのプレビュー機能拡張
        # 理由: タイトル・説明以外にも作成日、更新日、優先度などの表示ニーズがある
        # 実装: RelatedItem dataclassにフィールド追加、表示ロジックに反映
        # 置換先: このファイル内の RelatedItem と _build_related_item_card
        # 注意: 情報過多にならないよう、必要最小限のメタデータに留める

        # ステータスバッジ（ある場合のみ）
        status_badge = None
        if item.status and item.status_label:
            badge_color = get_task_status_color(item.status)
            status_badge = ft.Container(
                content=ft.Text(
                    item.status_label,
                    size=11,
                    color=get_on_primary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                bgcolor=badge_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=ft.border_radius.all(12),
            )

        return ft.Container(
            content=ft.Row(
                controls=[
                    # 左側: アイコンとコンテンツ
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                size=16,
                                color=get_grey_color(500),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                item.title,
                                                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            status_badge if status_badge else ft.Container(),
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Text(
                                        item.description,
                                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                                        color=get_grey_color(600),
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
            ),
            padding=12,
            border=ft.border.all(1, get_grey_color(300)),
            border_radius=ft.border_radius.all(8),
            on_click=lambda e, item_id=item.id: on_click(e, item_id),
            ink=True,
        )

    def set_props(self, props: TagDetailPanelProps) -> None:
        """Propsを反映し直し、必要時のみ再構築する"""
        self._props = props
        try:
            self.content = self._build(props)
            self.update()
        except (AttributeError, RuntimeError) as exc:
            logger.warning(f"TagDetailPanel.set_props skipped: {exc}")
