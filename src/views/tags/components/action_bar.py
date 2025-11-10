"""アクションバーコンポーネント

タグ管理画面のアクションバーUIコンポーネント。
新規作成ボタン、検索フィールド、フィルターボタンを含む。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft


def create_action_bar(
    on_create: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_search: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_color_filter: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
    on_refresh: Callable[[ft.ControlEvent], None],  # type: ignore[name-defined]
) -> ft.Control:  # type: ignore[name-defined]
    """アクションバーを構築する。

    Args:
        on_create: 新規作成ボタンクリック時のコールバック
        on_search: 検索フィールド変更時のコールバック
        on_color_filter: 色フィルターボタンクリック時のコールバック
        on_refresh: 更新ボタンクリック時のコールバック

    Returns:
        アクションバーコンポーネント
    """
    import flet as ft

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="新規タグ",
                    icon=ft.Icons.ADD,
                    on_click=on_create,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(expand=True),  # Spacer
                ft.TextField(
                    hint_text="タグを検索...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=300,
                    on_change=on_search,
                ),
                ft.IconButton(
                    icon=ft.Icons.PALETTE,
                    tooltip="カラーパレット表示切替",
                    on_click=on_color_filter,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="更新",
                    on_click=on_refresh,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(bottom=16),
    )
