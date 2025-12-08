"""Tasks Presenter.

Domain(dict) から UI 表示用 ViewModel への変換を担う。

提供する ViewModel:
- TaskCardVM: 一覧カード表示用の最小VM
- TaskDetailVM: 右ペイン詳細表示用の拡張VM
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # 型注釈専用
    from collections.abc import Iterable


@dataclass(frozen=True)
class TaskCardVM:
    """タスクカード表示用の最小 ViewModel。

    既存テスト互換のため `id`, `title`, `subtitle` は維持し、
    デザイン整合のため `description`, `status` を追加する。
    """

    id: str
    title: str
    subtitle: str
    description: str = ""
    status: str = ""
    tags: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.tags is None:
            object.__setattr__(self, "tags", [])


@dataclass(frozen=True)
class RelatedTaskVM:
    """関連タスク表示用のViewModel。

    Attributes:
        id: タスクID
        title: タスクタイトル
        status: ステータス表示用文字列
        is_completed: 完了フラグ
    """

    id: str
    title: str
    status: str
    is_completed: bool


@dataclass(frozen=True)
class TaskDetailVM:
    """タスク詳細表示用 ViewModel。

    一覧よりもリッチな情報を保持する。必須は一覧と同等、追加は任意。

    Attributes:
        id: タスクID
        title: タイトル
        description: 説明
        status: ステータス（string）
        subtitle: 補助表示用のサブタイトル（例: 更新日）
        due_date: 期限日（文字列、未設定は None）
        completed_at: 完了日時（文字列、未設定は None）
        project_id: プロジェクトID（文字列、未設定は None）
        project_name: プロジェクト名（文字列、未設定は None）
        project_status: プロジェクトステータス（文字列、未設定は None）
        memo_id: メモID（文字列、未設定は None）
        is_recurring: 繰り返しタスクフラグ（未設定は False）
        recurrence_rule: RRULE形式などの繰り返しルール（未設定は None）
        created_at: 作成日（文字列、未設定は None）
        updated_at: 更新日（文字列、未設定は None）
        tags: タグ名のリスト（未設定は空リスト）
    """

    id: str
    title: str
    description: str
    status: str
    subtitle: str = ""
    due_date: str | None = None
    completed_at: str | None = None
    project_id: str | None = None
    project_name: str | None = None
    project_status: str | None = None
    project_tasks: list[RelatedTaskVM] = None  # type: ignore[assignment]
    memo_id: str | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    tags: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.project_tasks is None:
            object.__setattr__(self, "project_tasks", [])
        if self.tags is None:
            object.__setattr__(self, "tags", [])


# TODO: 日付/時刻の整形 (subtitle のローカライズ) を集中管理するヘルパーを導入する。
# TODO: パフォーマンス観点で to_card_vm はジェネレータやバッチ変換最適化を検討 (大量件数時)。


def to_card_vm(items: Iterable[dict]) -> list[TaskCardVM]:
    """辞書タスクを TaskCardVM に変換する。

    Args:
        items: タスク辞書イテラブル
    Returns:
        TaskCardVM リスト
    """
    result = []
    for x in items:
        tags_data = x.get("tags", [])
        if not isinstance(tags_data, list):
            tags_data = []
        tags = [str(tag) for tag in tags_data]

        result.append(
            TaskCardVM(
                id=str(x.get("id")),
                title=str(x.get("title", "(無題)")),
                subtitle=str(x.get("updated_at", "")),
                description=str(x.get("description", "")),
                status=str(x.get("status", "")),
                tags=tags,
            )
        )
    return result


def to_detail_vm(item: dict) -> TaskDetailVM:
    """辞書タスクを TaskDetailVM に変換する。

    Args:
        item: タスク辞書
    Returns:
        TaskDetailVM
    """
    # 関連タスクを変換
    project_tasks_data = item.get("project_tasks", [])
    if not isinstance(project_tasks_data, list):
        project_tasks_data = []

    project_tasks = [
        RelatedTaskVM(
            id=str(task.get("id", "")),
            title=str(task.get("title", "無題のタスク")),
            status=str(task.get("status", "")),
            is_completed=task.get("is_completed", "False") in ("True", "true", "1"),
        )
        for task in project_tasks_data
    ]

    # タグを抽出
    tags_data = item.get("tags", [])
    if not isinstance(tags_data, list):
        tags_data = []
    tags = [str(tag) for tag in tags_data]

    return TaskDetailVM(
        id=str(item.get("id")),
        title=str(item.get("title", "(無題)")),
        description=str(item.get("description", "")),
        status=str(item.get("status", "")),
        subtitle=str(item.get("updated_at", "")),
        due_date=str(item.get("due_date")) if item.get("due_date") is not None else None,
        completed_at=str(item.get("completed_at")) if item.get("completed_at") is not None else None,
        project_id=str(item.get("project_id")) if item.get("project_id") is not None else None,
        project_name=str(item.get("project_name")) if item.get("project_name") else None,
        project_status=str(item.get("project_status")) if item.get("project_status") else None,
        project_tasks=project_tasks,
        memo_id=str(item.get("memo_id")) if item.get("memo_id") is not None else None,
        is_recurring=bool(item.get("is_recurring", False)),
        recurrence_rule=str(item.get("recurrence_rule")) if item.get("recurrence_rule") is not None else None,
        created_at=str(item.get("created_at")) if item.get("created_at") is not None else None,
        updated_at=str(item.get("updated_at")) if item.get("updated_at") is not None else None,
        tags=tags,
    )


def to_detail_from_card(vm: TaskCardVM) -> TaskDetailVM:
    """TaskCardVM から TaskDetailVM を生成する。

    一覧で保持していない情報は None/空文字で補完する。

    Args:
        vm: 一覧表示用VM
    Returns:
        TaskDetailVM
    """
    return TaskDetailVM(
        id=vm.id,
        title=vm.title,
        description=vm.description,
        status=vm.status,
        subtitle=vm.subtitle,
        due_date=None,
        completed_at=None,
        project_id=None,
        project_name=None,
        project_status=None,
        project_tasks=[],
        memo_id=None,
        is_recurring=False,
        recurrence_rule=None,
        created_at=None,
        updated_at=None,
        tags=[],
    )


# TODO: View/Persistence 層からの属性差異を吸収する Mapper 層を検討。
#       例: DBのカラム名とViewModelのプロパティ名の差異 (updatedAt vs updated_at)。
