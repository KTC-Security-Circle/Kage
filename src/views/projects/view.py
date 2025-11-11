"""プロジェクト画面のView層

MVP パターンの View として、Flet UI の描画とイベント配線の最小限実装。
ロジックは Controller に委譲し、表示に集中する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft

    from .presenter import ProjectCardVM, ProjectDetailVM

from loguru import logger

from views.projects.components.project_dialogs import show_create_project_dialog
from views.projects.controller import ProjectController
from views.projects.query import InMemoryProjectQuery
from views.sample import get_projects_for_ui
from views.shared.base_view import BaseView


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

        # TODO: データ取得の本実装に差し替える
        # - ここでは表示確認のためサンプルデータを InMemory の Query に流し込んでいます。
        # - 本番実装では DI コンテナ (src/logic/container.py) から ProjectQuery 実装
        #   もしくは ProjectApplicationService を解決し、Repository 経由でデータを取得してください。
        # - 例: query = container.resolve(ProjectQuery) / service = container.resolve(ProjectApplicationService)
        # - 例外時のユーザー通知は BaseView の snackbar を利用し、適宜リトライ導線も検討ください。
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
        # TODO: 非同期取得にする場合
        # - ApplicationService 側で I/O を行うなら読み込み中インジケータを表示してから
        #   完了時に _controller.refresh() 相当の更新を呼び出してください。
        # - エラー時は snackbar で通知し、空表示/前回キャッシュ表示などの方針を決めるとUXが安定します。
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
        logger.debug("新規プロジェクトダイアログを開きます")

        # 既存の美しいダイアログ実装を利用
        def _on_save(data: dict[str, str]) -> None:
            """ダイアログから受け取ったデータを正規化しControllerへ渡す。

            Args:
                data: ダイアログで入力されたプロジェクト基本情報
            """
            import uuid
            from datetime import datetime

            today = datetime.now().strftime("%Y-%m-%d")

            # ステータス値はダイアログから受け取った表示値(Active/On-Hold/Completed 等)を内部コードに正規化。
            # TODO: 重複正規化ロジックの最終的な移設
            #  - normalize_status は現在 views.shared.status_utils にあるが、
            #    ドメイン境界の明確化のため最終的には models (例: models/project.py) 側で
            #    ProjectStatus に紐づくユーティリティとして提供し、View 層は直接参照しない設計にする。
            #  - 関連重複箇所: controller.set_status / project_dialogs.save_project / query.list_projects
            status_display = (data.get("status") or "Active").strip()
            from views.shared.status_utils import normalize_status

            status_raw = normalize_status(status_display)

            # due_date は未設定時 None へ統一
            due_date_raw = (data.get("due_date") or "").strip()
            due_date = due_date_raw if due_date_raw else None

            # TODO: 作成ロジックの本実装
            # - 下記は InMemoryQuery 前提の暫定追加です。
            # - 実装では ProjectApplicationService.create_project(...) を呼び出し、
            #   成功時に controller.refresh() で最新状態を再取得してください。
            # - 失敗時は self.show_error_snackbar(...) でユーザーに通知しましょう。
            new_project = {
                "id": data.get("id", str(uuid.uuid4())),
                "title": data.get("title", "新規プロジェクト"),
                "description": data.get("description", ""),
                "status": status_raw,
                "created_at": today,
                "updated_at": today,
                "due_date": due_date,
                # task関連は未入力のため初期値（task_id は作成時空リスト）
                "task_count": "0",
                "completed_count": "0",
            }
            self._controller.create_project(new_project, select=True)
            self.show_success_snackbar("プロジェクトを追加しました")

        show_create_project_dialog(self.page, on_save=_on_save)  # type: ignore[arg-type]

    def _get_sample_data(self) -> list[dict[str, str]]:
        """`views.sample` のサンプルデータをプロジェクトView用形式に変換して取得する。

        `sample.py` 内の `get_projects_for_ui()` は以下のキーを持つ:
        - id, name, description, status, tasks_count, completed_tasks, created_at, start_date, end_date, priority

        本 View / Presenter 層では以下のキーを期待する:
        - id, title(or name), description, status, created_at, updated_at, due_date,
          task_count(or tasks_count), completed_count(or completed_tasks)

        欠損する `updated_at` は `created_at` を流用し、`due_date` は `end_date` をマッピングする。

        Returns:
            Presenter が処理可能な正規化済みプロジェクト辞書リスト
        """
        # TODO: サンプルデータの撤去
        # - 実運用では ProjectApplicationService から取得し、Presenter が期待する
        #   キー構造に合わせてマッピングしてください（可能なら Presenter 側で完結させる）。
        return build_projects_sample_data(get_projects_for_ui())


def build_projects_sample_data(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """`views.sample.get_projects_for_ui()`の出力をPresenterが扱える形へ正規化する。

    Args:
        items: sample由来の生データリスト

    Returns:
        正規化済みのプロジェクト辞書リスト
    """
    return [
        {
            "id": str(item.get("id", "")),
            # sample側は name を使用しているが Presenter 側は title も受け付ける
            "title": str(item.get("title", item.get("name", ""))),
            "description": str(item.get("description", "")),
            # 日本語ステータス想定（Presenter/Controller側での表示には支障なし）
            "status": str(item.get("status", "")),
            "created_at": str(item.get("created_at", item.get("start_date", ""))),
            # updated_at が無いので created_at を暫定利用（実データ導入時に差し替え）
            "updated_at": str(item.get("created_at", item.get("start_date", ""))),
            # due_date は sample 側 end_date をマッピング
            "due_date": str(item.get("end_date", "")),
            # Presenter は tasks_count / completed_tasks もしくは task_count / completed_count を受け付ける
            "task_count": str(item.get("tasks_count", "0")),
            "completed_count": str(item.get("completed_tasks", "0")),
        }
        for item in items
    ]
