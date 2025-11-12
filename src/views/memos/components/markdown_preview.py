"""Markdown preview helpers for memo views.

簡易的なMarkdownをFletコントロールに変換する関数群。
将来的に正式なMarkdownレンダラーへ差し替えることを想定し、
依存箇所をこのモジュールに集約する。
"""

from __future__ import annotations

import re

import flet as ft


def render_markdown_preview(markdown: str) -> list[ft.Control]:
    """最小限のMarkdownプレビューを生成する。

    対応: 見出し(#, ##, ###), 箇条書き(-, *), 太字(**text**/__text__), 斜体(*text*/_text_),
    インラインコード(`code`)

    Args:
        markdown: 入力文字列

    Returns:
        生成されたコントロール群
    """
    if not markdown.strip():
        return [ft.Text("プレビューはこちらに表示されます", color=ft.Colors.ON_SURFACE_VARIANT, italic=True)]

    lines = markdown.splitlines()
    controls: list[ft.Control] = []
    for line in lines:
        if line.startswith("### "):
            controls.append(ft.Text(line[4:], style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD))
            continue
        if line.startswith("## "):
            controls.append(ft.Text(line[3:], style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD))
            continue
        if line.startswith("# "):
            controls.append(ft.Text(line[2:], style=ft.TextThemeStyle.HEADLINE_SMALL, weight=ft.FontWeight.BOLD))
            continue

        if line.startswith(("- ", "* ")):
            controls.append(ft.Text("• " + line[2:], style=ft.TextThemeStyle.BODY_MEDIUM))
            continue

        # 太字/斜体/インラインコード（簡易置換）
        html_like = line
        html_like = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), html_like)
        html_like = re.sub(
            r"(?<!\*)\*([^*]+?)\*(?!\*)|(?<!_)_([^_]+?)_(?!_)",
            lambda m: m.group(1) or m.group(2),
            html_like,
        )
        html_like = re.sub(r"`(.+?)`", lambda m: m.group(1), html_like)

        if not html_like.strip():
            controls.append(ft.Container(height=8))  # 空行
        else:
            controls.append(ft.Text(html_like, style=ft.TextThemeStyle.BODY_MEDIUM))

    return controls
