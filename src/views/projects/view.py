"""プロジェクト画面のView層

MVP パターンの View として、Flet UI の描画とイベント配線の最小限実装。
ロジックは Controller に委譲し、表示に集中する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

    from .presenter import ProjectCardVM, ProjectDetailVM

from views.shared.base_view import BaseView

from .controller import ProjectController
from .query import InMemoryProjectQuery


class ProjectsView(BaseView):
    """プロジェクト画面のメインView。

    MVP パターンに従い、描画とイベント配線のみを担当。
    ビジネスロジックは Controller に委譲し、UI に集中する。

    Attributes:
        _controller: プロジェクトコントローラー
        _list_container: プロジェクトリストコンテナ
        _detail_container: プロジェクト詳細コンテナ
    """

    def __init__(self, page: ft.Page) -> None:  # type: ignore[name-defined]
        """ProjectsView を初期化する。

        Args:
            page: Fletページインスタンス
        """
        super().__init__(page)

        # サンプルデータで初期化（後でRepository連携に置き換え）
        sample_data = self._get_sample_data()
        query = InMemoryProjectQuery(sample_data)

        # コントローラー初期化
        self._controller = ProjectController(
            query=query,
            on_list_change=self._render_list,
            on_detail_change=self._render_detail,
        )

        # UI コンテナ
        self._list_container: ft.Column | None = None  # type: ignore[name-defined]
        self._detail_container: ft.Container | None = None  # type: ignore[name-defined]

    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト画面のコンテンツを構築する。

        Returns:
            プロジェクト画面のメインコンテンツ
        """
        import flet as ft

        # コンテナ初期化
        self._list_container = ft.Column(expand=True, spacing=8)
        self._detail_container = ft.Container(expand=True)

        # 初期描画
        self._controller.refresh()

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._build_header(),
                    ft.Container(
                        content=self._build_main_content(),
                        expand=True,
                        padding=ft.padding.only(top=24),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def _build_header(self) -> ft.Control:  # type: ignore[name-defined]
        """ヘッダー部分を構築する。

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
                                "プロジェクト",
                                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "複数のタスクをまとめたプロジェクト管理",
                                style=ft.TextThemeStyle.BODY_MEDIUM,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        spacing=4,
                    ),
                    self._build_header_actions(),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=24),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
        )

    def _build_header_actions(self) -> ft.Control:  # type: ignore[name-defined]
        """ヘッダーアクション部分を構築する。

        Returns:
            ヘッダーアクションコンテンツ
        """
        import flet as ft

        return ft.Row(
            controls=[
                # 検索バー
                ft.TextField(
                    hint_text="プロジェクトを検索...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=256,
                    on_change=self._on_search_change,
                    border_color=ft.Colors.GREY_400,
                    focused_border_color=ft.Colors.BLUE,
                ),
                # ステータスフィルタ
                ft.Dropdown(
                    label="ステータス",
                    width=150,
                    options=[
                        ft.dropdown.Option("", "全て"),
                        ft.dropdown.Option("進行中", "進行中"),
                        ft.dropdown.Option("完了", "完了"),
                        ft.dropdown.Option("保留", "保留"),
                        ft.dropdown.Option("キャンセル", "キャンセル"),
                    ],
                    value="",
                    on_change=self._on_status_change,
                ),
                # 並び替え
                ft.Dropdown(
                    label="並び替え",
                    width=120,
                    options=[
                        ft.dropdown.Option("updated_at", "更新日"),
                        ft.dropdown.Option("created_at", "作成日"),
                        ft.dropdown.Option("title", "タイトル"),
                        ft.dropdown.Option("due_date", "期限"),
                    ],
                    value="updated_at",
                    on_change=self._on_sort_change,
                ),
                # 並び順切替
                ft.IconButton(
                    icon=ft.Icons.ARROW_DOWNWARD,
                    tooltip="並び順切替",
                    on_click=self._on_sort_toggle,
                ),
                # 新規作成
                ft.ElevatedButton(
                    text="新規プロジェクト",
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_click,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=12,
        )

    def _build_main_content(self) -> ft.Control:  # type: ignore[name-defined]
        """メインコンテンツ部分を構築する。

        Returns:
            メインコンテンツ
        """
        import flet as ft

        controls = []
        if self._list_container:
            controls.append(
                ft.Container(
                    content=self._list_container,
                    width=480,
                    expand=False,
                )
            )
        if self._detail_container:
            controls.append(self._detail_container)

        return ft.Row(
            controls=controls,
            spacing=24,
            expand=True,
        )

    def _render_list(self, projects: list[ProjectCardVM]) -> None:
        """プロジェクトリストを描画する。

        Args:
            projects: 表示するプロジェクトのViewModelリスト
        """
        if not self._list_container:
            return

        if not projects:
            # 空の状態
            self._list_container.controls = [self._build_empty_state()]
        else:
            # プロジェクトカード
            cards = [self._build_project_card(project) for project in projects]
            self._list_container.controls = cards

        self._list_container.update()

    def _render_detail(self, project: ProjectDetailVM | None) -> None:
        """プロジェクト詳細を描画する。

        Args:
            project: 表示するプロジェクトの詳細ViewModel（None の場合は空表示）
        """
        if not self._detail_container:
            return

        if project is None:
            # 未選択状態
            self._detail_container.content = self._build_no_selection()
        else:
            # 詳細表示
            self._detail_container.content = self._build_project_detail(project)

        self._detail_container.update()

    def _build_project_card(self, project: ProjectCardVM) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクトカードを構築する。

        Args:
            project: プロジェクトViewModel

        Returns:
            プロジェクトカード
        """
        import flet as ft

        is_selected = self._controller.state.selected_id == project.id

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    project.title,
                                    style=ft.TextThemeStyle.TITLE_SMALL,
                                    weight=ft.FontWeight.W_500,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        project.status,
                                        style=ft.TextThemeStyle.LABEL_SMALL,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    bgcolor=project.status_color,
                                    border_radius=12,
                                ),
                            ],
                        ),
                        ft.Text(
                            project.subtitle,
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            project.description,
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=ft.Colors.GREY_700,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            project.progress_text,
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                ),
                                ft.ProgressBar(
                                    value=project.progress_value,
                                    color=ft.Colors.BLUE,
                                    bgcolor=ft.Colors.GREY_300,
                                    height=6,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=8,
                ),
                padding=16,
                ink=True,
                on_click=lambda _: self._controller.select_project(project.id),
            ),
            elevation=1 if not is_selected else 3,
            color=ft.Colors.WHITE if not is_selected else ft.Colors.BLUE_50,
            surface_tint_color=ft.Colors.BLUE if is_selected else None,
        )

    def _build_project_detail(self, project: ProjectDetailVM) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト詳細を構築する。

        Args:
            project: プロジェクト詳細ViewModel

        Returns:
            プロジェクト詳細コンテンツ
        """
        import flet as ft

        return ft.Column(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                # ヘッダー
                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    project.title,
                                                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    f"{project.created_at} 作成",
                                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=4,
                                            expand=True,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                project.status,
                                                style=ft.TextThemeStyle.LABEL_MEDIUM,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            bgcolor=project.status_color,
                                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                            border_radius=16,
                                        ),
                                    ],
                                ),
                                # 説明
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "説明",
                                            style=ft.TextThemeStyle.TITLE_SMALL,
                                            color=ft.Colors.GREY_500,
                                        ),
                                        ft.Text(
                                            project.description,
                                            style=ft.TextThemeStyle.BODY_MEDIUM,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                # 進捗
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "進捗",
                                            style=ft.TextThemeStyle.TITLE_SMALL,
                                            color=ft.Colors.GREY_500,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.ProgressBar(
                                                    value=project.progress_value,
                                                    color=ft.Colors.BLUE,
                                                    bgcolor=ft.Colors.GREY_300,
                                                    height=12,
                                                ),
                                                ft.Text(
                                                    project.progress_text,
                                                    style=ft.TextThemeStyle.BODY_SMALL,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=8,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=24,
                    ),
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_no_selection(self) -> ft.Control:  # type: ignore[name-defined]
        """未選択状態を構築する。

        Returns:
            未選択状態のコンテンツ
        """
        import flet as ft

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN,
                            size=48,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "プロジェクトを選択して詳細を表示",
                            style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=48,
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
                        ft.Icons.FOLDER_OPEN_OUTLINED,
                        size=64,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        "プロジェクトがありません",
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        "新規プロジェクトを作成してタスクを整理しましょう",
                        style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        text="最初のプロジェクトを作成",
                        icon=ft.Icons.ADD,
                        on_click=self._on_create_click,
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    # イベントハンドラー
    def _on_search_change(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索変更イベント。

        Args:
            e: イベント引数
        """
        keyword = e.control.value if e.control.value else ""  # type: ignore[attr-defined]
        self._controller.set_keyword(keyword)

    def _on_status_change(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """ステータス変更イベント。

        Args:
            e: イベント引数
        """
        status = e.control.value if e.control.value else None  # type: ignore[attr-defined]
        self._controller.set_status(status)

    def _on_sort_change(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """並び替え変更イベント。

        Args:
            e: イベント引数
        """
        sort_key = e.control.value  # type: ignore[attr-defined]
        self._controller.set_sort(sort_key)

    def _on_sort_toggle(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """並び順切替イベント。

        Args:
            _: イベント引数（未使用）
        """
        self._controller.toggle_sort_direction()

    def _on_create_click(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規作成クリックイベント。

        Args:
            _: イベント引数（未使用）
        """
        self.show_info_snackbar("新規プロジェクト作成機能は準備中です")

    def _get_sample_data(self) -> list[dict[str, str]]:
        """サンプルデータを取得する（開発用）。

        Returns:
            サンプルプロジェクトデータ
        """
        return [
            {
                "id": "1",
                "title": "Webアプリケーション開発",
                "description": "新しいWebアプリケーションの開発プロジェクトです。",
                "status": "進行中",
                "created_at": "2024-01-15",
                "updated_at": "2024-01-20",
                "due_date": "2024-03-31",
                "task_count": "10",
                "completed_count": "3",
            },
            {
                "id": "2",
                "title": "システムリニューアル",
                "description": "既存システムの全面的なリニューアルを行います。",
                "status": "保留",
                "created_at": "2024-01-10",
                "updated_at": "2024-01-18",
                "due_date": "2024-06-30",
                "task_count": "25",
                "completed_count": "5",
            },
            {
                "id": "3",
                "title": "モバイルアプリ開発",
                "description": "iOS・Android向けのモバイルアプリケーション開発。",
                "status": "完了",
                "created_at": "2023-12-01",
                "updated_at": "2024-01-05",
                "due_date": "2024-01-31",
                "task_count": "15",
                "completed_count": "15",
            },
        ]
