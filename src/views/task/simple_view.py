"""シンプルなテスト用タスクビュー

基本的な動作確認のためのシンプルなビューです。
"""

from __future__ import annotations

import flet as ft


class SimpleTaskView(ft.Column):
    """シンプルなタスクビューのテスト版"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self._page = page
        self.spacing = 10
        self.expand = True

        # シンプルなレイアウト
        self.controls = [
            ft.Text("タスク管理", size=24, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    # 左サイドバー
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("QUICK-ACTION", size=14, weight=ft.FontWeight.BOLD),
                                ft.TextButton("📥 Inbox に追加"),
                                ft.TextButton("📋 次のアクション"),
                                ft.TextButton("📅 いつかやる"),
                                ft.Container(height=20),
                                ft.Text("PROJECTS", size=14, weight=ft.FontWeight.BOLD),
                                ft.Text("📁 開発中... ", size=12, color=ft.Colors.GREY_600),
                                ft.Container(height=20),
                                ft.Text("TASKS", size=14, weight=ft.FontWeight.BOLD),
                                ft.Text("📋 ToDo", size=12),
                                ft.Text("🔄 InProgress", size=12),
                                ft.Text("✅ Done", size=12),
                                ft.Text("📥 Inbox", size=12),
                            ],
                            spacing=8,
                        ),
                        width=200,
                        bgcolor=ft.Colors.GREY_100,
                        padding=16,
                        border_radius=8,
                    ),
                    # メインエリア
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("メインタスクエリア", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text("ここにタスクボードが表示されます", size=14),
                                ft.Container(
                                    content=ft.Text("タスクリストのプレースホルダー"),
                                    height=300,
                                    bgcolor=ft.Colors.WHITE,
                                    border_radius=8,
                                    alignment=ft.alignment.center,
                                ),
                            ]
                        ),
                        expand=True,
                        padding=16,
                    ),
                ],
                expand=True,
            ),
        ]


def create_simple_task_view(page: ft.Page) -> ft.Container:
    """シンプルなタスクビューを作成"""
    return ft.Container(content=SimpleTaskView(page=page))
