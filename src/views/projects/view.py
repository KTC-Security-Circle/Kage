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

# Application service (domain access)
from logic.application.apps import ApplicationServices
from logic.application.project_application_service import ProjectApplicationService

# View / UI layer components
from views.projects.components.project_dialogs import (
    show_create_project_dialog,
    show_edit_project_dialog,
)
from views.projects.controller import ProjectController
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

    def __init__(self, page: ft.Page) -> None:
        """ProjectsView を初期化する。

        Args:
            page: Fletページインスタンス
        """
        super().__init__(page)

        # データ取得: ApplicationService を優先して利用する
        # - 例外時のユーザー通知は BaseView の snackbar を利用
        apps = ApplicationServices.create()
        service = apps.get_service(ProjectApplicationService)

        # コントローラー初期化
        self._controller = ProjectController(
            service=service,
            on_list_change=self._render_list,
            on_detail_change=self._render_detail,
            # BaseView.show_error_snackbar は (page, message) 署名のためアダプタで統一
            on_error=lambda msg: self.show_error_snackbar(self.page, msg),
        )

        # UI コンテナ
        self._list_container: ft.Column | None = None
        self._detail_container: ft.Container | None = None

    def build_content(self) -> ft.Control:
        """プロジェクト画面のコンテンツを構築する。

        Returns:
            プロジェクト画面のメインコンテンツ
        """
        import flet as ft

        # コンテナ初期化
        self._list_container = ft.Column(expand=True, spacing=8)
        self._detail_container = ft.Container(expand=True)

        # 初期データ取得: ここで refresh を呼ぶが、未マウント時の update() 呼び出しは
        # _render_list / _render_detail 内で page 属性存在確認後に行うため安全。
        try:
            self._controller.refresh()
        except Exception as e:  # [AI GENERATED] 初期ロード失敗のフォールバック
            logger.warning(f"初期ロード時に一時的なエラー: {e}")

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

    def did_mount(self) -> None:
        """マウント後に初期データを読み込む。"""
        super().did_mount()
        # did_mount は BaseView(ft.Container) では自動コールされないため使用しない

    def _build_header(self) -> ft.Control:
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

    def _build_header_actions(self) -> ft.Control:
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
                        ft.dropdown.Option("全て", "全て"),
                        ft.dropdown.Option("進行中", "進行中"),
                        ft.dropdown.Option("完了", "完了"),
                        ft.dropdown.Option("保留", "保留"),
                        ft.dropdown.Option("キャンセル", "キャンセル"),
                    ],
                    value="全て",
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

    def _build_main_content(self) -> ft.Control:
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

            # コントロールがまだ page に追加されていない初期段階では update() を避ける
            if getattr(self._list_container, "page", None):  # type: ignore[attr-defined]
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

            if getattr(self._detail_container, "page", None):  # type: ignore[attr-defined]
                self._detail_container.update()

    def _build_project_card(self, project: ProjectCardVM) -> ft.Control:
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

    def _build_project_detail(self, project: ProjectDetailVM) -> ft.Control:
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
                                                    # TODO: 日付表示の整形
                                                    # - ロケール/タイムゾーン/相対表現の方針は Presenter で統一し、
                                                    #   View は整形済み文字列のみを表示する。
                                                    f"{project.created_at} 作成",
                                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=4,
                                            expand=True,
                                        ),
                                        ft.Row(
                                            controls=[
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
                                                ft.IconButton(
                                                    icon=ft.Icons.EDIT,
                                                    tooltip="編集",
                                                    on_click=lambda _: self._open_edit_dialog(project),
                                                ),
                                                ft.IconButton(
                                                    icon=ft.Icons.DELETE_OUTLINE,
                                                    tooltip="削除",
                                                    on_click=lambda _: self._confirm_delete(project),
                                                ),
                                            ],
                                            spacing=8,
                                            alignment=ft.MainAxisAlignment.END,
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

    def _build_no_selection(self) -> ft.Control:
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

    def _build_empty_state(self) -> ft.Control:
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

    # ------------------------------------------------------------------
    # 編集 / 削除 ダイアログ操作
    # ------------------------------------------------------------------
    def _open_edit_dialog(self, vm: ProjectDetailVM) -> None:
        """編集ダイアログを開いて保存時に更新処理を呼び出す。"""
        from views.shared.status_utils import normalize_status

        project_dict: dict[str, str] = {
            "id": vm.id,
            "title": vm.title,
            "description": vm.description,
            "status": normalize_status(vm.status),  # 内部コードへ正規化
            "due_date": vm.due_date or "",
            "tasks_count": str(vm.task_count),
            "completed_tasks": str(vm.completed_count),
        }

        def _on_save(updated: dict[str, str]) -> None:
            changes = {
                "title": updated.get("title", ""),
                "description": updated.get("description", ""),
                "status": updated.get("status", ""),
                "due_date": updated.get("due_date"),
            }
            self.with_loading(lambda: self._controller.update_project(vm.id, changes))
            self.show_success_snackbar("プロジェクトを更新しました")

        show_edit_project_dialog(self.page, project_dict, on_save=_on_save)

    def _confirm_delete(self, vm: ProjectDetailVM) -> None:
        """削除確認を表示し、確定時に削除処理を実行する。"""
        import flet as ft

        def _close(_: ft.ControlEvent) -> None:
            dialog.open = False
            self.page.update()

        def _delete(_: ft.ControlEvent) -> None:
            self.with_loading(lambda: self._controller.delete_project(vm.id))
            _close(_)
            self.show_success_snackbar("プロジェクトを削除しました")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("削除の確認", style=ft.TextThemeStyle.TITLE_MEDIUM),
            content=ft.Text(f"「{vm.title}」を削除します。よろしいですか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=_close),
                ft.ElevatedButton(
                    "削除",
                    icon=ft.Icons.DELETE,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=_delete,
                ),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # イベントハンドラー
    def _on_search_change(self, e: ft.ControlEvent) -> None:
        """検索変更イベント。

        Args:
            e: イベント引数
        """
        keyword = e.control.value if e.control.value else ""
        self._controller.set_keyword(keyword)

    def _on_status_change(self, e: ft.ControlEvent) -> None:
        """ステータス変更イベント。

        Args:
            e: イベント引数
        """
        status = e.control.value if e.control.value else None
        self._controller.set_status(status)

    def _on_sort_change(self, e: ft.ControlEvent) -> None:
        """並び替え変更イベント。

        Args:
            e: イベント引数
        """
        sort_key = e.control.value
        self._controller.set_sort(sort_key)

    def _on_sort_toggle(self, _: ft.ControlEvent) -> None:
        """並び順切替イベント。

        Args:
            _: イベント引数（未使用）
        """
        self._controller.toggle_sort_direction()

    def _on_create_click(self, _: ft.ControlEvent) -> None:
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
            # 作成処理もローディング表示で包み、更新/削除と挙動を統一
            self.with_loading(lambda: self._controller.create_project(new_project, select=True))
            self.show_success_snackbar("プロジェクトを追加しました")

        show_create_project_dialog(self.page, on_save=_on_save)
