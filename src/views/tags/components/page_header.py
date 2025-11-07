"""タグ管理ページヘッダーコンポーネント

タグ管理画面専用のページヘッダーUIコンポーネント。
共通コンポーネントのラッパー。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from views.shared.components import create_page_header as create_shared_header


def create_page_header(item_count: int) -> ft.Control:  # type: ignore[name-defined]
    """タグ管理ページヘッダーを構築する。

    Args:
        item_count: 表示するタグ数

    Returns:
        ヘッダーコンポーネント
    """
    return create_shared_header(
        title="タグ管理",
        subtitle=f"合計 {item_count} 件のタグ",
    )
