"""プロジェクト管理画面

プロジェクトの一覧表示、作成、編集、削除機能を提供するメインビュー。
BaseViewパターンを採用し、一貫したUIと機能を提供する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from src.views_new.shared.base_view import BaseView


class ProjectsView(BaseView):
    """プロジェクト管理画面のメインビュー。

    プロジェクトの一覧表示、CRUD操作、検索・フィルタ機能を提供。
    BaseViewを継承し、エラーハンドリングとローディング機能を活用。
    """

    def __init__(self, page: ft.Page) -> None:  # type: ignore[name-defined]
        """ProjectsViewを初期化する。

        Args:
            page: Fletページインスタンス
        """
        super().__init__(page)
        self.projects_data: list[dict[str, str]] = []  # TODO: 実際のデータバインディング

    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト画面のコンテンツを構築する。

        Returns:
            プロジェクト画面のメインコンテンツ
        """
        import flet as ft

        # Mock data for development
        self.projects_data = [
            {
                "id": "1",
                "name": "ウェブサイトリニューアル",
                "description": "会社ウェブサイトの全面リニューアルプロジェクト",
                "status": "進行中",
                "tasks_count": "12",
                "created_at": "2024-01-15",
            },
            {
                "id": "2",
                "name": "モバイルアプリ開発",
                "description": "iOS/Android向けの新しいモバイルアプリケーション",
                "status": "計画中",
                "tasks_count": "8",
                "created_at": "2024-02-01",
            },
            {
                "id": "3",
                "name": "データベース最適化",
                "description": "既存システムのパフォーマンス改善",
                "status": "完了",
                "tasks_count": "5",
                "created_at": "2024-01-01",
            },
        ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._build_header(),
                    self._build_action_bar(),
                    self._build_projects_list(),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def _build_header(self) -> ft.Control:  # type: ignore[name-defined]
        """ページヘッダーを構築する。

        Returns:
            ヘッダーコンテンツ
        """
        import flet as ft

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "プロジェクト管理",
                                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                weight=ft.FontWeight.BOLD,
                                color=self.theme.colors.on_surface,
                            ),
                            ft.Text(
                                f"合計 {len(self.projects_data)} 件のプロジェクト",
                                style=ft.TextThemeStyle.BODY_MEDIUM,
                                color=self.theme.colors.on_surface_variant,
                            ),
                        ],
                        spacing=self.theme.spacing.small,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=self.theme.spacing.medium),
        )

    def _build_action_bar(self) -> ft.Control:  # type: ignore[name-defined]
        """アクションバーを構築する。

        Returns:
            アクションバーコンテンツ
        """
        import flet as ft

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text="新規プロジェクト",
                        icon=ft.icons.ADD,
                        on_click=self._handle_create_project,
                        style=ft.ButtonStyle(
                            bgcolor=self.theme.colors.primary,
                            color=self.theme.colors.on_primary,
                        ),
                    ),
                    ft.Container(expand=True),  # Spacer
                    ft.TextField(
                        hint_text="プロジェクトを検索...",
                        prefix_icon=ft.icons.SEARCH,
                        width=300,
                        on_change=self._handle_search,
                        border_color=self.theme.colors.outline,
                        focused_border_color=self.theme.colors.primary,
                    ),
                    ft.IconButton(
                        icon=ft.icons.FILTER_LIST,
                        tooltip="フィルター",
                        on_click=self._handle_filter,
                        icon_color=self.theme.colors.on_surface_variant,
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        tooltip="更新",
                        on_click=self._handle_refresh,
                        icon_color=self.theme.colors.on_surface_variant,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=self.theme.spacing.medium),
        )

    def _build_projects_list(self) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト一覧を構築する。

        Returns:
            プロジェクト一覧コンテンツ
        """
        import flet as ft

        if not self.projects_data:
            return self._build_empty_state()

        projects_cards = [self._create_project_card(project) for project in self.projects_data]

        return ft.Container(
            content=ft.Column(
                controls=projects_cards,
                spacing=self.theme.spacing.medium,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )

    def _build_empty_state(self) -> ft.Control:  # type: ignore[name-defined]
        """空の状態を構築する。

        Returns:
            空の状態コンテンツ
        """
        import flet as ft

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.icons.FOLDER_OPEN_OUTLINED,
                        size=64,
                        color=self.theme.colors.on_surface_variant,
                    ),
                    ft.Text(
                        "プロジェクトがありません",
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color=self.theme.colors.on_surface_variant,
                    ),
                    ft.Text(
                        "新規プロジェクトを作成してタスクを整理しましょう",
                        style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=self.theme.colors.on_surface_variant,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=self.theme.spacing.large),
                    ft.ElevatedButton(
                        text="最初のプロジェクトを作成",
                        icon=ft.icons.ADD,
                        on_click=self._handle_create_project,
                        style=ft.ButtonStyle(
                            bgcolor=self.theme.colors.primary,
                            color=self.theme.colors.on_primary,
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=self.theme.spacing.medium,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def _create_project_card(self, project: dict[str, str]) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクトカードを作成する。

        Args:
            project: プロジェクトデータ

        Returns:
            プロジェクトカード
        """
        import flet as ft

        # Status color mapping
        status_colors = {
            "進行中": self.theme.colors.primary,
            "計画中": self.theme.colors.secondary,
            "完了": ft.colors.GREEN,
            "保留": ft.colors.ORANGE,
        }

        status_color = status_colors.get(project["status"], self.theme.colors.outline)

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            project["name"],
                                            style=ft.TextThemeStyle.TITLE_MEDIUM,
                                            weight=ft.FontWeight.W500,
                                            color=self.theme.colors.on_surface,
                                        ),
                                        ft.Text(
                                            project["description"],
                                            style=ft.TextThemeStyle.BODY_MEDIUM,
                                            color=self.theme.colors.on_surface_variant,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=self.theme.spacing.small,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        project["status"],
                                        style=ft.TextThemeStyle.LABEL_SMALL,
                                        color=ft.colors.WHITE,
                                        weight=ft.FontWeight.W500,
                                    ),
                                    bgcolor=status_color,
                                    padding=ft.padding.symmetric(
                                        horizontal=self.theme.spacing.small,
                                        vertical=self.theme.spacing.tiny,
                                    ),
                                    border_radius=ft.border_radius.all(12),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Divider(
                            height=1,
                            color=self.theme.colors.outline_variant,
                        ),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.icons.TASK_ALT,
                                            size=16,
                                            color=self.theme.colors.on_surface_variant,
                                        ),
                                        ft.Text(
                                            f"{project['tasks_count']} タスク",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=self.theme.colors.on_surface_variant,
                                        ),
                                    ],
                                    spacing=self.theme.spacing.tiny,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.icons.CALENDAR_TODAY,
                                            size=16,
                                            color=self.theme.colors.on_surface_variant,
                                        ),
                                        ft.Text(
                                            project["created_at"],
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=self.theme.colors.on_surface_variant,
                                        ),
                                    ],
                                    spacing=self.theme.spacing.tiny,
                                ),
                                ft.Container(expand=True),  # Spacer
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT_OUTLINED,
                                            tooltip="編集",
                                            icon_size=20,
                                            on_click=lambda e, p=project: self._handle_edit_project(e, p),
                                            icon_color=self.theme.colors.on_surface_variant,
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINE,
                                            tooltip="削除",
                                            icon_size=20,
                                            on_click=lambda e, p=project: self._handle_delete_project(e, p),
                                            icon_color=ft.colors.ERROR,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=self.theme.spacing.medium,
                ),
                padding=self.theme.spacing.large,
            ),
            elevation=2,
        )

    def _handle_create_project(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規プロジェクト作成を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: プロジェクト作成ダイアログを表示
        self.show_info_snackbar("新規プロジェクト作成機能は準備中です")

    def _handle_edit_project(self, _: ft.ControlEvent, project: dict[str, str]) -> None:  # type: ignore[name-defined]
        """プロジェクト編集を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            project: 編集対象のプロジェクト
        """
        # TODO: プロジェクト編集ダイアログを表示
        self.show_info_snackbar(f"プロジェクト「{project['name']}」の編集機能は準備中です")

    def _handle_delete_project(self, _: ft.ControlEvent, project: dict[str, str]) -> None:  # type: ignore[name-defined]
        """プロジェクト削除を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            project: 削除対象のプロジェクト
        """
        # TODO: 削除確認ダイアログを表示
        self.show_info_snackbar(f"プロジェクト「{project['name']}」の削除機能は準備中です")

    def _handle_search(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索を処理する。

        Args:
            e: イベントオブジェクト
        """
        # TODO: 検索機能を実装
        search_text = e.control.value if e.control.value else ""  # type: ignore[attr-defined]
        if search_text:
            self.show_info_snackbar(f"「{search_text}」の検索機能は準備中です")

    def _handle_filter(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """フィルターを処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: フィルターダイアログを表示
        self.show_info_snackbar("フィルター機能は準備中です")

    def _handle_refresh(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """データ更新を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        # TODO: 実際のデータ再読み込み
        self.show_success_snackbar("プロジェクトデータを更新しました")
        self.page.update()
