"""Term detail component for displaying full term information.

【責務】
    選択された用語の詳細表示を担当。
    - Props駆動の不変データ受信
    - 詳細情報の構造化表示
    - 編集/外部リンクのアクションコールバック
    - 関連アイテム（メモ・タスク）の表示

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

from views.sample import SampleTermStatus

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class RelatedItemData:
    """関連アイテム表示用データ。"""

    item_id: str
    title: str
    item_type: str  # "memo" or "task"
    badge_text: str | None = None


@dataclass(frozen=True, slots=True)
class TermDetailData:
    """詳細パネル表示用のデータ。"""

    term_id: str
    title: str
    key: str
    description: str
    status: SampleTermStatus
    status_text: str
    synonyms: tuple[str, ...]
    tags: tuple[str, ...]
    source_url: str | None
    created_date: str
    updated_date: str
    related_items: list[RelatedItemData]


@dataclass(frozen=True, slots=True)
class DetailPanelProps:
    """TermDetailPanel初期化プロパティ。"""

    on_edit: Callable[[str], None] | None = None
    on_tag_click: Callable[[str], None] | None = None
    on_item_click: Callable[[str, str], None] | None = None  # (item_type, item_id)


class TermDetailPanel:
    """右ペイン用の詳細表示コンポーネント（非継承パターン）。"""

    def __init__(self, props: DetailPanelProps) -> None:
        """Initialize term detail panel.

        Args:
            props: 初期化プロパティ
        """
        self._props = props
        self._data: TermDetailData | None = None
        self._root = ft.Container(expand=True)

    @property
    def control(self) -> ft.Control:
        """コントロールを取得する（初回はプレースホルダ表示）。"""
        if self._root.content is None:
            self._root.content = self._placeholder()
        return self._root

    def set_item(self, data: TermDetailData | None) -> None:
        """詳細対象を切り替えて再描画する。

        Args:
            data: 表示する用語の詳細データ
        """
        self._data = data
        if not data:
            self._root.content = self._placeholder()
            with contextlib.suppress(AssertionError):
                self._root.update()
            return

        self._root.content = self._build_detail_view(data)
        with contextlib.suppress(AssertionError):
            self._root.update()

    def _placeholder(self) -> ft.Control:
        """プレースホルダ表示を構築する。"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE_OUTLINED,
                        size=64,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Text(
                        "用語を選択して詳細を表示",
                        size=18,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=48,
            alignment=ft.alignment.center,
            expand=True,
        )

    def _build_detail_view(self, data: TermDetailData) -> ft.Control:
        """詳細ビューを構築する。

        Args:
            data: 表示する詳細データ

        Returns:
            詳細表示用のコントロール
        """
        return ft.Card(
            expand=True,
            content=ft.Container(
                expand=True,
                content=ft.Column(
                    controls=[
                        self._build_header(data),
                        ft.Divider(),
                        self._build_description_section(data),
                        self._build_synonyms_section(data),
                        self._build_tags_section(data),
                        self._build_source_section(data),
                        ft.Divider(),
                        self._build_metadata(data),
                        self._build_related_items_section(data),
                        ft.Divider(),
                        self._build_edit_button(data),
                    ],
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=24,
            ),
        )

    def _build_header(self, data: TermDetailData) -> ft.Control:
        """ヘッダーセクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            ヘッダーコントロール
        """
        status_badge = self._get_status_badge(data.status, data.status_text)

        return ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.BOOK_ROUNDED,
                            size=32,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    data.title,
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        data.key,
                                        size=13,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        font_family="monospace",
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    bgcolor=ft.Colors.SURFACE,
                                    border_radius=4,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=16,
                    expand=True,
                ),
                status_badge,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _get_status_badge(self, status: SampleTermStatus, status_text: str) -> ft.Control:
        """ステータスバッジを取得する。

        Args:
            status: 用語ステータス
            status_text: ステータステキスト

        Returns:
            バッジコントロール
        """
        status_config = {
            SampleTermStatus.APPROVED: {
                "bgcolor": ft.Colors.BLUE_600,
                "color": ft.Colors.WHITE,
            },
            SampleTermStatus.DRAFT: {
                "bgcolor": ft.Colors.GREY_300,
                "color": ft.Colors.ON_SURFACE,
            },
            SampleTermStatus.DEPRECATED: {
                "bgcolor": ft.Colors.GREY_300,
                "color": ft.Colors.ON_SURFACE,
            },
        }

        config = status_config.get(status, status_config[SampleTermStatus.DRAFT])

        return ft.Container(
            content=ft.Text(
                status_text,
                size=14,
                color=config["color"],
                weight=ft.FontWeight.BOLD,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor=config["bgcolor"],
            border_radius=8,
        )

    def _build_description_section(self, data: TermDetailData) -> ft.Control:
        """説明セクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            説明セクションコントロール
        """
        return ft.Column(
            controls=[
                ft.Text(
                    "説明",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    data.description,
                    size=15,
                    color=ft.Colors.ON_SURFACE,
                ),
            ],
            spacing=8,
        )

    def _build_synonyms_section(self, data: TermDetailData) -> ft.Control:
        """同義語セクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            同義語セクションコントロール
        """
        if not data.synonyms:
            return ft.Container()

        synonym_chips = [
            ft.Container(
                content=ft.Text(
                    synonym,
                    size=14,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border_radius=16,
            )
            for synonym in data.synonyms
        ]

        return ft.Column(
            controls=[
                ft.Text(
                    "同義語",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Row(
                    controls=synonym_chips,
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=8,
        )

    def _build_tags_section(self, data: TermDetailData) -> ft.Control:
        """タグセクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            タグセクションコントロール
        """
        if not data.tags:
            return ft.Container()

        tag_chips = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.TAG,
                            size=16,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            tag_name,
                            size=14,
                            color=ft.Colors.PRIMARY,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.all(1, ft.Colors.PRIMARY),
                border_radius=16,
                ink=True,
                on_click=lambda _e, tag=tag_name: self._props.on_tag_click(tag) if self._props.on_tag_click else None,
            )
            for tag_name in data.tags
        ]

        return ft.Column(
            controls=[
                ft.Text(
                    "タグ",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Row(
                    controls=tag_chips,
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=8,
        )

    def _build_source_section(self, data: TermDetailData) -> ft.Control:
        """出典URLセクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            出典セクションコントロール
        """
        if not data.source_url:
            return ft.Container()

        return ft.Column(
            controls=[
                ft.Text(
                    "出典",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.ElevatedButton(
                    text="外部リンクを開く",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda _: self._handle_source_click(data.source_url),
                ),
            ],
            spacing=8,
        )

    def _build_metadata(self, data: TermDetailData) -> ft.Control:
        """メタデータセクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            メタデータセクションコントロール
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "作成日",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                data.created_date,
                                size=14,
                                color=ft.Colors.ON_SURFACE,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "最終更新",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                data.updated_date,
                                size=14,
                                color=ft.Colors.ON_SURFACE,
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=32,
            ),
            padding=ft.padding.all(16),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )

    def _build_related_items_section(self, data: TermDetailData) -> ft.Control:
        """関連アイテムセクションを構築する。

        Args:
            data: 詳細データ

        Returns:
            関連アイテムセクションコントロール
        """
        if not data.related_items:
            return ft.Container()

        # メモとタスクに分類
        related_memos = [item for item in data.related_items if item.item_type == "memo"]
        related_tasks = [item for item in data.related_items if item.item_type == "task"]

        sections = []

        if related_memos:
            sections.append(self._build_related_item_list("関連メモ", related_memos, "memo"))

        if related_tasks:
            sections.append(self._build_related_item_list("関連タスク", related_tasks, "task"))

        if not sections:
            return ft.Container()

        return ft.Column(
            controls=[
                ft.Text(
                    "関連アイテム",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                *sections,
            ],
            spacing=16,
        )

    def _build_related_item_list(self, title: str, items: list[RelatedItemData], item_type: str) -> ft.Control:
        """関連アイテムリストを構築する。

        Args:
            title: セクションタイトル
            items: 関連アイテムリスト
            item_type: アイテムタイプ（"memo" or "task"）

        Returns:
            関連アイテムリストコントロール
        """
        max_display = 3

        item_controls = []
        for item in items[:max_display]:  # 最大3件まで表示
            row_controls: list[ft.Control] = [ft.Text(item.title, size=14)]
            if item.badge_text:
                row_controls.append(
                    ft.Container(
                        content=ft.Text(
                            item.badge_text,
                            size=12,
                            color=ft.Colors.ON_SECONDARY_CONTAINER,
                        ),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        border_radius=12,
                    )
                )

            item_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=row_controls,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.all(12),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    ink=True,
                    on_click=lambda _e, item_id=item.item_id: self._props.on_item_click(item_type, item_id)
                    if self._props.on_item_click
                    else None,
                )
            )

        if len(items) > max_display:
            item_controls.append(
                ft.Text(
                    f"他 {len(items) - max_display} 件",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            )

        return ft.Column(
            controls=[
                ft.Text(
                    f"{title} ({len(items)})",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Column(
                    controls=item_controls,
                    spacing=8,
                ),
            ],
            spacing=8,
        )

    def _build_edit_button(self, data: TermDetailData) -> ft.Control:
        """編集ボタンを構築する。

        Args:
            data: 詳細データ

        Returns:
            編集ボタンコントロール
        """
        return ft.ElevatedButton(
            text="編集",
            icon=ft.Icons.EDIT,
            on_click=lambda _: self._handle_edit(data.term_id),
            width=None,
        )

    def _handle_edit(self, term_id: str) -> None:
        """編集ボタンクリックをハンドリングする。

        Args:
            term_id: 用語ID
        """
        if self._props.on_edit:
            self._props.on_edit(term_id)

    def _handle_source_click(self, source_url: str | None) -> None:
        """出典リンククリックをハンドリングする。

        Args:
            source_url: 出典URL
        """
        if source_url and self._root.page:
            self._root.page.launch_url(source_url)
