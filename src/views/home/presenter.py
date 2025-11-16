"""Home Presenter Layer.

【責務】
    Presenter層はView層から表示用ロジックを切り出し、UI構築を担当する。

    - データのフォーマット変換
    - コンポーネント用データモデルの生成
    - UI要素の生成（純粋関数として提供）
    - 表示用メッセージの提供

【責務外（他層の担当）】
    - 状態の保持 → State
    - イベントハンドリング → View
    - データの取得 → Controller

【アーキテクチャ上の位置づけ】
    View → Presenter.build_xxx()         # UI要素生成
         → Presenter.format_xxx()        # フォーマット

【提供する関数】
    - build_daily_review_card(): デイリーレビューカード構築
    - build_inbox_memo_item(): Inboxメモアイテム構築
    - build_stat_card(): 統計カード構築

# TODO: [ロジック担当者向け] デイリーレビューカードのアクセントカラー動的対応
# 実装箇所: src/views/home/presenter.py - build_daily_review_card()
# 依存: src/logic/services/ のデイリーレビュー生成ロジック
#
# 【現状の課題】
# - アクセントカラー(amber, blue, green等)がハードコードマップで管理されている
# - 新しいレビュータイプを追加する際に presenter.py の修正が必要
#
# 【実装提案】
# 1. Logic層でレビュー生成時にカラー情報も含める
#    例: {"message": "...", "color": "amber", "icon": "coffee", "severity": "info"}
#
# 2. theme.py に get_accent_colors() を追加して、color名から
#    背景色・ボーダー色・アイコン色のセットを返すヘルパーを提供
#
# 3. presenter.py のマップを theme.py のヘルパーに置き換え
#    メリット: 新しいアクセントカラー追加時に theme.py のみ修正で対応可能
#
# 【優先度】
# - Priority: Low (現状でも動作しているため)
# - 推奨実装時期: デイリーレビューロジック拡張時

# TODO: [ロジック担当者向け] AIステータスバッジのコンポーネント化
# 実装箇所: src/views/home/presenter.py - build_inbox_memo_item()
# 依存: なし(View層のみのリファクタリング)
#
# 【現状の課題】
# - AIステータスバッジの生成ロジックが build_inbox_memo_item() 内に埋め込まれている
# - 同じバッジを他のView(タスク一覧、検索結果等)で再利用できない
#
# 【実装提案】
# 1. 新しいヘルパー関数を追加
#    def build_ai_status_badge(status: str | None) -> ft.Container | None:
#        # AIステータスバッジを構築する(available/pending/not_requested)
#
# 2. バッジスタイルを theme.py に定義
#    @dataclass
#    class BadgeStyles:
#        success: dict  # AI提案あり
#        pending: dict  # AI処理中
#        neutral: dict  # AI未実行
#
# 3. 他Viewでも同じバッジを再利用可能に
#    例: タスク一覧でもAI提案状態を表示する場合など
#
# 【優先度】
# - Priority: Low (リファクタリング)
# - 推奨実装時期: AI機能を他Viewに展開する際
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from views.theme import (
    BORDER_RADIUS,
    BORDER_WIDTH,
    OPACITY,
    SPACING,
    UI_COLORS,
    create_medium_shadow,
    create_subtle_shadow,
    get_accent_background_color,
    get_accent_border_color,
    get_on_surface_color,
    get_outline_color,
    get_surface_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def build_daily_review_card(review: dict[str, Any], on_action_click: Callable[[str], None]) -> ft.Container:
    """デイリーレビューカードを構築する。

    Args:
        review: デイリーレビュー情報
        on_action_click: アクションボタンのクリックハンドラ

    Returns:
        デイリーレビューカードのコンテナ
    """
    icon_map = {
        "error": ft.Icons.GITE_ROUNDED,
        "coffee": ft.Icons.COFFEE,
        "play_arrow": ft.Icons.BOLT,
        "trending_up": ft.Icons.TRENDING_UP,
        "lightbulb": ft.Icons.AUTO_AWESOME,
        "check_circle": ft.Icons.CHECK_CIRCLE,
        "wb_sunny": ft.Icons.WB_SUNNY,
    }

    color_name = review.get("color", "primary")
    icon = icon_map.get(review.get("icon", ""), ft.Icons.INFO)
    bg_color = ft.Colors.with_opacity(OPACITY.subtle, get_accent_background_color(color_name))
    border_color = ft.Colors.with_opacity(OPACITY.border_light, get_accent_border_color(color_name))
    icon_color = get_on_surface_color()

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=24, color=icon_color),
                            padding=SPACING.sm + SPACING.xs,
                            bgcolor=get_surface_color(),
                            border_radius=BORDER_RADIUS.round,
                            shadow=create_medium_shadow(),
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        review.get("message", ""),
                                        size=18,
                                        weight=ft.FontWeight.NORMAL,
                                        color=get_on_surface_color(),
                                    ),
                                ],
                                spacing=0,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=SPACING.md,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(
                    content=ft.OutlinedButton(
                        text=review.get("action_text", ""),
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=lambda _: on_action_click(review.get("action_route", "")),
                        style=ft.ButtonStyle(
                            color=get_on_surface_color(),
                            bgcolor=get_surface_color(),
                            side=ft.BorderSide(
                                BORDER_WIDTH.thin,
                                ft.Colors.with_opacity(OPACITY.border_light, get_outline_color()),
                            ),
                        ),
                    ),
                    margin=ft.margin.only(top=SPACING.sm),
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(SPACING.lg),
        bgcolor=bg_color,
        border_radius=BORDER_RADIUS.lg,
        border=ft.border.all(BORDER_WIDTH.thin, border_color),
    )


def build_inbox_memo_item(memo: dict[str, Any], on_click: Callable[[str], None]) -> ft.Container:
    """Inboxメモアイテムを構築する。

    Args:
        memo: メモ情報
        on_click: クリックハンドラ

    Returns:
        メモアイテムのコンテナ
    """
    max_content_length = 100
    content_preview = (
        memo["content"][:max_content_length] + "..." if len(memo["content"]) > max_content_length else memo["content"]
    )

    status_badge = None
    ai_status = memo.get("ai_suggestion_status")

    if ai_status == "available":
        status_badge = ft.Container(
            content=ft.Text(
                "AI提案あり",
                size=11,
                weight=ft.FontWeight.W_500,
                color=UI_COLORS.primary_dark,
            ),
            padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=BORDER_RADIUS.sm,
            border=ft.border.all(BORDER_WIDTH.thin, ft.Colors.BLUE_300),
        )
    elif ai_status == "pending":
        status_badge = ft.Container(
            content=ft.Text(
                "AI処理中",
                size=11,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.with_opacity(OPACITY.high, get_text_secondary_color()),
            ),
            padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
            bgcolor=ft.Colors.with_opacity(OPACITY.light, ft.Colors.BLUE_GREY_100),
            border_radius=BORDER_RADIUS.sm,
            border=ft.border.all(
                BORDER_WIDTH.thin,
                ft.Colors.with_opacity(OPACITY.border_medium, get_outline_color()),
            ),
        )
    elif ai_status == "not_requested":
        status_badge = ft.Container(
            content=ft.Text(
                "AI未実行",
                size=11,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.with_opacity(OPACITY.medium, get_text_secondary_color()),
            ),
            padding=ft.padding.symmetric(horizontal=SPACING.sm, vertical=SPACING.xs),
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=BORDER_RADIUS.sm,
            border=ft.border.all(
                BORDER_WIDTH.thin,
                ft.Colors.with_opacity(OPACITY.border_medium, get_outline_color()),
            ),
        )

    title_row = ft.Row(
        [
            ft.Text(
                memo.get("title", ""),
                size=14,
                weight=ft.FontWeight.NORMAL,
            ),
        ],
        spacing=SPACING.xs,
    )
    if status_badge:
        title_row.controls.append(status_badge)

    return ft.Container(
        content=ft.Column(
            [
                title_row,
                ft.Text(
                    content_preview,
                    size=14,
                    color=ft.Colors.with_opacity(OPACITY.medium, get_on_surface_color()),
                    max_lines=2,
                ),
            ],
            spacing=SPACING.xs,
            tight=True,
        ),
        padding=SPACING.sm + SPACING.xs,
        bgcolor=get_surface_color(),
        border_radius=BORDER_RADIUS.md,
        border=ft.border.all(
            BORDER_WIDTH.thin,
            ft.Colors.with_opacity(OPACITY.border_light, get_outline_color()),
        ),
        on_click=lambda _: on_click(memo.get("id", "")),
        ink=True,
    )


def build_stat_card(title: str, value: str, subtitle: str, icon: str, on_click: Callable[[], None]) -> ft.Container:
    """統計カードを構築する。

    Args:
        title: カードタイトル
        value: 表示値
        subtitle: サブタイトル
        icon: アイコン
        on_click: クリックハンドラ

    Returns:
        統計カードのコンテナ
    """
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            title,
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Icon(icon, size=20, color=get_on_surface_color()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=SPACING.sm),
                ft.Text(
                    value,
                    size=36,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    subtitle,
                    size=14,
                    color=ft.Colors.with_opacity(OPACITY.medium, get_text_secondary_color()),
                ),
            ],
            spacing=0,
            tight=True,
        ),
        padding=ft.padding.all(SPACING.lg),
        bgcolor=get_surface_color(),
        border_radius=BORDER_RADIUS.lg,
        border=ft.border.all(
            BORDER_WIDTH.thin,
            ft.Colors.with_opacity(OPACITY.light, get_outline_color()),
        ),
        shadow=create_subtle_shadow(),
        on_click=lambda _: on_click(),
        ink=True,
        col={"xs": 12, "sm": 6, "md": 4},
    )
