"""アプリケーション全体のレイアウト管理。

このモジュールは、Fletアプリケーションの全体レイアウト（サイドバー + コンテンツ領域）を管理し、
ルーティングに基づいて適切なViewを表示する機能を提供します。
AppBarは使用せず、サイドバーベースの設計となっています。
"""

from __future__ import annotations

import flet as ft

from views_new.home import HomeView
from views_new.projects import ProjectsView
from views_new.shared.sidebar import build_sidebar


def build_layout(page: ft.Page, route: str) -> ft.View:
    """指定されたルートに対応するレイアウトとViewを構築する。

    Args:
        page: Fletのページオブジェクト
        route: 現在のルート文字列

    Returns:
        構築されたFletビュー

    Notes:
        AppBarは使用せず、サイドバーとコンテンツ領域のみで構成される。
        ルートとViewの対応は今後各画面実装時に追加される。
    """
    # Route to view mapping
    content = _get_view_content(page, route)

    # Build sidebar with current route
    sidebar = build_sidebar(page, route)

    return ft.View(
        route=route,
        controls=[
            ft.Row(
                [
                    # Sidebar
                    sidebar,
                    # Main content area
                    ft.Container(
                        content=content,
                        expand=True,
                        padding=16,
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )


def _get_view_content(page: ft.Page, route: str) -> ft.Control:
    """ルートに基づいて適切なViewコンテンツを取得する。

    Args:
        page: Fletページオブジェクト
        route: 現在のルート文字列

    Returns:
        対応するViewコンテンツ
    """
    # Route to view mapping
    if route == "/":
        # Home view is fully implemented
        return HomeView(page)

    if route == "/projects":
        # Projects view is now implemented
        return ProjectsView(page)

    # Other views are still placeholders
    # TODO: 各View実装完了後に対応するViewクラスを追加
    # 理由: ProjectsView、TagsView等が未実装のため
    # 置換先: 各Viewモジュールからインポートして使用
    return _create_placeholder_content(route)


def _create_placeholder_content(route: str) -> ft.Control:
    """ルートに基づいてプレースホルダーコンテンツを作成する。

    Args:
        route: 現在のルート文字列

    Returns:
        プレースホルダーコンテンツ
    """
    route_titles = {
        "/": "ホーム",
        "/projects": "プロジェクト",
        "/tags": "タグ",
        "/tasks": "タスク",
        "/memos": "メモ",
        "/memos/inbox": "受信箱メモ",
        "/memos/processing": "処理中メモ",
        "/memos/history": "メモ履歴",
        "/terms": "用語集",
        "/weekly-review": "週間レビュー",
        "/settings": "設定",
    }

    title = route_titles.get(route, "未知のページ")

    return ft.Column(
        [
            ft.Text(
                title,
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),
            ft.Text(
                f"ルート: {route}",
                size=14,
                color=ft.colors.ON_SURFACE_VARIANT,
            ),
            ft.Text(
                "TODO: 実際のViewコンテンツで置換予定",
                size=12,
                italic=True,
                color=ft.colors.ON_SURFACE_VARIANT,
            ),
        ],
        spacing=8,
    )


# Route to view mapping (populated after view implementations)
# TODO: 各View実装完了後に以下の形式で設定
# ROUTE_TO_VIEW = {
#     "/": HomeView,
#     "/projects": ProjectsView,
#     "/tags": TagsView,
#     "/tasks": TasksView,
#     "/memos": MemosView,
#     "/memos/inbox": InboxMemosView,
#     "/memos/processing": ProcessingMemosView,
#     "/memos/history": MemoHistoryView,
#     "/terms": TermsView,
#     "/weekly-review": WeeklyReviewView,
#     "/settings": SettingsView,
# }
