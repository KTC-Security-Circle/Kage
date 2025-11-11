"""プロジェクト管理画面

プロジェクトの一覧表示、作成、編集、削除機能を提供するメインビュー。
BaseViewパターンを採用し、一貫したUIと機能を提供する。
"""

# TODO(実装者向け): このファイルはレガシーパターンの暫定版です
# - 新しい Controller/Presenter 版 (views/projects/view.py) に移行後は削除予定です。
# - サンプルデータ呼び出し (get_enhanced_projects_sample_data) は
#   ApplicationService 経由の取得に置き換えてください。

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

from views.sample import get_enhanced_projects_sample_data
from views.shared.base_view import BaseView

from .components import show_create_project_dialog, show_edit_project_dialog


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
        self.selected_project: dict[str, str] | None = None
        self.search_query: str = ""
        self.main_row: ft.Row | None = None  # メインレイアウトの参照を保持
        self._detail_panel: ft.Container | None = None  # 詳細パネルの参照を保持

    def build_content(self) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト画面のコンテンツを構築する。

        Returns:
            プロジェクト画面のメインコンテンツ
        """
        import flet as ft

        # [ToDo: 実装機能] 実際の実装では以下を ProjectApplicationService で置き換える
        # self.projects_data = project_application_service.get_all_projects()
        self.projects_data = get_enhanced_projects_sample_data()

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
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
                                            f"複数のタスクをまとめたプロジェクト ({len(self.projects_data)}件)",
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
                    ),
                    # Main content with left-right layout
                    ft.Container(
                        content=self._create_main_row(),
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

    def _build_header_actions(self) -> ft.Control:  # type: ignore[name-defined]
        """ヘッダーアクションを構築する。

        Returns:
            ヘッダーアクションコンテンツ
        """
        import flet as ft

        return ft.Row(
            controls=[
                # 検索バー
                ft.Container(
                    content=ft.TextField(
                        hint_text="プロジェクトを検索...",
                        prefix_icon=ft.Icons.SEARCH,
                        width=256,
                        on_change=self._handle_search,
                        border_color=ft.Colors.GREY_400,
                        focused_border_color=ft.Colors.BLUE,
                    ),
                    padding=ft.padding.only(right=12),
                ),
                ft.ElevatedButton(
                    text="新規プロジェクト",
                    icon=ft.Icons.ADD,
                    on_click=self._handle_create_project,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=12,
        )

    def _build_projects_sections(self) -> ft.Control:  # type: ignore[name-defined]
        """ステータス別プロジェクトセクションを構築する。

        Returns:
            ステータス別プロジェクトセクション
        """
        import flet as ft

        filtered_projects = self._filter_projects()

        # ステータス別にプロジェクトを分類
        active_projects = [p for p in filtered_projects if p["status"] == "進行中"]
        completed_projects = [p for p in filtered_projects if p["status"] == "完了"]
        on_hold_projects = [p for p in filtered_projects if p["status"] == "保留"]
        cancelled_projects = [p for p in filtered_projects if p["status"] == "キャンセル"]

        sections = []

        # 進行中セクション
        if active_projects:
            sections.append(
                self._create_status_section("進行中", active_projects, ft.Icons.FOLDER_OPEN, ft.Colors.BLUE_600)
            )

        # 完了セクション
        if completed_projects:
            sections.append(
                self._create_status_section("完了", completed_projects, ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_600)
            )

        # 保留セクション
        if on_hold_projects:
            sections.append(
                self._create_status_section("保留", on_hold_projects, ft.Icons.SCHEDULE, ft.Colors.ORANGE_600)
            )

        # キャンセルセクション
        if cancelled_projects:
            sections.append(
                self._create_status_section("キャンセル", cancelled_projects, ft.Icons.CANCEL, ft.Colors.GREY_600)
            )

        if not sections:
            return self._build_empty_state()

        return ft.Column(
            controls=sections,
            spacing=24,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _filter_projects(self) -> list[dict[str, str]]:
        """検索クエリに基づいてプロジェクトをフィルタリングする。

        Returns:
            フィルタリングされたプロジェクトリスト
        """
        if not self.search_query:
            return self.projects_data

        query = self.search_query.lower()
        return [
            project
            for project in self.projects_data
            if query in project["name"].lower() or query in project["description"].lower()
        ]

    def _create_status_section(self, status: str, projects: list[dict[str, str]], icon: str, color: str) -> ft.Control:  # type: ignore[name-defined]
        """ステータスセクションを作成する。

        Args:
            status: ステータス名
            projects: プロジェクトリスト
            icon: アイコン
            color: 色

        Returns:
            ステータスセクション
        """
        import flet as ft

        project_cards = [self._create_project_card_for_section(project) for project in projects]

        return ft.Column(
            controls=[
                # セクションヘッダー
                ft.Row(
                    controls=[
                        ft.Icon(icon, size=20, color=color),
                        ft.Text(
                            status,
                            style=ft.TextThemeStyle.TITLE_MEDIUM,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Container(
                            content=ft.Text(
                                str(len(projects)),
                                style=ft.TextThemeStyle.LABEL_SMALL,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=ft.Colors.GREY_500,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=ft.border_radius.all(10),
                        ),
                    ],
                    spacing=8,
                ),
                # プロジェクトカード
                ft.Column(
                    controls=project_cards,
                    spacing=12,
                ),
            ],
            spacing=12,
        )

    def _create_project_card_for_section(self, project: dict[str, str]) -> ft.Control:  # type: ignore[name-defined]
        """セクション用のプロジェクトカードを作成する。

        Args:
            project: プロジェクトデータ

        Returns:
            プロジェクトカード
        """
        import flet as ft

        # 進捗計算
        total_tasks = int(project["tasks_count"])
        completed_tasks = int(project["completed_tasks"])
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        is_selected = self.selected_project and self.selected_project["id"] == project["id"]

        # ステータスバッジの色
        status_colors = {
            "進行中": ft.Colors.BLUE,
            "完了": ft.Colors.GREEN,
            "保留": ft.Colors.ORANGE,
            "キャンセル": ft.Colors.GREY,
        }
        status_color = status_colors.get(project["status"], ft.Colors.GREY)

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
                                            style=ft.TextThemeStyle.TITLE_SMALL,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Text(
                                            f"{project['created_at']} 作成",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.Icon(
                                    ft.Icons.MORE_VERT,
                                    size=16,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Container(
                            content=ft.Text(
                                project["description"],
                                style=ft.TextThemeStyle.BODY_SMALL,
                                color=ft.Colors.GREY_700,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            padding=ft.padding.symmetric(vertical=8),
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                project["status"],
                                                style=ft.TextThemeStyle.LABEL_SMALL,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            bgcolor=status_color,
                                            border_radius=12,
                                        ),
                                        ft.Text(
                                            f"{completed_tasks}/{total_tasks} タスク完了",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(
                                    value=progress / 100,
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
                ink=True,  # リップル効果を有効化
                on_click=lambda e, p=project: self._handle_project_click(e, p),
            ),
            elevation=1 if not is_selected else 3,
            color=ft.Colors.WHITE if not is_selected else ft.Colors.BLUE_50,
            surface_tint_color=ft.Colors.BLUE if is_selected else None,
        )

    def _build_project_details(self) -> ft.Control:  # type: ignore[name-defined]
        """プロジェクト詳細パネルを構築する。

        Returns:
            プロジェクト詳細パネル
        """
        import flet as ft

        if not self.selected_project:
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

        # 選択されたプロジェクトの詳細
        project = self.selected_project
        total_tasks = int(project["tasks_count"])
        completed_tasks = int(project["completed_tasks"])
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # ステータスバッジの色
        status_colors = {
            "進行中": ft.Colors.BLUE,
            "完了": ft.Colors.GREEN,
            "保留": ft.Colors.ORANGE,
            "キャンセル": ft.Colors.GREY,
        }
        status_color = status_colors.get(project["status"], ft.Colors.GREY)

        return ft.Column(
            controls=[
                # プロジェクト概要カード
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
                                                    project["name"],
                                                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    f"{project['created_at']} 作成",
                                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=4,
                                            expand=True,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                project["status"],
                                                style=ft.TextThemeStyle.LABEL_MEDIUM,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            bgcolor=status_color,
                                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                            border_radius=ft.border_radius.all(16),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
                                            project["description"],
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
                                                    value=progress / 100,
                                                    color=ft.Colors.BLUE,
                                                    bgcolor=ft.Colors.GREY_300,
                                                    height=12,
                                                ),
                                                ft.Text(
                                                    f"{progress:.0f}% 完了 ({completed_tasks} / {total_tasks} タスク)",
                                                    style=ft.TextThemeStyle.BODY_SMALL,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=8,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                # 編集ボタン
                                ft.ElevatedButton(
                                    text="編集",
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda _: self._handle_edit_project(_, project),
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.BLUE,
                                        bgcolor=ft.Colors.WHITE,
                                        side=ft.BorderSide(1, ft.Colors.BLUE),
                                    ),
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=24,
                    ),
                ),
                # タスク一覧カード
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            "タスク一覧",
                                            style=ft.TextThemeStyle.TITLE_MEDIUM,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                f"{total_tasks}件",
                                                style=ft.TextThemeStyle.LABEL_SMALL,
                                                color=ft.Colors.WHITE,
                                            ),
                                            bgcolor=ft.Colors.GREY_500,
                                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                            border_radius=ft.border_radius.all(10),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(
                                    f"このプロジェクトに含まれるタスク ({total_tasks}件)",
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.Colors.GREY_600,
                                ),
                                # [ToDo: 実装機能] プロジェクトに関連するタスクリストを表示
                                # 1. TaskApplicationService.get_tasks_by_project_id(project_id) でタスク取得
                                # 2. 各タスクをカード形式で表示（ステータスバッジ、優先度、期限付き）
                                # 3. タスククリックで/tasks画面への遷移機能
                                # 4. 空の場合は「新しいタスクを作成」ボタンと説明を表示
                                ft.Container(
                                    content=ft.Text(
                                        "タスクの詳細表示は準備中です",
                                        style=ft.TextThemeStyle.BODY_MEDIUM,
                                        color=ft.Colors.GREY_500,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    alignment=ft.alignment.center,
                                    padding=32,
                                ),
                            ],
                            spacing=16,
                        ),
                        padding=24,
                    ),
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_main_row(self) -> ft.Row:  # type: ignore[name-defined]
        """メインレイアウトの行を作成する。

        Returns:
            メインレイアウトの行
        """
        import flet as ft

        # 詳細パネルを作成して保持
        self._detail_panel = ft.Container(
            content=self._build_project_details(),
            expand=True,
        )

        self.main_row = ft.Row(
            controls=[
                # Left panel: Project list by status
                ft.Container(
                    content=self._build_projects_sections(),
                    width=480,  # Fixed width for left panel
                    expand=False,
                ),
                # Right panel: Project details
                self._detail_panel,
            ],
            spacing=24,
            expand=True,
        )
        return self.main_row

    def _handle_project_click(self, _: ft.ControlEvent, project: dict[str, str]) -> None:  # type: ignore[name-defined]
        """プロジェクトカードのクリックイベントを処理する。

        Args:
            _: クリックイベント（未使用）
            project: 選択されたプロジェクト
        """
        from loguru import logger

        logger.info(f"プロジェクトカードがクリックされました: {project['name']}")
        self._handle_project_select(project)

    def _handle_project_select(self, project: dict[str, str]) -> None:
        """プロジェクト選択を処理する。

        Args:
            project: 選択されたプロジェクト
        """
        from loguru import logger

        logger.debug(f"プロジェクト選択: {project['name']}")
        self.selected_project = project
        self._update_detail_panel()

    def _update_detail_panel(self) -> None:
        """詳細パネルを更新する（メモページの成功パターンを適用）。"""
        from loguru import logger

        if hasattr(self, "_detail_panel") and self._detail_panel:
            logger.debug("詳細パネルを更新中...")
            new_detail_panel = self._build_project_details()
            self._detail_panel.content = new_detail_panel
            self._detail_panel.update()

            # 左パネルも更新（選択状態を反映）
            self._update_project_list()
        else:
            logger.debug("詳細パネルが見つかりません")

    def _update_project_list(self) -> None:
        """プロジェクトリストを更新する（選択状態を反映）。"""
        from loguru import logger

        if hasattr(self, "main_row") and self.main_row and len(self.main_row.controls) > 0:
            import flet as ft

            logger.debug("プロジェクトリストを更新中...")
            left_container = ft.Container(
                content=self._build_projects_sections(),
                width=480,
                expand=False,
            )
            self.main_row.controls[0] = left_container
            self.main_row.update()

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
                        on_click=self._handle_create_project,
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

    def _handle_create_project(self, _: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """新規プロジェクト作成を処理する。

        Args:
            _: イベントオブジェクト（未使用）
        """
        if self.page:
            show_create_project_dialog(self.page, self._handle_save_project)

    def _handle_edit_project(self, _: ft.ControlEvent, project: dict[str, str]) -> None:  # type: ignore[name-defined]
        """プロジェクト編集を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            project: 編集対象のプロジェクト
        """
        if self.page:
            show_edit_project_dialog(self.page, project, self._handle_save_project)

    def _handle_delete_project(self, _: ft.ControlEvent, project: dict[str, str]) -> None:  # type: ignore[name-defined]
        """プロジェクト削除を処理する。

        Args:
            _: イベントオブジェクト（未使用）
            project: 削除対象のプロジェクト
        """
        # [ToDo: 実装機能] 削除確認ダイアログとProjectApplicationServiceを使用する
        # 1. 削除確認ダイアログを表示
        # 2. 確認後、project_application_service.delete_project(project_id) を呼び出し
        # 3. 成功時はリストから削除、選択状態もクリア
        # 4. エラー時は適切なエラーメッセージを表示
        self.show_info_snackbar(f"プロジェクト「{project['name']}」の削除機能は準備中です")

    def _handle_search(self, e: ft.ControlEvent) -> None:  # type: ignore[name-defined]
        """検索を処理する。

        Args:
            e: イベントオブジェクト
        """
        self.search_query = e.control.value if e.control.value else ""  # type: ignore[attr-defined]
        if self.page:
            self.page.update()

    def _handle_save_project(self, project_data: dict[str, str]) -> None:
        """プロジェクト保存を処理する。

        Args:
            project_data: 保存するプロジェクトデータ
        """
        # [ToDo: 実装機能] 実際の実装では ProjectApplicationService を使用して
        # プロジェクトの新規作成・更新処理を行う予定です。
        # 例: project_application_service.create_project(project_data) など

        # 暫定実装（サンプルデータ操作）
        existing_project = None
        for i, project in enumerate(self.projects_data):
            if project["id"] == project_data["id"]:
                existing_project = i
                break

        if existing_project is not None:
            # 既存プロジェクトの更新
            self.projects_data[existing_project] = project_data
            self.show_success_snackbar(f"プロジェクト「{project_data['name']}」を更新しました")
            # 選択されたプロジェクトも更新
            if self.selected_project and self.selected_project["id"] == project_data["id"]:
                self.selected_project = project_data
        else:
            # 新規プロジェクトの追加
            self.projects_data.append(project_data)
            self.show_success_snackbar(f"プロジェクト「{project_data['name']}」を作成しました")

        if self.page:
            self.page.update()

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
        if self.page:
            self.page.update()
