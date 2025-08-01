"""GTDサイドバーコンポーネント

GTD（Getting Things Done）のワークフローに基づいたナビゲーションサイドバーを提供します。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from models.new_task import TaskStatus
from models.project import ProjectStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from logic.services.project_service import ProjectService
    from logic.services.task_service import TaskService


class GTDSidebar(ft.Column):
    """GTDサイドバーコンポーネント

    タスク管理のためのGTDベースナビゲーションを提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        task_service: TaskService,
        project_service: ProjectService,
        on_section_change: Callable[[str, dict | None], None],
    ) -> None:
        """GTDSidebarのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            task_service: タスクサービス
            project_service: プロジェクトサービス
            on_section_change: セクション変更時のコールバック
        """
        super().__init__()
        self._page = page
        self.task_service = task_service
        self.project_service = project_service
        self.on_section_change = on_section_change
        self.spacing = 10
        self.expand = True

        # 現在選択されているセクション
        self.selected_section = None

        # コンポーネントの構築
        self._build_sidebar()

    def _build_sidebar(self) -> None:
        """サイドバーのレイアウトを構築"""
        self.controls = [
            # QUICK-ACTION セクション
            self._build_quick_action_section(),
            ft.Divider(),
            # PROJECTS セクション
            self._build_projects_section(),
            ft.Divider(),
            # CLOSED セクション
            self._build_closed_section(),
            ft.Divider(),
            # INBOX セクション
            self._build_inbox_section(),
        ]

    def _build_quick_action_section(self) -> ft.Container:
        """QUICK-ACTION セクションを構築"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "QUICK-ACTION",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_600,
                    ),
                    self._create_action_button(
                        "📥 Inbox に追加",
                        "add_to_inbox",
                        ft.Colors.BLUE_600,
                    ),
                    self._create_action_button(
                        "☑️ 本日のタスクを追加",
                        "add_today_task",
                        ft.Colors.GREEN_600,
                    ),
                    self._create_action_button(
                        "⏳ 待ちタスクを追加",
                        "add_waiting_task",
                        ft.Colors.ORANGE_600,
                    ),
                    self._create_action_button(
                        "📔 日記を追加",
                        "add_diary",
                        ft.Colors.PURPLE_600,
                    ),
                ]
            ),
        )

    def _build_projects_section(self) -> ft.Container:
        """PROJECTS セクションを構築"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "PROJECTS",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_size=16,
                                on_click=self._add_new_project,
                                tooltip="新規プロジェクト",
                            ),
                        ]
                    ),
                    self._build_projects_list(),
                ]
            ),
        )

    def _build_projects_list(self) -> ft.Column:
        """アクティブプロジェクト一覧を構築"""
        projects_list = ft.Column(spacing=2)

        try:
            # アクティブなプロジェクトを取得
            active_projects = self.project_service.get_projects_by_status(ProjectStatus.ACTIVE)

            for project in active_projects:
                projects_list.controls.append(self._create_project_item(project.title, str(project.id)))

        except Exception:
            # エラー時は空のリストを表示
            projects_list.controls.append(ft.Text("プロジェクトの読み込みに失敗しました", size=10, color=ft.Colors.RED))

        return projects_list

    def _build_closed_section(self) -> ft.Container:
        """CLOSED セクション（ステータス別）を構築"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "CLOSED",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_600,
                    ),
                    self._create_status_item("📋 ToDo", TaskStatus.NEXT_ACTION, "0"),
                    self._create_status_item("🔄 InProgress", TaskStatus.DELEGATED, "0"),
                    self._create_status_item("✅ Done", TaskStatus.COMPLETED, "0"),
                ]
            ),
        )

    def _build_inbox_section(self) -> ft.Container:
        """INBOX セクションを構築"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "INBOX",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_600,
                    ),
                    self._create_status_item("📥 整理用", TaskStatus.INBOX, "0"),
                    self._create_status_item("🎯 次に取るべき行動", TaskStatus.NEXT_ACTION, "0"),
                ]
            ),
        )

    def _create_action_button(self, label: str, action: str, color: str) -> ft.Container:
        """クイックアクションボタンを作成"""
        return ft.Container(
            content=ft.Text(label, size=14, color=ft.Colors.WHITE),
            bgcolor=color,
            padding=10,
            border_radius=5,
            on_click=lambda _: self._handle_quick_action(action),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _create_project_item(self, name: str, project_id: str) -> ft.Container:
        """プロジェクト項目を作成"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER, size=16, color=ft.Colors.BLUE_600),
                    ft.Text(name, size=14, expand=True),
                    ft.Text("ロック中", size=10, color=ft.Colors.GREY_600),  # タスク数は後で実装
                ]
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4,
            on_click=lambda _: self._handle_project_select(project_id),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _create_status_item(self, label: str, status: TaskStatus, count: str) -> ft.Container:
        """ステータス項目を作成"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(label, size=14, expand=True),
                    ft.Text(count, size=12, color=ft.Colors.GREY_600),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4,
            on_click=lambda _: self._handle_status_select(status),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _handle_quick_action(self, action: str) -> None:
        """クイックアクション処理"""
        self.on_section_change("quick_action", {"action": action})

    def _handle_project_select(self, project_id: str) -> None:
        """プロジェクト選択処理"""
        self.selected_section = f"project_{project_id}"
        self.on_section_change("project", {"project_id": project_id})

    def _handle_status_select(self, status: TaskStatus) -> None:
        """ステータス選択処理"""
        self.selected_section = f"status_{status.value}"
        self.on_section_change("status", {"status": status})

    def _add_new_project(self, _: ft.ControlEvent) -> None:
        """新規プロジェクト追加"""
        # [AI GENERATED] プロジェクト作成ダイアログの実装は後の段階で行う
        return

    def refresh(self) -> None:
        """サイドバーの内容を再読み込み"""
        # プロジェクトリストを更新
        self._build_sidebar()
        self.update()
