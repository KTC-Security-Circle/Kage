"""GTDプロジェクトリストコンポーネント

プロジェクト一覧の表示と管理機能を提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models.project import ProjectStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.project_service import ProjectService


class GTDProjectList(ft.Container):
    """GTDプロジェクトリストコンポーネント

    アクティブなプロジェクトの一覧表示と管理機能を提供します。
    """

    def __init__(
        self,
        project_service: ProjectService,
        on_project_click: Callable[[str], None],
        on_add_project_click: Callable[[], None],
    ) -> None:
        """GTDProjectListのコンストラクタ

        Args:
            project_service: プロジェクトサービス
            on_project_click: プロジェクトクリック時のコールバック
            on_add_project_click: プロジェクト追加クリック時のコールバック
        """
        super().__init__()
        self.project_service = project_service
        self.on_project_click = on_project_click
        self.on_add_project_click = on_add_project_click

        # スタイル設定
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 12
        self.padding = 16
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        )

        # プロジェクトリスト
        self.projects_list = ft.Column(spacing=4)

        # コンテンツの構築
        self._build_content()
        self._load_projects()

    def _build_content(self) -> None:
        """コンテンツを構築"""
        self.content = ft.Column(
            [
                # セクションヘッダー
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.FOLDER,
                            color=ft.Colors.BLUE_600,
                            size=20,
                        ),
                        ft.Text(
                            "PROJECTS",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=16,
                            icon_color=ft.Colors.BLUE_600,
                            tooltip="新規プロジェクト",
                            on_click=lambda _: self._handle_add_project(),
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=8, color=ft.Colors.GREY_300),
                # プロジェクトリスト
                self.projects_list,
            ],
            spacing=8,
        )

    def _load_projects(self) -> None:
        """プロジェクトを読み込み"""
        try:
            # アクティブなプロジェクトを取得
            active_projects = self.project_service.get_projects_by_status(ProjectStatus.ACTIVE)

            self.projects_list.controls.clear()

            if not active_projects:
                self.projects_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "プロジェクトがありません",
                            size=12,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    )
                )
            else:
                for project in active_projects:
                    self.projects_list.controls.append(self._create_project_item(project.title, str(project.id)))

        except Exception as e:
            logger.error(f"プロジェクト読み込みエラー: {e}")
            self.projects_list.controls.clear()
            self.projects_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "プロジェクトの読み込みに失敗しました",
                        size=10,
                        color=ft.Colors.RED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                )
            )

    def _create_project_item(self, name: str, project_id: str) -> ft.Container:
        """プロジェクト項目を作成"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.FOLDER,
                        size=16,
                        color=ft.Colors.BLUE_600,
                    ),
                    ft.Text(
                        name,
                        size=14,
                        color=ft.Colors.GREY_800,
                        expand=True,
                    ),
                    ft.Text(
                        "0",  # タスク数は後で実装
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_FORWARD_IOS,
                        color=ft.Colors.GREY_400,
                        size=12,
                    ),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.GREY_200),
            on_click=lambda _, pid=project_id: self._handle_project_click(pid),
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _handle_project_click(self, project_id: str) -> None:
        """プロジェクトクリック処理"""
        logger.info(f"プロジェクト選択: {project_id}")
        self.on_project_click(project_id)

    def _handle_add_project(self) -> None:
        """プロジェクト追加処理"""
        logger.info("プロジェクト追加ボタンがクリックされました")
        self.on_add_project_click()

    def refresh(self) -> None:
        """プロジェクトリストを再読み込み"""
        self._load_projects()
        if self.page:
            self.update()
