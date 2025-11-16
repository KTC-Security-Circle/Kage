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
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from views.theme import SPACING

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
    # アイコンマッピング
    icon_map = {
        "error": ft.Icons.GITE_ROUNDED,
        "coffee": ft.Icons.COFFEE,
        "play_arrow": ft.Icons.BOLT,
        "trending_up": ft.Icons.TRENDING_UP,
        "lightbulb": ft.Icons.AUTO_AWESOME,
        "check_circle": ft.Icons.CHECK_CIRCLE,
        "wb_sunny": ft.Icons.WB_SUNNY,
    }

    # 背景色マッピング
    bg_color_map = {
        "amber": ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
        "blue": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
        "green": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
        "primary": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
        "purple": ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800),
    }

    # ボーダー色マッピング
    border_color_map = {
        "amber": ft.Colors.AMBER_400,
        "blue": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
        "green": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
        "primary": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
        "purple": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800),
    }

    # アイコン色
    icon_color_map = {
        "amber": ft.Colors.BLUE_GREY_900,
        "blue": ft.Colors.BLUE_GREY_900,
        "green": ft.Colors.BLUE_GREY_900,
        "primary": ft.Colors.BLUE_GREY_900,
        "purple": ft.Colors.BLUE_GREY_900,
    }

    icon = icon_map.get(review.get("icon", ""), ft.Icons.INFO)
    bg_color = bg_color_map.get(review.get("color", ""), ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_800))
    border_color = border_color_map.get(review.get("color", ""), ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800))
    icon_color = icon_color_map.get(review.get("color", ""), ft.Colors.BLUE_GREY_900)

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=24, color=icon_color),
                            padding=12,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=50,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=2,
                                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                offset=ft.Offset(0, 1),
                            ),
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        review.get("message", ""),
                                        size=18,
                                        weight=ft.FontWeight.NORMAL,
                                        color=ft.Colors.BLUE_GREY_900,
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
                            color=ft.Colors.BLUE_GREY_900,
                            bgcolor=ft.Colors.WHITE,
                            side=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800)),
                        ),
                    ),
                    margin=ft.margin.only(top=SPACING.sm),
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(24),
        bgcolor=bg_color,
        border_radius=12,
        border=ft.border.all(1, border_color),
    )


def build_inbox_memo_item(memo: dict[str, Any], on_click: Callable[[int], None]) -> ft.Container:
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

    # AI提案ステータスのバッジ
    status_badge = None
    ai_status = memo.get("ai_suggestion_status")

    if ai_status == "available":
        status_badge = ft.Container(
            content=ft.Text(
                "AI提案あり",
                size=11,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.BLUE_700,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=4,
            border=ft.border.all(1, ft.Colors.BLUE_300),
        )
    elif ai_status == "pending":
        status_badge = ft.Container(
            content=ft.Text(
                "AI処理中",
                size=11,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.with_opacity(0.7, ft.Colors.BLUE_GREY_700),
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_100),
            border_radius=4,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)),
        )
    elif ai_status == "not_requested":
        status_badge = ft.Container(
            content=ft.Text(
                "AI未実行",
                size=11,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.with_opacity(0.6, ft.Colors.BLUE_GREY_700),
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=4,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)),
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
                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                    max_lines=2,
                ),
            ],
            spacing=4,
            tight=True,
        ),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_800)),
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
                        ft.Icon(icon, size=20, color=ft.Colors.BLUE_GREY_900),
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
                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                ),
            ],
            spacing=0,
            tight=True,
        ),
        padding=ft.padding.all(24),
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=2,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 1),
        ),
        on_click=lambda _: on_click(),
        ink=True,
        col={"xs": 12, "sm": 6, "md": 4},
    )
