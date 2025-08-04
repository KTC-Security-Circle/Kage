"""プロジェクトリストコンポーネント

プロジェクト一覧の表示と管理機能を提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.project_service import ProjectService


class ProjectList(ft.Container):
    """プロジェクトリストコンポーネント

    アクティブなプロジェクトの一覧表示と管理機能を提供します。
    """

    def __init__(
        self,
        project_service: ProjectService,
        on_project_select: Callable[[int | None], None] | None = None,
    ) -> None:
        """ProjectListのコンストラクタ

        Args:
            project_service: プロジェクトサービス
            on_project_select: プロジェクト選択時のコールバック
        """
        super().__init__()
        self.project_service = project_service
        self.on_project_select = on_project_select

        # スタイル設定
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 12
        self.padding = 16
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        )

        # プロジェクトデータ
        self.projects = []
        self.selected_project_id: int | None = None

        # コンテンツの構築
        self._load_projects()
        self._build_content()

    def _load_projects(self) -> None:
        """プロジェクトデータを読み込み"""
        try:
            self.projects = self.project_service.get_active_projects()
            logger.info(f"プロジェクト読み込み完了: {len(self.projects)}件")
        except Exception as e:
            logger.error(f"プロジェクト読み込みエラー: {e}")
            self.projects = []

    def _build_content(self) -> None:
        """コンテンツを構築"""
        logger.info("ProjectList コンテンツ構築開始")

        self.content = ft.Column(
            [
                # ヘッダー
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.FOLDER_OUTLINED,
                            color=ft.Colors.GREEN_600,
                            size=20,
                        ),
                        ft.Text(
                            "プロジェクト",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=16,
                            tooltip="新規プロジェクト",
                            on_click=self._handle_add_project,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),  # スペーサー
                # プロジェクトリスト
                ft.Column(
                    [self._create_project_item(project) for project in self.projects]
                    if self.projects
                    else [self._create_empty_state()],
                    spacing=4,
                ),
            ],
            spacing=0,
        )

    def _create_project_item(self, project: object) -> ft.Container:
        """プロジェクトアイテムを作成

        Args:
            project: プロジェクトデータ

        Returns:
            プロジェクトアイテムのコンテナ
        """
        is_selected = self.selected_project_id == project.id  # type: ignore[attr-defined]

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.RADIO_BUTTON_CHECKED if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        size=16,
                        color=ft.Colors.GREEN_600 if is_selected else ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        project.name,  # type: ignore[attr-defined]
                        size=14,
                        color=ft.Colors.GREY_800 if is_selected else ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL,
                        expand=True,
                    ),
                    ft.Text(
                        str(getattr(project, "task_count", 0)),
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.GREEN_50 if is_selected else ft.Colors.TRANSPARENT,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            on_click=lambda _, p=project: self._handle_project_select(p.id),  # type: ignore[attr-defined]
            ink=True,
        )

    def _create_empty_state(self) -> ft.Container:
        """空状態の表示"""
        return ft.Container(
            content=ft.Text(
                "プロジェクトがありません",
                size=12,
                color=ft.Colors.GREY_500,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=16,
        )

    def _handle_project_select(self, project_id: int) -> None:
        """プロジェクト選択処理

        Args:
            project_id: 選択されたプロジェクトID
        """
        self.selected_project_id = project_id if self.selected_project_id != project_id else None

        if self.on_project_select:
            self.on_project_select(self.selected_project_id)

        # UI更新
        self._build_content()
        self.update()

    def _handle_add_project(self, _: ft.ControlEvent) -> None:
        """プロジェクト追加処理"""
        logger.info("新規プロジェクト追加要求")
        # 将来: プロジェクト追加ダイアログを表示

    def refresh(self) -> None:
        """プロジェクトリストを再読み込み"""
        self._load_projects()
        self._build_content()
        if hasattr(self, "update"):
            self.update()
