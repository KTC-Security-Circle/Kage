"""プロジェクト画面のView層

MVP パターンの View として、Flet UI の描画とイベント配線の最小限実装。
ロジックは Controller に委譲し、表示に集中する。
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

if TYPE_CHECKING:
    from .presenter import ProjectCardVM, ProjectDetailVM

from logic.application.project_application_service import ProjectApplicationService
from models import ProjectStatus
from views.projects.components import (
    ProjectCardList,
    ProjectDetailPanel,
    ProjectNoSelection,
    ProjectStatusTabs,
    show_create_project_dialog,
    show_edit_project_dialog,
)
from views.projects.controller import ProjectController
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import HeaderButtonData
from views.theme import get_error_color, get_on_primary_color


class ProjectsView(BaseView):
    """プロジェクト画面のメインView。

    MVP パターンに従い、描画とイベント配線のみを担当。
    ビジネスロジックは Controller に委譲し、UI に集中する。

    Attributes:
        _controller: プロジェクトコントローラー
        _list_container: プロジェクトリストコンテナ
        _detail_container: プロジェクト詳細コンテナ
    """

    def __init__(self, props: BaseViewProps) -> None:
        """ProjectsView を初期化する。

        Args:
            props: View共通プロパティ
        """
        super().__init__(props)

        # データ取得: ApplicationService を優先して利用する
        # - 例外時のユーザー通知は BaseView の snackbar を利用
        service = self.apps.get_service(ProjectApplicationService)

        # コントローラー初期化
        self._controller = ProjectController(
            service=service,
            on_list_change=self._render_list,
            on_detail_change=self._render_detail,
            # BaseView.show_error_snackbar は (page, message) 署名のためアダプタで統一
            on_error=lambda msg: self.show_error_snackbar(self.page, msg),
            apps=self.apps,
        )

        # UI コンポーネント
        self._project_list: ProjectCardList | None = None
        self._detail_panel: ProjectDetailPanel | ProjectNoSelection | None = None
        self._status_tabs: ProjectStatusTabs | None = None
        self._detail_container: ft.Container | None = None

    def build_content(self) -> ft.Control:
        """プロジェクト画面のコンテンツを構築する。

        Returns:
            プロジェクト画面のメインコンテンツ
        """
        # Headerコンポーネント (検索と新規作成ボタン)
        header = self.create_header(
            title="プロジェクト",
            subtitle="複数のタスクをまとめたプロジェクト管理",
            search_placeholder="プロジェクトを検索...",
            on_search=self._handle_search,
            action_buttons=[
                HeaderButtonData(
                    label="新規プロジェクト",
                    icon=ft.Icons.ADD,
                    on_click=self._handle_create_click,
                    is_primary=True,
                )
            ],
        )

        # ステータスタブ
        self._status_tabs = ProjectStatusTabs(
            on_tab_change=self._on_tabs_change,
            active_status=self._controller.state.status,
            tab_counts=self._safe_get_counts(),
        )

        # プロジェクトリスト（初期は空）
        self._project_list = ProjectCardList(
            projects=[],
            on_select=self._controller.select_project,
            selected_id=self._controller.state.selected_id,
            on_create=self._create_project,
        )

        # 詳細パネル(初期は未選択状態)
        self._detail_panel = ProjectNoSelection()

        # 詳細パネル用のコンテナを保持
        self._detail_container = ft.Container(
            content=self._detail_panel,
            col={"xs": 12, "lg": 7},
        )

        # 2カラムレイアウト
        layout = ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    self._status_tabs,
                    ft.Divider(),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                content=self._project_list,
                                col={"xs": 12, "lg": 5},
                                padding=ft.padding.only(right=12),
                            ),
                            self._detail_container,
                        ],
                        expand=True,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

        # UIコンポーネントが構築された後に初期データを読み込む
        try:
            self._controller.refresh()
            logger.debug("ProjectsView: 初期データ読み込み完了")
        except Exception as e:
            logger.error(f"ProjectsView: 初期データ読み込みエラー: {e}")
            # エラーが発生しても空状態で画面を表示する

        return layout

    def _render_list(self, projects: list[ProjectCardVM]) -> None:
        """プロジェクトリストを描画する。

        Args:
            projects: 表示するプロジェクトのViewModelリスト
        """
        if not self._project_list:
            return

        self._project_list.update_projects(
            projects,
            selected_id=self._controller.state.selected_id,
        )

        # タブバッジを更新
        if self._status_tabs:
            self._status_tabs.update_counts(self._safe_get_counts())

    def _render_detail(self, project: ProjectDetailVM | None) -> None:
        """プロジェクト詳細を描画する。

        Args:
            project: 表示するプロジェクトの詳細ViewModel（None の場合は空表示）
        """
        if project is None:
            # 詳細パネルから未選択状態へ切り替え
            self._detail_panel = ProjectNoSelection()
        elif isinstance(self._detail_panel, ProjectDetailPanel):
            # 既存の詳細パネルを更新
            self._detail_panel.update_project(project)
            return  # update_project内でupdate()が呼ばれるので、ここでは不要
        else:
            # 未選択状態から詳細パネルへ切り替え
            self._detail_panel = ProjectDetailPanel(
                project=project,
                on_edit=self._open_edit_dialog,
                on_delete=self._confirm_delete,
            )

        # コンテナの内容を更新
        if self._detail_container:
            self._detail_container.content = self._detail_panel
            try:
                self._detail_container.update()
            except AssertionError:
                # ページにまだ追加されていない場合はスキップ
                logger.debug("詳細コンテナがまだページに追加されていません")

    # ------------------------------------------------------------------
    # 編集 / 削除 ダイアログ操作
    # ------------------------------------------------------------------
    def _open_edit_dialog(self, vm: ProjectDetailVM) -> None:
        """編集ダイアログを開いて保存時に更新処理を呼び出す。"""
        # VMのステータスを内部コードへ逆変換
        try:
            status_code = ProjectStatus.parse(vm.status).value
        except ValueError:
            status_code = "active"

        project_dict: dict[str, str] = {
            "id": vm.id,
            "title": vm.title,
            "description": vm.description,
            "status": status_code,
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
            # task_idsが含まれていればタスクのproject_idを更新
            if "task_ids" in updated:
                task_ids_value = updated["task_ids"]
                logger.debug(f"プロジェクト編集: task_ids={task_ids_value}, type={type(task_ids_value)}")
                if isinstance(task_ids_value, list):
                    logger.debug(f"タスクをプロジェクトに更新: project_id={vm.id}, task_ids={task_ids_value}")
                    self._controller.update_project_tasks(vm.id, task_ids_value)
            else:
                logger.debug("プロジェクト編集: task_idsは含まれていません")
            self.with_loading(lambda: self._controller.update_project(vm.id, changes))
            self.show_success_snackbar("プロジェクトを更新しました")

        # 利用可能なタスクを取得
        available_tasks = self._get_available_tasks()
        show_edit_project_dialog(self.page, project_dict, on_save=_on_save, available_tasks=available_tasks)

    def _confirm_delete(self, vm: ProjectDetailVM) -> None:
        """削除確認を表示し、確定時に削除処理を実行する。"""

        def _close(_: ft.ControlEvent) -> None:
            dialog.open = False
            self.page.update()

        def _delete(_: ft.ControlEvent) -> None:
            self.with_loading(lambda: self._controller.delete_project(vm.id))
            _close(_)
            self.show_success_snackbar("プロジェクトを削除しました")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("削除の確認", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            content=ft.Text(f"「{vm.title}」を削除します。よろしいですか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=_close),
                ft.ElevatedButton(
                    "削除",
                    icon=ft.Icons.DELETE,
                    bgcolor=get_error_color(),
                    color=get_on_primary_color(),
                    on_click=_delete,
                ),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # イベントハンドラー
    def _handle_search(self, query: str) -> None:
        """検索ハンドラ。

        Args:
            query: 検索クエリ
        """
        self._controller.set_keyword(query)

    def _on_tabs_change(self, status: ProjectStatus | None) -> None:
        """タブ変更時のイベントハンドラー。

        Args:
            status: 選択されたステータス（None = すべて）
        """
        if status is None:
            self._controller.set_status(None)
        else:
            self._controller.set_status(status.value)

        self.safe_update()

    def _safe_get_counts(self) -> dict[ProjectStatus, int]:
        """各ステータスの件数を安全に取得。

        Returns:
            ステータスごとの件数辞書
        """
        try:
            return self._controller.get_counts()
        except Exception:
            return {
                ProjectStatus.ACTIVE: 0,
                ProjectStatus.ON_HOLD: 0,
                ProjectStatus.COMPLETED: 0,
                ProjectStatus.CANCELLED: 0,
            }

    def _get_available_tasks(self) -> list[dict[str, str | None]]:
        """利用可能なタスクを取得する

        Returns:
            タスクのリスト（id, title, project_idを含む辞書）
        """
        try:
            from logic.application.task_application_service import TaskApplicationService

            task_service = self.apps.get_service(TaskApplicationService)
            tasks = task_service.get_all_tasks()
            return [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "project_id": str(task.project_id) if task.project_id else None,
                }
                for task in tasks
            ]
        except Exception as e:
            logger.warning(f"タスクの取得に失敗しました: {e}")
            return []

    def _handle_create_click(self) -> None:
        """Header作成ボタンのクリック処理。"""
        self._create_project()

    def _create_project(self) -> None:
        """プロジェクト作成のビジネスロジックを実行する。"""
        logger.debug("新規プロジェクトダイアログを開きます")

        # 既存の美しいダイアログ実装を利用
        def _on_save(data: dict[str, str]) -> None:
            """ダイアログから受け取ったデータを正規化しControllerへ渡す。

            Args:
                data: ダイアログで入力されたプロジェクト基本情報
            """
            today = datetime.now().strftime("%Y-%m-%d")

            status_display = (data.get("status") or "Active").strip()
            try:
                status_raw = ProjectStatus.parse(status_display).value
            except ValueError:
                status_raw = "active"

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
            # task_idsが含まれていればタスクのproject_idを設定
            task_ids = data.get("task_ids", [])
            logger.debug(f"プロジェクト作成: task_ids={task_ids}, type={type(task_ids)}")
            # 作成処理もローディング表示で包み、更新/削除と挙動を統一
            project_id = self.with_loading(lambda: self._controller.create_project(new_project, select=True))
            logger.debug(f"プロジェクト作成完了: project_id={project_id}")
            # タスクをプロジェクトに割り当て
            if task_ids and project_id and isinstance(task_ids, list) and isinstance(project_id, str):
                logger.debug(f"タスクをプロジェクトに割り当て: project_id={project_id}, task_ids={task_ids}")
                self._controller.update_project_tasks(project_id, task_ids)
            else:
                logger.debug(
                    f"タスク割り当てスキップ: task_ids={task_ids}, "
                    f"project_id={project_id}, is_list={isinstance(task_ids, list)}"
                )
            self.show_success_snackbar("プロジェクトを追加しました")

        # 利用可能なタスクを取得
        available_tasks = self._get_available_tasks()
        show_create_project_dialog(self.page, on_save=_on_save, available_tasks=available_tasks)
