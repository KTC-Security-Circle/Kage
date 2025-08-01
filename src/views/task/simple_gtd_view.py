"""シンプルなテスト用GTDビュー

基本的な動作確認のためのシンプルなビューです。
"""

from __future__ import annotations

import flet as ft


class SimpleGTDView(ft.Column):
    """シンプルなGTDビューのテスト版"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self._page = page
        self.spacing = 10
        self.expand = True

        # シンプルなレイアウト
        self.controls = [
            ft.Text("GTDタスク管理", size=24, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    # 左サイドバー
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("QUICK-ACTION", size=14, weight=ft.FontWeight.BOLD),
                                ft.TextButton("📥 Inbox に追加"),
                                ft.TextButton("☑️ 本日のタスクを追加"),
                                ft.Divider(),
                                ft.Text("PROJECTS", size=14, weight=ft.FontWeight.BOLD),
                                ft.Text("（プロジェクト一覧）"),
                                ft.Divider(),
                                ft.Text("CLOSED", size=14, weight=ft.FontWeight.BOLD),
                                ft.TextButton("📋 ToDo"),
                                ft.TextButton("🔄 InProgress"),
                                ft.TextButton("✅ Done"),
                                ft.Divider(),
                                ft.Text("INBOX", size=14, weight=ft.FontWeight.BOLD),
                                ft.TextButton("📥 整理用"),
                            ]
                        ),
                        width=250,
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                    ),
                    # メインコンテンツ
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("タスク一覧", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text("ここにタスク一覧が表示されます"),
                                ft.ElevatedButton("新しいタスク", icon=ft.Icons.ADD),
                            ]
                        ),
                        expand=True,
                        padding=20,
                    ),
                ],
                expand=True,
            ),
        ]


def create_simple_gtd_view(page: ft.Page) -> ft.Container:
    """シンプルなGTDビューを作成"""
    return ft.Container(content=SimpleGTDView(page=page))
