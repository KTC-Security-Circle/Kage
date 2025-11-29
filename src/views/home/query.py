"""Home Query Definitions.

【責務】
    ホーム画面のデータ取得を抽象化する。
    ControllerとDataSource間のインターフェースを明確化する。

    - デイリーレビュー情報の取得
    - Inboxメモの取得
    - 統計情報の取得

【責務外（他層の担当）】
    - UI表示 → View/Presenter
    - 状態保持 → State
    - 実際のデータ永続化 → ApplicationService/Repository

【設計上の特徴】
    - Protocolによる抽象化（依存性逆転）
    - テスト用のインメモリ実装を提供
    - 型安全なインターフェース定義

【アーキテクチャ上の位置づけ】
    Controller → HomeQuery (Protocol)
                    ↓
                InMemoryHomeQuery (実装)
                    ↓
                サンプルデータ
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from loguru import logger

from errors import NotFoundError
from models import (
    AiSuggestionStatus,
    MemoRead,
    MemoStatus,
    ProjectRead,
    ProjectStatus,
    TaskRead,
    TaskStatus,
)

if TYPE_CHECKING:
    from agents.task_agents.one_liner.state import OneLinerState


class MemoServicePort(Protocol):
    """MemoApplicationService互換のポート。"""

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        """メモを全件取得する。"""
        ...


class TaskServicePort(Protocol):
    """TaskApplicationService互換のポート。"""

    def get_all_tasks(self) -> list[TaskRead]:
        """タスクを全件取得する。"""
        ...


class ProjectServicePort(Protocol):
    """ProjectApplicationService互換のポート。"""

    def get_all_projects(self) -> list[ProjectRead]:
        """プロジェクトを全件取得する。"""
        ...


class OneLinerServicePort(Protocol):
    """OneLinerApplicationService互換のポート。"""

    def generate_one_liner(self, query: OneLinerState | None = None) -> str:
        """一言メッセージを生成する。"""
        ...


class HomeQuery(Protocol):
    """ホーム画面データ取得のポート。"""

    def get_daily_review(self) -> dict[str, Any]:
        """デイリーレビュー情報を取得する。

        Returns:
            デイリーレビュー情報を含む辞書
        """
        ...

    def get_inbox_memos(self) -> list[dict[str, Any]]:
        """Inboxメモを取得する。

        Returns:
            Inboxメモのリスト
        """
        ...

    def get_stats(self) -> dict[str, int]:
        """統計情報を取得する。

        Returns:
            統計情報を含む辞書
        """
        ...

    def get_one_liner_message(self) -> str | None:
        """AI一言メッセージのみを生成する。

        Returns:
            生成されたメッセージ（失敗時はNone）
        """
        ...


class InMemoryHomeQuery:
    """軽量なデフォルト実装。テスト・プロトタイピング用。"""

    def __init__(
        self,
        daily_review: dict[str, Any] | None = None,
        inbox_memos: list[dict[str, Any]] | None = None,
        stats: dict[str, int] | None = None,
    ) -> None:
        """InMemoryHomeQueryを初期化する。

        Args:
            daily_review: デイリーレビュー情報
            inbox_memos: Inboxメモのリスト
            stats: 統計情報
        """
        self._daily_review = dict(daily_review) if daily_review else {}
        self._inbox_memos = list(inbox_memos) if inbox_memos else []
        self._stats = dict(stats) if stats else {}

    def get_daily_review(self) -> dict[str, Any]:
        """デイリーレビュー情報を取得する。

        Returns:
            デイリーレビュー情報を含む辞書
        """
        return self._daily_review

    def get_inbox_memos(self) -> list[dict[str, Any]]:
        """Inboxメモを取得する。

        Returns:
            Inboxメモのリスト
        """
        return self._inbox_memos

    def get_stats(self) -> dict[str, int]:
        """統計情報を取得する。

        Returns:
            統計情報を含む辞書
        """
        return self._stats

    def get_one_liner_message(self) -> str | None:
        """AI一言メッセージのみを生成する（InMemory実装では常にNone）。

        Returns:
            None（テスト用実装のため）
        """
        return None


@dataclass(slots=True)
class ApplicationHomeQuery(HomeQuery):
    """ApplicationServiceを経由して実データを取得するQuery実装。

    このクラスは、各Application Serviceからデータを取得し、
    ホーム画面で必要な形式に変換して提供します。
    パフォーマンスのため、取得したデータは内部でキャッシュされます。

    Attributes:
        memo_service: メモデータ取得用サービス
        task_service: タスクデータ取得用サービス
        project_service: プロジェクトデータ取得用サービス
        one_liner_service: 一言メッセージ生成用サービス
        max_inbox_items: Inboxメモの最大表示件数
    """

    memo_service: MemoServicePort
    task_service: TaskServicePort
    project_service: ProjectServicePort
    one_liner_service: OneLinerServicePort
    max_inbox_items: int = 20
    _memo_cache: list[MemoRead] | None = field(default=None, init=False, repr=False)
    _task_cache: list[TaskRead] | None = field(default=None, init=False, repr=False)
    _project_cache: list[ProjectRead] | None = field(default=None, init=False, repr=False)

    def get_daily_review(self) -> dict[str, Any]:
        """タスクとメモの状況を基にデイリーレビューを生成する（AI一言なし）。"""
        return self._build_daily_review(self._get_tasks(), self._get_memos())

    def get_one_liner_message(self) -> str | None:
        """AI一言メッセージのみを生成する。

        Returns:
            生成されたメッセージ（失敗時はNone）
        """
        return self._generate_one_liner_message()

    def get_inbox_memos(self) -> list[dict[str, Any]]:
        """Inboxステータスのメモを最新順で返す。"""
        inbox_candidates = (memo for memo in self._get_memos() if memo.status == MemoStatus.INBOX)
        inbox_memos = sorted(inbox_candidates, key=self._memo_sort_key, reverse=True)
        return [self._memo_to_dict(memo) for memo in inbox_memos[: self.max_inbox_items]]

    def get_stats(self) -> dict[str, int]:
        """タスク・プロジェクトの集計値を返す。"""
        tasks = self._get_tasks()
        projects = self._get_projects()
        return {
            "todays_tasks": sum(1 for task in tasks if task.status == TaskStatus.TODAYS),
            "todo_tasks": sum(1 for task in tasks if task.status == TaskStatus.TODO),
            "active_projects": sum(1 for project in projects if project.status == ProjectStatus.ACTIVE),
        }

    def _get_memos(self) -> list[MemoRead]:
        if self._memo_cache is None:
            try:
                self._memo_cache = self.memo_service.get_all_memos(with_details=True)
            except NotFoundError as e:
                # メモが存在しない場合は空リストで扱う（UIではエラーにしない）
                logger.info("No memos found in MemoService: {}", e)
                logging.getLogger(__name__).info("No memos found")
                self._memo_cache = []
        return self._memo_cache

    def _get_tasks(self) -> list[TaskRead]:
        if self._task_cache is None:
            try:
                self._task_cache = self.task_service.get_all_tasks()
            except NotFoundError as e:
                # タスクが存在しない場合は空リストで扱う
                logger.info("No tasks found in TaskService: {}", e)
                logging.getLogger(__name__).info("No tasks found")
                self._task_cache = []
        return self._task_cache

    def _get_projects(self) -> list[ProjectRead]:
        if self._project_cache is None:
            try:
                self._project_cache = self.project_service.get_all_projects()
            except NotFoundError as e:
                logger.info("No projects found in ProjectService: {}", e)
                logging.getLogger(__name__).info("No projects found")
                self._project_cache = []
        return self._project_cache

    def _memo_to_dict(self, memo: MemoRead) -> dict[str, Any]:
        ai_status = memo.ai_suggestion_status or AiSuggestionStatus.NOT_REQUESTED
        return {
            "id": str(memo.id) if memo.id is not None else "",
            "title": memo.title or "",
            "content": memo.content or "",
            "ai_suggestion_status": ai_status.value,
        }

    def _memo_sort_key(self, memo: MemoRead) -> float:
        created_at = memo.created_at
        if created_at is None:
            return float("-inf")
        return created_at.timestamp()

    def _build_daily_review(self, tasks: list[TaskRead], memos: list[MemoRead]) -> dict[str, Any]:
        # タスクリストを複数回走査するのではなく、単一パスで分類する。
        # 理由: 大きなタスクリストでの効率化（O(n)）と可読性向上のため。
        todays_tasks: list[TaskRead] = []
        todo_tasks: list[TaskRead] = []
        progress_tasks: list[TaskRead] = []
        overdue_tasks: list[TaskRead] = []
        completed_tasks: list[TaskRead] = []

        for task in tasks:
            status = task.status
            if status == TaskStatus.TODAYS:
                todays_tasks.append(task)
            elif status == TaskStatus.TODO:
                todo_tasks.append(task)
            elif status == TaskStatus.PROGRESS:
                progress_tasks.append(task)
            elif status == TaskStatus.OVERDUE:
                overdue_tasks.append(task)
            elif status == TaskStatus.COMPLETED:
                completed_tasks.append(task)

        # メモのInbox抽出は単純なフィルタでよい（メモは通常少数）
        inbox_memos = [memo for memo in memos if memo.status == MemoStatus.INBOX]
        return self._select_review_scenario(
            todays_tasks=todays_tasks,
            todo_tasks=todo_tasks,
            progress_tasks=progress_tasks,
            overdue_tasks=overdue_tasks,
            completed_tasks=completed_tasks,
            inbox_memos=inbox_memos,
        )

    def _select_review_scenario(
        self,
        *,
        todays_tasks: list[TaskRead],
        todo_tasks: list[TaskRead],
        progress_tasks: list[TaskRead],
        overdue_tasks: list[TaskRead],
        completed_tasks: list[TaskRead],
        inbox_memos: list[MemoRead],
    ) -> dict[str, Any]:
        """デイリーレビュー表示用のシナリオを判定して返す。

        Args:
            todays_tasks: 今日のタスク一覧
            todo_tasks: TODO 状態のタスク一覧
            progress_tasks: 進行中のタスク一覧
            overdue_tasks: 期限超過のタスク一覧
            completed_tasks: 完了済みタスク一覧
            inbox_memos: Inbox のメモ一覧

        Returns:
            選択されたシナリオのデータ辞書
        """
        review_scenarios = [
            (
                bool(overdue_tasks),
                {
                    "icon": "error",
                    "color": "amber",
                    "message": f"{len(overdue_tasks)}件の期限超過タスクがあります。優先的に対処しましょう。",
                    "action_text": "期限超過のタスクを確認",
                    "action_route": "/tasks",
                    "priority": "high",
                },
            ),
            (
                not todays_tasks and bool(todo_tasks),
                {
                    "icon": "coffee",
                    "color": "blue",
                    "message": (
                        f"今日のタスクがまだ設定されていません。{len(todo_tasks)}件のTODOから選んで始めましょう！"
                    ),
                    "action_text": "タスクを設定する",
                    "action_route": "/tasks",
                    "priority": "medium",
                },
            ),
            (
                bool(todays_tasks) and not progress_tasks,
                {
                    "icon": "play_arrow",
                    "color": "green",
                    "message": f"{len(todays_tasks)}件のタスクが待っています。さあ、最初の一歩を踏み出しましょう！",
                    "action_text": "タスクを開始する",
                    "action_route": "/tasks",
                    "priority": "medium",
                },
            ),
            (
                bool(progress_tasks),
                {
                    "icon": "trending_up",
                    "color": "primary",
                    "message": f"{len(progress_tasks)}件のタスクが進行中です。良いペースです、その調子で続けましょう！",
                    "action_text": "進行中のタスクを見る",
                    "action_route": "/tasks",
                    "priority": "normal",
                },
            ),
            (
                bool(inbox_memos),
                {
                    "icon": "lightbulb",
                    "color": "purple",
                    "message": f"{len(inbox_memos)}件のInboxメモがあります。AIにタスクを生成させて整理しましょう。",
                    "action_text": "メモを整理する",
                    "action_route": "/memos",
                    "priority": "medium",
                },
            ),
            (
                bool(completed_tasks) and not todays_tasks,
                {
                    "icon": "check_circle",
                    "color": "green",
                    "message": "素晴らしい！全てのタスクが完了しています。新しいメモを書いて次の目標を設定しましょう。",
                    "action_text": "新しいメモを作成",
                    "action_route": "/memos",
                    "priority": "low",
                },
            ),
        ]

        selected: dict[str, Any] | None = None
        for condition, data in review_scenarios:
            if condition:
                selected = data
                break

        if selected is None:
            selected = {
                "icon": "wb_sunny",
                "color": "primary",
                "message": "今日も良い一日にしましょう。まずはメモを書いて、やるべきことを整理しませんか?",
                "action_text": "メモを作成する",
                "action_route": "/memos",
                "priority": "low",
            }

        # AI一言は非同期で生成されるため、ここでは含めない
        return selected

    def _generate_one_liner_message(self) -> str | None:
        try:
            return self.one_liner_service.generate_one_liner()
        except Exception:
            return None
