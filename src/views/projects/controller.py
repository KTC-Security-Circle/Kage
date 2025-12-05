"""プロジェクト画面のコントローラー

イベント→状態更新→データ取得→並び替え→ViewModel生成→再描画の調停役。
MVP パターンの Presenter と View の橋渡しを行う。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from loguru import logger

from models import ProjectStatus, ProjectUpdate

from .ordering import apply_order, get_order_strategy
from .presenter import (
    ProjectCardVM,
    ProjectDetailVM,
    to_card_vm,
    to_detail_vm,
)
from .state import ProjectState

if TYPE_CHECKING:
    from collections.abc import Callable

    from models import ProjectRead


class ProjectApplicationPort(Protocol):
    """ProjectApplicationService へ依存を抽象化するポート。

    View/Controller はこの Protocol のみを前提にし、具体的な取得方法や
    UnitOfWork/Repository には依存しない。テストではモックを注入可能。
    """

    def get_all_projects(self) -> list[ProjectRead]:  # pragma: no cover - interface
        """全プロジェクト取得"""
        ...

    def get_by_id(self, project_id: UUID) -> ProjectRead | None:  # pragma: no cover - interface
        """ID で単一取得。見つからない場合 None。"""
        ...

    def search(
        self,
        query: str,
        *,
        status: ProjectStatus | None = None,
    ) -> list[ProjectRead]:  # pragma: no cover - interface
        """検索（任意でステータスフィルタ）。"""
        ...

    def list_by_status(self, status: ProjectStatus) -> list[ProjectRead]:  # pragma: no cover - interface
        """ステータス別一覧取得。"""
        ...

    def create(
        self,
        title: str,
        description: str | None = None,
        *,
        status: ProjectStatus | None = None,
    ) -> ProjectRead:  # pragma: no cover - interface
        """プロジェクト作成。"""
        ...

    def update(self, project_id: UUID, update_data: ProjectUpdate) -> ProjectRead:  # pragma: no cover - interface
        """プロジェクト更新。"""
        ...

    def delete(self, project_id: UUID) -> bool:  # pragma: no cover - interface
        """プロジェクト削除。"""
        ...


class ProjectController:
    """ProjectsView 用の調停役 Controller。

    - Port 経由で ApplicationService を呼び出し、一覧/詳細/検索/並び替えを行う
    - 不変 `ProjectState` を生成し UI 更新をコールバックで通知
    - 例外発生時はユーザ通知ハンドラ経由で UI レイヤに委譲
    """

    def __init__(
        self,
        service: ProjectApplicationPort,
        on_list_change: Callable[[list[ProjectCardVM]], None],
        on_detail_change: Callable[[ProjectDetailVM | None], None],
        on_error: Callable[[str], None] | None = None,
        *,
        apps: object | None = None,
    ) -> None:
        """Controller 初期化。

        Args:
            service: ProjectApplicationPort 実装（ApplicationService を抽象化）
            on_list_change: 一覧 VM 更新時コールバック
            on_detail_change: 詳細 VM 更新時コールバック
            on_error: ユーザ通知用エラーハンドラ（SnackBar 等）
            apps: ApplicationServices インスタンス（タスク取得用）
        """
        self._service = service
        self._state = ProjectState()
        self._on_list_change = on_list_change
        self._on_detail_change = on_detail_change
        self._on_error = on_error
        self._apps = apps

    def _notify_error(self, message: str) -> None:
        """UI 層へエラー通知（存在すれば）。"""
        logger.error(message)
        if self._on_error:
            self._on_error(message)

    @property
    def state(self) -> ProjectState:
        """現在のUI状態を取得する。

        Returns:
            現在の ProjectState インスタンス
        """
        return self._state

    def set_keyword(self, keyword: str) -> None:
        """検索キーワードを設定する。

        Args:
            keyword: 新しい検索キーワード
        """
        logger.debug(f"検索キーワード設定: '{keyword}'")
        new_state = self._state.update(keyword=keyword)
        self._update_and_render(new_state)

    def set_status(self, status: str | None) -> None:
        """ステータスフィルタを設定する。

        Args:
            status: 新しいステータスフィルタ(None の場合は全て)
        """
        status_filter = None
        if status and status.strip():
            try:
                # ドメイン層の parse を使用して統一的に変換
                status_filter = ProjectStatus.parse(status)
            except ValueError:
                # 未知のステータスは全件扱い
                logger.debug(f"未知のステータス入力を全件扱いに変換: {status}")
                status_filter = None

        logger.debug(f"ステータスフィルタ設定: {status_filter}")
        new_state = self._state.update(status=status_filter)
        self._update_and_render(new_state)

    def set_sort(self, key: str, *, desc: bool | None = None) -> None:
        """並び替え設定を変更する。

        Args:
            key: 並び替えキー
            desc: 降順フラグ（None の場合は現在の設定を維持）
        """
        current_desc = desc if desc is not None else self._state.sort_desc
        logger.debug(f"並び替え設定: key={key}, desc={current_desc}")

        try:
            # 並び替えキーの妥当性チェック
            get_order_strategy(key)
            new_state = self._state.update(sort_key=key, sort_desc=current_desc)
            self._update_and_render(new_state)
        except KeyError as e:
            logger.error(f"並び替えキーエラー: {e}")

    def set_sort_asc(self, key: str) -> None:
        """並び替えを昇順で設定する。

        Args:
            key: 並び替えキー
        """
        self.set_sort(key, desc=False)

    def set_sort_desc(self, key: str) -> None:
        """並び替えを降順で設定する。

        Args:
            key: 並び替えキー
        """
        self.set_sort(key, desc=True)

    def toggle_sort_direction(self) -> None:
        """並び替え方向を切り替える。"""
        new_state = self._state.toggle_sort_direction()
        logger.debug(f"並び替え方向切替: desc={new_state.sort_desc}")
        self._update_and_render(new_state)

    def select_project(self, project_id: str) -> None:
        """プロジェクトを選択する。

        Args:
            project_id: 選択するプロジェクトのID
        """
        logger.debug(f"プロジェクト選択: {project_id}")
        new_state = self._state.update(selected_id=project_id)
        self._update_and_render(new_state)

    def clear_selection(self) -> None:
        """プロジェクト選択をクリアする。"""
        logger.debug("プロジェクト選択クリア")
        new_state = self._state.clear_selection()
        self._update_and_render(new_state)

    def refresh(self) -> None:
        """データを再読み込みして画面を更新する。"""
        logger.debug("データ再読み込み: 一覧・詳細を再描画")
        # 初回ロードや外部要因で状態が不変でも、強制的に描画更新する
        self._update_list()
        self._update_detail()

    def get_counts(self) -> dict[ProjectStatus, int]:
        """各ステータスの件数を取得する。

        Returns:
            ステータスごとの件数辞書
        """
        try:
            all_projects = self._service.get_all_projects()
            counts: dict[ProjectStatus, int] = {
                ProjectStatus.ACTIVE: 0,
                ProjectStatus.ON_HOLD: 0,
                ProjectStatus.COMPLETED: 0,
                ProjectStatus.CANCELLED: 0,
            }
            for project in all_projects:
                status = getattr(project, "status", None)
                if isinstance(status, ProjectStatus):
                    counts[status] = counts.get(status, 0) + 1
        except Exception as e:
            logger.warning(f"ステータス件数取得エラー: {e}")
            return {
                ProjectStatus.ACTIVE: 0,
                ProjectStatus.ON_HOLD: 0,
                ProjectStatus.COMPLETED: 0,
                ProjectStatus.CANCELLED: 0,
            }
        else:
            return counts

    def create_project(self, project: dict[str, str], *, select: bool = True) -> str | None:
        """新規プロジェクトを ApplicationService 経由で作成する。

        Args:
            project: ダイアログ等から受け取った新規作成データ（title, description, status 等）
            select: 作成後に選択状態にするか

        Returns:
            作成されたプロジェクトのID（文字列）、失敗時はNone
        """
        title = str(project.get("title") or project.get("name") or "").strip()
        description = str(project.get("description") or "").strip() or None
        status_text = str(project.get("status") or "").strip()

        # ステータスはドメインのparseで正規化
        status_enum = None
        if status_text:
            try:
                status_enum = ProjectStatus.parse(status_text)
            except ValueError:
                status_enum = None

        if not title:
            self._notify_error("タイトルを入力してください。")
            return None

        try:
            created = self._service.create(title, description, status=status_enum)
            new_id = str(getattr(created, "id", ""))
            logger.debug(f"プロジェクト作成成功: new_id={new_id}, created.id={created.id}")

            new_state = self._state
            if select:
                new_state = new_state.update(selected_id=new_id)
            self._state = new_state
            self._update_list()
            self._update_detail()
        except Exception as e:
            logger.exception(f"プロジェクト作成中にエラー: {e}")
            self._notify_error("プロジェクトの作成に失敗しました。詳細はログを参照してください。")
            return None
        else:
            return new_id

    def update_project(self, project_id: str, changes: dict[str, Any]) -> None:
        """既存プロジェクトを ApplicationService 経由で更新する。

        Args:
            project_id: 文字列のプロジェクトID
            changes: 変更フィールド（title/description/status/due_date など）
        """
        try:
            pid = UUID(project_id)

            update_kwargs: dict[str, Any] = {}
            if "title" in changes and changes.get("title") is not None:
                update_kwargs["title"] = str(changes["title"]).strip()
            if "description" in changes:
                desc_val = changes.get("description")
                update_kwargs["description"] = None if desc_val in (None, "") else str(desc_val)
            if "status" in changes and changes.get("status"):
                try:
                    # ドメインのparseで正規化
                    update_kwargs["status"] = ProjectStatus.parse(str(changes["status"]))
                except ValueError:
                    logger.warning(f"未知のステータス更新要求: {changes['status']}")
            if "due_date" in changes and changes.get("due_date"):
                update_kwargs["due_date"] = changes["due_date"]

            update_data = ProjectUpdate(**update_kwargs)
            updated = self._service.update(pid, update_data)

            # 状態更新: 選択IDが一致していれば詳細も更新
            if self._state.selected_id == str(getattr(updated, "id", "")):
                self._update_detail()
            # 一覧は常に更新
            self._update_list()
        except ValueError:
            self._notify_error("不正なプロジェクトIDです。")
        except Exception as e:
            logger.exception(f"プロジェクト更新中にエラー: {e}")
            self._notify_error("プロジェクトの更新に失敗しました。詳細はログを参照してください。")

    def update_project_tasks(self, project_id: str, task_ids: list[str]) -> None:
        """プロジェクトに関連するタスクのproject_idを更新する。

        Args:
            project_id: プロジェクトID
            task_ids: 関連付けるタスクIDのリスト
        """
        try:
            from logic.application.task_application_service import TaskApplicationService
            from logic.unit_of_work import SqlModelUnitOfWork
            from models import TaskUpdate

            pid = UUID(project_id)

            # TaskApplicationServiceを初期化
            task_service = TaskApplicationService(SqlModelUnitOfWork)

            # このプロジェクトに以前属していたタスクを取得してクリア
            all_tasks = task_service.get_all_tasks()
            for task in all_tasks:
                if task.project_id == pid and str(task.id) not in task_ids:
                    # このプロジェクトから外す
                    task_service.update(task.id, TaskUpdate(project_id=None))

            # 新しく選択されたタスクを更新
            for task_id_str in task_ids:
                try:
                    tid = UUID(task_id_str)
                    task_service.update(tid, TaskUpdate(project_id=pid))
                except ValueError:
                    logger.warning(f"不正なタスクID: {task_id_str}")

            logger.info(f"プロジェクト {project_id} のタスクを更新しました")
        except Exception as e:
            logger.exception(f"タスク更新中にエラー: {e}")
            self._notify_error("タスクの更新に失敗しました。")

    def delete_project(self, project_id: str) -> None:
        """プロジェクトを ApplicationService 経由で削除する。

        Args:
            project_id: 削除するプロジェクトのID（文字列）
        """
        try:
            pid = UUID(project_id)
        except ValueError:
            self._notify_error("不正なプロジェクトIDです。")
            return

        try:
            success = False
            delete_method = getattr(self._service, "delete", None)
            if callable(delete_method):
                success = bool(delete_method(pid))  # type: ignore[no-any-return]
            else:
                logger.warning("Port に delete が未実装のため操作をスキップ")

            if not success:
                self._notify_error("プロジェクトの削除に失敗しました。詳細はログを参照してください。")
                return

            # 選択解除と一覧更新
            if self._state.selected_id == project_id:
                self._state = self._state.clear_selection()
                self._on_detail_change(None)
            self._update_list()
            logger.info(f"プロジェクト削除完了: {project_id}")
        except Exception as e:
            logger.exception(f"プロジェクト削除中にエラー: {e}")
            self._notify_error("プロジェクトの削除に失敗しました。詳細はログを参照してください。")

    def _update_and_render(self, new_state: ProjectState) -> None:
        """状態を更新してUIを再描画する。

        Args:
            new_state: 新しいUI状態
        """
        old_state = self._state
        self._state = new_state

        # リスト更新（検索・フィルタ・並び替えが変更された場合）
        if (
            old_state.keyword != new_state.keyword
            or old_state.status != new_state.status
            or old_state.sort_key != new_state.sort_key
            or old_state.sort_desc != new_state.sort_desc
        ):
            self._update_list()

        # 詳細更新（選択が変更された場合）
        if old_state.selected_id != new_state.selected_id:
            self._update_detail()

    def _update_list(self) -> None:
        """プロジェクトリストを更新する。"""
        try:
            # データ取得
            if self._state.keyword:
                items = self._service.search(self._state.keyword, status=self._state.status)
            elif self._state.status is not None:
                items = self._service.list_by_status(self._state.status)
            else:
                items = self._service.get_all_projects()

            # 並び替え（ProjectReadのまま辞書化し、並び替えを適用）
            strategy = get_order_strategy(self._state.sort_key)
            ordered_items = apply_order(
                self._reads_to_presenter_dicts(items),
                strategy,
                desc=self._state.sort_desc,
            )

            # ViewModel変換（辞書経由でのレガシー互換性を維持）
            view_models = to_card_vm(ordered_items)

            # UI更新通知
            self._on_list_change(view_models)
            logger.debug(f"プロジェクトリスト更新: {len(view_models)}件")

        except Exception as e:
            logger.error(f"プロジェクトリスト更新エラー: {e}")
            self._on_list_change([])
            self._notify_error("プロジェクト一覧の取得に失敗しました。詳細はログを参照してください。")

    def _update_detail(self) -> None:
        """プロジェクト詳細を更新する。"""
        try:
            if not self._state.selected_id:
                # 選択なしの場合
                self._on_detail_change(None)
                logger.debug("プロジェクト詳細クリア")
                return

            # 選択されたプロジェクトを検索
            # TODO: ID 取得 API の利用
            # - list → 探索は暫定です。ProjectQuery に get_project_by_id を追加し、
            #   Repository で最適に取得してください。
            selected = None
            try:
                # ID 取得 API があれば利用
                if hasattr(self._service, "get_by_id"):
                    selected = self._service.get_by_id(UUID(self._state.selected_id))
            except Exception as e:
                logger.warning(f"get_by_id 失敗: {e}. 一覧から探索を継続")

            if selected is None:
                # フォールバック: 全件取得後に探索
                try:
                    all_items = self._service.get_all_projects()
                    for p in all_items:
                        if str(getattr(p, "id", "")) == self._state.selected_id:
                            selected = p
                            break
                except Exception as e:
                    logger.error(f"詳細取得用の一覧取得失敗: {e}")

            if selected is not None:
                # Presenter 互換の辞書へマッピング
                detail_vm = to_detail_vm(self._project_read_to_presenter_dict(selected))
                self._on_detail_change(detail_vm)
                logger.debug(f"プロジェクト詳細更新: {detail_vm.title}")
            else:
                logger.warning(f"選択されたプロジェクトが見つかりません: {self._state.selected_id}")
                self._on_detail_change(None)

        except Exception as e:
            # ログ出力（長文を分割して可読性と行長制限を両立）
            msg = f"プロジェクト詳細更新中にエラーが発生しました: project_id={self._state.selected_id}, error={e}"
            logger.exception(msg)
            # [AI GENERATED] ユーザーにエラー内容を通知
            user_msg = (
                f"プロジェクト詳細の取得中にエラーが発生しました（ID: {self._state.selected_id}）。"
                "詳細はログを参照してください。"
            )
            self._notify_error(user_msg)
            self._on_detail_change(None)

    # --- internal helpers -------------------------------------------------

    def _reads_to_presenter_dicts(self, items: list[ProjectRead]) -> list[dict[str, Any]]:
        """ProjectRead の配列を Presenter 互換の辞書リストへ正規化する。

        Note:
            Presenter は dict[str, str] を想定するため、文字列へ寄せる。
            進捗系は未集計のため 0 を設定する（将来 ApplicationService に統合）。
        """
        return [self._project_read_to_presenter_dict(p) for p in items]

    def _project_read_to_presenter_dict(self, p: ProjectRead) -> dict[str, str]:
        def _s(v: object | None) -> str:
            return "" if v is None else str(v)

        status_value = getattr(p, "status", None)
        status_text = _s(status_value)
        # Enum の場合は表示ラベルへ（ドメイン層のメソッドを使用）
        if isinstance(status_value, ProjectStatus):
            status_text = ProjectStatus.display_label(status_value)
        else:
            status_text = _s(status_value)

        # 関連タスクIDリストと完了数を取得
        project_id = getattr(p, "id", None)
        task_ids: list[str] = []
        completed_count = 0
        tasks_details: list[dict[str, str]] = []
        if project_id:
            try:
                from logic.application.task_application_service import TaskApplicationService
                from models import TaskStatus

                if not hasattr(self._apps, "get_service"):
                    return {}
                task_service = self._apps.get_service(TaskApplicationService)  # type: ignore[union-attr]
                all_tasks = task_service.get_all_tasks()
                # プロジェクトに関連するタスクをフィルタ
                related_tasks = [task for task in all_tasks if task.project_id == project_id]
                task_ids = [str(task.id) for task in related_tasks]
                # 完了タスクをカウント
                completed_count = sum(1 for task in related_tasks if task.status == TaskStatus.COMPLETED)
                # タスク詳細を作成
                tasks_details.extend(
                    [
                        {
                            "id": str(task.id),
                            "title": str(task.title),
                            "status": (
                                task.status.display_label()
                                if hasattr(task.status, "display_label")
                                else str(task.status)
                            ),
                            "is_completed": str(task.status == TaskStatus.COMPLETED),
                        }
                        for task in related_tasks
                    ]
                )
            except Exception as e:
                logger.warning(f"プロジェクト {project_id} の関連タスク取得エラー: {e}")

        return {
            "id": _s(getattr(p, "id", "")),
            "title": _s(getattr(p, "title", "")),
            "description": _s(getattr(p, "description", "")),
            "status": status_text,
            "created_at": _s(getattr(p, "created_at", "")),
            "updated_at": _s(getattr(p, "updated_at", "")),
            "due_date": _s(getattr(p, "due_date", "")),
            # 進捗系
            "task_count": str(len(task_ids)),
            "completed_count": str(completed_count),
            "task_id": task_ids,  # type: ignore[dict-item]
            "tasks": tasks_details,  # type: ignore[dict-item]
        }
