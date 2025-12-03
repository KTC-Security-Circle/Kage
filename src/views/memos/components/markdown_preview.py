"""Markdown preview helpers for memo views.

Flet標準のMarkdownコントロールを使用したプレビュー生成。
"""

from __future__ import annotations

import flet as ft


def render_markdown_preview(markdown: str) -> ft.Control:
    """Markdownプレビューを生成する。

    Flet標準の`ft.Markdown`コントロールを使用してMarkdown文字列を
    レンダリングする。GitHub Web拡張セットを有効化し、テーブル、
    打ち消し線、タスクリストなどをサポート。

    Args:
        markdown: 入力Markdown文字列

    Returns:
        レンダリングされたMarkdownコントロール
    """
    if not markdown.strip():
        return ft.Text(
            "プレビューはこちらに表示されます",
            color=ft.Colors.ON_SURFACE_VARIANT,
            italic=True,
        )

    return ft.Markdown(
        value=markdown,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        on_tap_link=lambda _: None,  # リンククリックは無効化(必要に応じて page.launch_url(e.data) に変更可能)
    )
