"""Tasks Controller.

View と Query/Ordering/Presenter を調停し状態を不変更新する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from loguru import logger

if TYPE_CHECKING:  # 型チェック専用
    from collections.abc import Callable
    from uuid import UUID

    from models import TaskRead, TaskStatus, TaskUpdate

from .components.shared.constants import STATUS_ORDER
from .ordering import ORDERING_MAP, apply_order
from .presenter import TaskCardVM, to_card_vm
from .state import TasksState


class TaskApplicationPort(Protocol):
    """TaskApplicationService への依存を抽象化するポート。

    View/Controller はこの Protocol のみを前提にし、具体的な取得方法や
    UnitOfWork/Repository には依存しない。テストではモックを注入可能。
    """

    def get_all_tasks(self) -> list[TaskRead]:  # pragma: no cover - interface
        """全タスク取得"""
        ...

    def get_by_id(
        self, task_id: UUID, *, with_details: bool = False
    ) -> TaskRead | None:  # pragma: no cover - interface
        """ID で単一取得。見つからない場合 None。"""
        ...

    def search(
        self,
        query: str,
        *,
        with_details: bool = False,
        status: TaskStatus | None = None,
    ) -> list[TaskRead]:  # pragma: no cover - interface
        """検索（任意でステータスフィルタ）。"""
        ...

    def list_by_status(
        self, status: TaskStatus, *, with_details: bool = False
    ) -> list[TaskRead]:  # pragma: no cover - interface
        """ステータス別一覧取得。"""
        ...

    def create(
        self,
        title: str,
        description: str | None = None,
        *,
        status: TaskStatus | None = None,
    ) -> TaskRead:  # pragma: no cover - interface
        """タスク作成。"""
        ...

    def update(self, task_id: UUID, update_data: TaskUpdate) -> TaskRead:  # pragma: no cover - interface
        """タスク更新。"""
        ...

    def delete(self, task_id: UUID) -> bool:  # pragma: no cover - interface
        """タスク削除。"""
        ...


class TasksController:
    """TasksView 用の調停役 Controller。

    - Port 経由で ApplicationService を呼び出し、一覧/詳細/検索/並び替えを行う
    - 不変 `TasksState` を生成し UI 更新をコールバックで通知
    - 例外発生時はユーザー通知ハンドラ経由で UI レイヤに委譲
    """

    def __init__(
        self,
        service: TaskApplicationPort,
        on_change: Callable[[list[TaskCardVM]], None],
        on_error: Callable[[str], None] | None = None,
        apps: object | None = None,
    ) -> None:
        """Controller 初期化。

        Args:
            service: TaskApplicationPort 実装(ApplicationService を抽象化)
            on_change: 一覧 VM 更新時コールバック
            on_error: ユーザー通知用エラーハンドラ(SnackBar 等)
            apps: ApplicationService コンテナ
        """
        self._service = service
        self._state = TasksState()
        self._on_change = on_change
        self._on_error = on_error
        self._apps = apps
        # キャッシュ: 現在のキーワードでフィルタされた全タスクを保持
        self._cached_tasks: list[TaskRead] | None = None
        self._cached_keyword: str = ""

    def _notify_error(self, message: str) -> None:
        """UI 層へエラー通知(存在すれば)。"""
        logger.error(message)
        if self._on_error:
            self._on_error(message)

    @property
    def state(self) -> TasksState:
        """現在の状態を返す。"""
        return self._state

    # --- Public Events ---
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
                from models import TaskStatus

                status_filter = TaskStatus(status)
            except ValueError:
                logger.debug(f"未知のステータス入力を全件扱いに変換: {status}")
                status_filter = None

        logger.debug(f"ステータスフィルタ設定: {status_filter}")
        new_state = self._state.update(status=status)
        self._update_and_render(new_state)

    def set_sort(self, key: str, *, descending: bool) -> None:
        """ソート条件を更新する。

        Args:
            key: ソートキー
            descending: 降順にするか
        """
        logger.debug(f"並び替え設定: key={key}, desc={descending}")
        self._update_and_render(self._state.update(sort_key=key, sort_desc=descending))

    def refresh(self) -> None:
        """外部からの再読み込み要求。キャッシュを無効化して最新データを取得する。"""
        logger.debug("データ再読み込み: キャッシュをクリアして一覧を再描画")
        self._invalidate_cache()
        self._update_and_render(self._state)

    def _invalidate_cache(self) -> None:
        """キャッシュを無効化する。タスクの作成・更新・削除時に呼び出す。"""
        self._cached_tasks = None
        self._cached_keyword = ""

    def set_selected(self, task_id: str | None) -> None:
        """選択中のタスクIDを更新する。"""
        logger.debug(f"タスク選択: {task_id}")
        self._update_and_render(self._state.update(selected_id=task_id))

    def change_task_status(self, task_id: str, new_status: str) -> None:
        """タスクのステータスを変更し再描画する。

        Args:
            task_id: 変更対象ID
            new_status: 新ステータス
        """
        from uuid import UUID

        from models import TaskStatus, TaskUpdate

        try:
            tid = UUID(task_id)
            status_enum = TaskStatus(new_status)
            update_data = TaskUpdate(status=status_enum)
            self._service.update(tid, update_data)
            logger.debug("Changed task status id={} -> {}", task_id, new_status)
            # ステータス変更後はキャッシュを無効化
            self._invalidate_cache()
        except (ValueError, Exception) as e:
            logger.error(f"Failed to change task status: {e}")
            self._notify_error("タスクのステータス変更に失敗しました。")
        finally:
            # 反映
            self._update_and_render(self._state)

    def create_task(
        self,
        title: str,
        description: str | None = None,
        status: str | None = None,
    ) -> None:
        """新規タスクを ApplicationService 経由で作成する。

        Args:
            title: タスクタイトル
            description: タスクの説明
            status: タスクのステータス
        """
        from models import TaskStatus

        # タイトルのバリデーション
        title = title.strip()
        if not title:
            self._notify_error("タイトルを入力してください。")
            return

        # ステータスの変換
        status_enum = None
        if status and status.strip():
            try:
                status_enum = TaskStatus(status)
            except ValueError:
                # 未知のステータスはデフォルト(None)
                logger.debug(f"未知のステータス入力: {status}")
                status_enum = None

        try:
            # ApplicationService経由でタスク作成
            created = self._service.create(
                title=title,
                description=description,
                status=status_enum,
            )
            logger.info(f"タスク作成完了: {created.title}")

            # キャッシュを無効化して一覧を更新
            self._invalidate_cache()
            self._update_and_render(self._state)

        except Exception as e:
            logger.exception(f"タスク作成中にエラー: {e}")
            self._notify_error("タスクの作成に失敗しました。詳細はログを参照してください。")

    # TODO: MVC整備後は Command/ApplicationService 層へ書き込み操作を委譲する。
    #       例: TaskApplicationService.change_status(cmd) にトランザクション管理/ドメイン検証を移管。
    # TODO: 検索入力は debounce / throttle を導入し過剰な再描画を抑制。
    # TODO: _update_and_render の失敗時にユーザー通知 (トースト/ダイアログ) を発火するエラーハンドリングを追加。

    # --- Query helpers for View ---
    def get_counts(self) -> dict[str, int]:
        """現在のキーワードフィルタでのステータス別件数を返す。

        キャッシュされたタスク一覧から集計するため、追加のDB クエリは発生しない。
        """
        from models import TaskStatus

        # キャッシュが無効な場合は全タスクを取得
        if self._cached_tasks is None or self._cached_keyword != self._state.keyword:
            try:
                self._cached_tasks = self._service.search(
                    self._state.keyword,
                    with_details=False,
                    status=None,
                )
                self._cached_keyword = self._state.keyword
            except Exception:
                self._cached_tasks = []

        # キャッシュからステータス別に集計
        counts: dict[str, int] = {}
        for status in STATUS_ORDER:
            try:
                status_enum = TaskStatus(status) if status else None
                if status_enum:
                    counts[status] = sum(
                        1 for task in self._cached_tasks if task.status == status_enum
                    )
                else:
                    counts[status] = len(self._cached_tasks)
            except Exception:
                counts[status] = 0
        return counts

    def get_total_count(self) -> int:
        """現在のキーワードでの総件数。

        キャッシュされたタスク一覧から件数を返すため、追加のDB クエリは発生しない。
        """
        # キャッシュが無効な場合は全タスクを取得
        if self._cached_tasks is None or self._cached_keyword != self._state.keyword:
            try:
                self._cached_tasks = self._service.search(
                    self._state.keyword,
                    with_details=False,
                    status=None,
                )
                self._cached_keyword = self._state.keyword
            except Exception:
                self._cached_tasks = []

        return len(self._cached_tasks)

    def get_detail(self, task_id: str) -> dict | None:
        """タスクIDから詳細データを取得する。

        Args:
            task_id: タスクID

        Returns:
            タスク詳細の辞書、見つからない場合はNone
        """
        from uuid import UUID

        try:
            task_uuid = UUID(task_id)
            task = self._service.get_by_id(task_uuid, with_details=True)
            if task:
                return self._task_read_to_dict(task)
        except Exception as e:
            logger.error(f"タスク詳細取得エラー: task_id={task_id}, error={e}")
        return None

    # --- Internal orchestration ---
    def _update_and_render(self, new_state: TasksState) -> None:
        """状態を更新してUIを再描画する。

        Args:
            new_state: 新しいUI状態
        """
        self._state = new_state
        try:
            # キャッシュの更新判定
            keyword_changed = self._cached_keyword != new_state.keyword

            # キーワードが変わった場合のみDBから取得し、キャッシュを更新
            if keyword_changed or self._cached_tasks is None:
                from models import TaskStatus

                self._cached_tasks = self._service.search(
                    new_state.keyword,
                    with_details=False,
                    status=None,
                )
                self._cached_keyword = new_state.keyword

            # キャッシュからステータスフィルタを適用
            from models import TaskStatus

            status_enum = TaskStatus(new_state.status) if new_state.status else None
            if status_enum:
                items = [task for task in self._cached_tasks if task.status == status_enum]
            else:
                items = self._cached_tasks

            # 辞書化してPresenterへ
            items_dict = [self._task_read_to_dict(item) for item in items]

            # 並び替え
            strategy = ORDERING_MAP[new_state.sort_key]
            ordered = apply_order(items_dict, strategy, descending=new_state.sort_desc)
            vm: list[TaskCardVM] = to_card_vm(ordered)

            logger.debug(
                "Render tasks count={} keyword='{}' status={} sort={} desc={}",
                len(vm),
                new_state.keyword,
                new_state.status,
                new_state.sort_key,
                new_state.sort_desc,
            )
            self._on_change(vm)
        except Exception as e:
            logger.error(f"タスク一覧更新エラー: {e}")
            self._on_change([])
            self._notify_error("タスク一覧の取得に失敗しました。詳細はログを参照してください。")

    def _task_read_to_dict(self, task: TaskRead) -> dict:
        """TaskRead を辞書形式に変換する。

        Args:
            task: TaskRead インスタンス

        Returns:
            タスク情報の辞書
        """

        def _s(v: object | None) -> str:
            return "" if v is None else str(v)

        # プロジェクト情報と関連タスクを取得
        project_name: str | None = None
        project_status: str | None = None
        project_tasks: list[dict[str, str]] = []
        if task.project_id:
            try:
                from uuid import UUID

                from logic.application.project_application_service import ProjectApplicationService
                from models import TaskStatus

                if hasattr(self._apps, "get_service"):
                    project_service = self._apps.get_service(ProjectApplicationService)  # type: ignore[union-attr]
                    project = project_service.get_by_id(UUID(str(task.project_id)))
                    if project:
                        from models import ProjectStatus

                        project_name = str(project.title)
                        project_status = ProjectStatus.display_label(project.status)

                        # 同じプロジェクトに属する他のタスクを取得
                        all_tasks = self._service.get_all_tasks()
                        from views.tasks.components.shared.constants import TASK_STATUS_LABELS

                        project_tasks.extend(
                            [
                                {
                                    "id": str(other_task.id),
                                    "title": str(other_task.title),
                                    "status": TASK_STATUS_LABELS.get(
                                        other_task.status.value if other_task.status else "",
                                        str(other_task.status) if other_task.status else "",
                                    ),
                                    "is_completed": str(other_task.status == TaskStatus.COMPLETED),
                                }
                                for other_task in all_tasks
                                if (other_task.project_id == task.project_id and str(other_task.id) != str(task.id))
                            ]
                        )
                        logger.debug(
                            f"タスク {task.id} のプロジェクト関連タスク取得: "
                            f"project_id={task.project_id}, 関連タスク数={len(project_tasks)}"
                        )
            except Exception as e:
                logger.warning(f"タスク {task.id} のプロジェクト情報取得エラー: {e}")

        return {
            "id": _s(task.id),
            "title": _s(task.title),
            "description": _s(task.description),
            "status": _s(task.status.value if task.status else ""),
            "due_date": _s(task.due_date),
            "created_at": _s(task.created_at),
            "updated_at": _s(task.updated_at),
            "completed_at": _s(task.completed_at),
            "project_id": _s(task.project_id),
            "project_name": project_name or "",
            "project_status": project_status or "",
            "project_tasks": project_tasks,  # type: ignore[dict-item]
        }
        # TODO: ここでリカバリアクション (再試行/フォールバック) を検討し、View へユーザー向け通知を行う。

    def update_task(
        self,
        task_id: str,
        title: str,
        description: str | None = None,
        status: str | None = None,
        due_date: str | None = None,
    ) -> None:
        """タスクを更新する。

        Args:
            task_id: タスクID
            title: タスクタイトル
            description: タスク説明
            status: タスクステータス
            due_date: 期限日（YYYY-MM-DD形式）

        Raises:
            ValueError: タスクIDが不正な場合
        """
        from uuid import UUID

        from models import TaskStatus, TaskUpdate

        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            logger.error(f"Invalid task_id: {task_id}")
            self._notify_error("タスクIDが不正です。")
            msg = f"Invalid task_id: {task_id}"
            raise ValueError(msg) from e

        # TaskUpdate を構築
        from datetime import date as date_type

        due_date_parsed: date_type | None = None
        if due_date:
            try:
                due_date_parsed = date_type.fromisoformat(due_date)
            except ValueError:
                logger.warning(f"Invalid due_date format: {due_date}")
                self._notify_error("期限日の形式が不正です。")
                return

        update_data = TaskUpdate(
            title=title,
            description=description,
            status=TaskStatus(status) if status else None,
            due_date=due_date_parsed,
        )

        try:
            # ApplicationServiceのupdateメソッドを使用
            self._service.update(task_uuid, update_data)
            logger.info(f"Task updated: {task_id}")
            # 更新後に一覧を再取得
            self.refresh()
        except Exception as e:
            logger.exception(f"タスク更新エラー: task_id={task_id}, error={e}")
            self._notify_error("タスクの更新に失敗しました。")
            raise
