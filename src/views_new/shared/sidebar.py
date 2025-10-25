"""サイドバー・ナビゲーション実装。

このモジュールは、アプリケーション全体で使用するサイドバーナビゲーションを提供します。
各ページへの移動リンク、現在の選択状態の表示、テーマに対応したスタイリングを含みます。
"""

from __future__ import annotations

import flet as ft

from views_new.theme import SPACING, get_dark_color, get_light_color


class NavigationItem:
    """ナビゲーション項目のデータクラス。"""

    def __init__(
        self,
        label: str,
        route: str,
        icon: str,
        selected_icon: str | None = None,
    ) -> None:
        """NavigationItemを初期化する。

        Args:
            label: 表示ラベル
            route: 対応するルート
            icon: 通常時のアイコン
            selected_icon: 選択時のアイコン（省略時は通常アイコンを使用）
        """
        self.label = label
        self.route = route
        self.icon = icon
        self.selected_icon = selected_icon or icon


# Navigation items configuration
NAVIGATION_ITEMS = [
    NavigationItem("ホーム", "/", ft.Icons.HOME_OUTLINED, ft.Icons.HOME),
    NavigationItem("プロジェクト", "/projects", ft.Icons.FOLDER_OUTLINED, ft.Icons.FOLDER),
    NavigationItem("タグ", "/tags", ft.Icons.LOCAL_OFFER_OUTLINED, ft.Icons.LOCAL_OFFER),
    NavigationItem("タスク", "/tasks", ft.Icons.TASK_OUTLINED, ft.Icons.TASK),
    NavigationItem("メモ", "/memos", ft.Icons.NOTE_OUTLINED, ft.Icons.NOTE),
    NavigationItem("用語集", "/terms", ft.Icons.MENU_BOOK_OUTLINED, ft.Icons.MENU_BOOK),
    NavigationItem("週間レビュー", "/weekly-review", ft.Icons.ASSESSMENT_OUTLINED, ft.Icons.ASSESSMENT),
    NavigationItem("設定", "/settings", ft.Icons.SETTINGS_OUTLINED, ft.Icons.SETTINGS),
]


def build_sidebar(page: ft.Page, current_route: str = "/") -> ft.Container:
    """サイドバーを構築する。

    Args:
        page: Fletページオブジェクト
        current_route: 現在のルート（選択状態表示用）

    Returns:
        構築されたサイドバーContainer
    """
    # TODO: テーマモード取得を統合フェーズで実装
    # 理由: page.theme_mode の動的取得機能が未確定のため
    # 置換先: settings service から現在のテーマモードを取得
    is_dark_mode = False  # ダミー値

    sidebar_items: list[ft.Container | ft.Divider] = []

    # App title
    sidebar_items.append(
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PSYCHOLOGY, size=24),
                    ft.Text(
                        "Kage",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=SPACING.lg,
            margin=ft.margin.only(bottom=SPACING.md),
        )
    )

    # Divider
    sidebar_items.append(ft.Divider())

    # Navigation items
    for item in NAVIGATION_ITEMS:
        is_selected = current_route == item.route

        item_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        item.selected_icon if is_selected else item.icon,
                        size=20,
                        color=get_light_color("primary") if is_selected else None,
                    ),
                    ft.Text(
                        item.label,
                        size=14,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        color=get_light_color("primary") if is_selected else None,
                    ),
                ],
                spacing=SPACING.sm,
            ),
            padding=ft.padding.symmetric(horizontal=SPACING.md, vertical=SPACING.sm),
            margin=ft.margin.symmetric(horizontal=SPACING.xs),
            bgcolor=get_light_color("surface") if is_selected else None,
            border_radius=8,
            on_click=lambda _e, route=item.route: _handle_navigation(page, route),
            ink=True,
        )
        sidebar_items.append(item_container)

    return ft.Container(
        content=ft.Column(
            [
                # タイトルと上部ナビゲーション項目
                ft.Column(
                    sidebar_items[0:2],
                    spacing=SPACING.xs,
                    alignment=ft.MainAxisAlignment.START,
                ),
                # 中間のスペーサー
                ft.Column(
                    sidebar_items[2:-1],
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE,
                ),
                # 下部ナビゲーション項目
                ft.Column(
                    sidebar_items[-1:],
                    spacing=SPACING.xs,
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            expand=True,
        ),
        width=200,
        height=None,
        bgcolor=get_light_color("surface") if not is_dark_mode else get_dark_color("surface"),
        padding=SPACING.sm,
        border=ft.border.only(
            right=ft.border.BorderSide(
                width=1,
                color=get_light_color("primary_variant"),
            )
        ),
    )


def _handle_navigation(page: ft.Page, route: str) -> None:
    """ナビゲーション項目クリック時の処理。

    Args:
        page: Fletページオブジェクト
        route: 移動先ルート
    """
    if page.route != route:
        page.go(route)


# TODO: サブメニュー対応を統合フェーズで追加
# 理由: メモ関連画面（/memos/inbox, /memos/processing, /memos/history）等の
#       階層ナビゲーションが現在未対応のため
# 置換先: 展開可能なサブメニューUI（ExpansionTile等）を使用

# TODO: ナビゲーション状態の永続化機能を統合フェーズで追加
# 理由: 選択状態の保持機能が未実装のため
# 置換先: local_storage または shared_preferences を使用した状態保存
