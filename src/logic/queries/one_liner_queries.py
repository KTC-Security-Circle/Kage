"""一言コメント関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from logic.queries.task_queries import GetTodayTasksCountQuery  # [AI GENERATED] 今日件数クエリ
from settings.manager import get_config_manager  # [AI GENERATED] user_name 取得用


@dataclass
class OneLinerContext:
    """一言コメント生成のためのコンテキスト情報

    将来の拡張性を考慮し、当日のタスク数、期限超過数、進捗サマリ等の
    情報を含められるような構造として設計されています。
    現在は最小実装として空の状態でも動作します。
    """

    # 基本的なタスク情報
    today_task_count: int = 0
    """今日のタスク数"""

    overdue_task_count: int = 0
    """期限超過タスク数"""

    completed_task_count: int = 0
    """完了済みタスク数"""

    # 将来の拡張用フィールド（現在は未使用）
    progress_summary: str = ""
    """進捗サマリ（将来実装予定）"""

    user_name: str = ""
    """ユーザー名（将来実装予定）"""


def build_one_liner_context(
    today_task_count: int = 0,
    overdue_task_count: int = 0,
    completed_task_count: int = 0,
    progress_summary: str = "",
    user_name: str | None = None,
) -> OneLinerContext:
    """設定から user_name を補完して OneLinerContext を構築するユーティリティ。

    Args:
        today_task_count: 今日のタスク数
        overdue_task_count: 期限超過タスク数
        completed_task_count: 完了済みタスク数
        progress_summary: 追加進捗サマリ
        user_name: 明示指定されたユーザー名 (None の場合は設定値を使用)

    Returns:
        OneLinerContext: コンテキスト
    """
    # [AI GENERATED] 設定値から user_name を取得 (空文字ならそのまま)
    if user_name is None:
        try:
            user_name = get_config_manager().settings.user.user_name
        except Exception:  # pragma: no cover - 設定取得異常は匿名扱い
            user_name = ""
    return OneLinerContext(
        today_task_count=today_task_count,
        overdue_task_count=overdue_task_count,
        completed_task_count=completed_task_count,
        progress_summary=progress_summary,
        user_name=user_name or "",
    )


__all__ = ["OneLinerContext", "build_one_liner_context"]


# === 自動集計ビルダー ===
if TYPE_CHECKING:  # [AI GENERATED] 実行時不要の型のみ
    from collections.abc import Callable


class _TaskMetricsProvider(Protocol):  # [AI GENERATED] 型安全のためのProtocol
    def get_today_tasks_count(self, query: GetTodayTasksCountQuery) -> int: ...  # [AI GENERATED] interface
    def get_completed_tasks_count(self) -> int: ...  # [AI GENERATED] interface
    def get_overdue_tasks_count(self) -> int: ...  # [AI GENERATED] interface


def build_one_liner_context_auto(
    *,
    task_app_service_factory: Callable[[], _TaskMetricsProvider] | None = None,
    user_name: str | None = None,
) -> OneLinerContext:
    """タスク情報をアプリケーションサービス経由で自動集計して `OneLinerContext` を構築する。

    UI 側で個別カウントを渡す必要を無くし、バックエンドの一貫した集計ロジックを利用します。

    Args:
        task_app_service_factory: TaskApplicationService を生成するファクトリ（テスト差し替え用）
        user_name: 明示指定ユーザー名（未指定時は設定から取得）

    Returns:
        OneLinerContext: 集計済みコンテキスト
    """
    # [AI GENERATED] 依存解決（デフォルトは実運用用 UoW ベースのサービス生成）
    if task_app_service_factory is None:

        def _default_factory() -> _TaskMetricsProvider:  # [AI GENERATED] closure で遅延生成
            from logic.application.task_application_service import TaskApplicationService
            from logic.unit_of_work import SqlModelUnitOfWork

            return TaskApplicationService(SqlModelUnitOfWork)

        task_app_service_factory = _default_factory

    # 遅延 import で循環依存回避
    service = task_app_service_factory()

    # [AI GENERATED] 今日 / 完了 / 期限超過 タスク件数 (Application Service 公開API)
    today_count = service.get_today_tasks_count(GetTodayTasksCountQuery())
    # 型チェック防止: Protocol 拡張前に getattr fallback
    completed_count = service.get_completed_tasks_count()
    overdue_count = service.get_overdue_tasks_count()

    return build_one_liner_context(
        today_task_count=today_count,
        overdue_task_count=overdue_count,
        completed_task_count=completed_count,
        progress_summary="",  # TODO: まだ算出ロジックなし
        user_name=user_name,
    )


__all__ += ["build_one_liner_context_auto"]
