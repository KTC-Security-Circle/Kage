"""プロジェクト画面のプレゼンテーション層

Domain Model から Presentation Model への変換ロジックを提供。
UI に必要な形式でデータを整形し、表示ロジックを分離する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class ProjectCardVM:
    """プロジェクトカード表示用のViewModel。

    UI での表示に最適化されたプロジェクト情報を保持。
    不変オブジェクトとして設計し、安全な状態管理を実現する。

    Attributes:
        id: プロジェクトID
        title: プロジェクトタイトル
        subtitle: サブタイトル（作成日や更新日）
        description: プロジェクト説明（省略形）
        status: ステータス表示用文字列
        status_color: ステータス色
        progress_text: 進捗表示用テキスト
        progress_value: 進捗値（0.0-1.0）
        task_count: タスク総数
        completed_count: 完了タスク数
    """

    id: str
    title: str
    subtitle: str
    description: str
    status: str
    status_color: str
    progress_text: str
    progress_value: float
    task_count: int
    completed_count: int


@dataclass(frozen=True)
class ProjectDetailVM:
    """プロジェクト詳細表示用のViewModel。

    詳細画面での表示に最適化されたプロジェクト情報を保持。

    Attributes:
        id: プロジェクトID
        title: プロジェクトタイトル
        description: 完全なプロジェクト説明
        status: ステータス表示用文字列
        status_color: ステータス色
        created_at: 作成日時（表示用フォーマット）
        updated_at: 更新日時（表示用フォーマット）
        due_date: 期限日（表示用フォーマット、None可）
        progress_text: 進捗表示用テキスト
        progress_value: 進捗値（0.0-1.0）
        task_count: タスク総数
        completed_count: 完了タスク数
    """

    id: str
    title: str
    description: str
    status: str
    status_color: str
    created_at: str
    updated_at: str
    due_date: str | None
    progress_text: str
    progress_value: float
    task_count: int
    completed_count: int


def to_card_vm(items: Iterable[dict[str, str]]) -> list[ProjectCardVM]:
    """プロジェクトデータをカードViewModel に変換する。

    Args:
        items: プロジェクトデータのイテラブル

    Returns:
        カード表示用 ViewModel のリスト
    """
    return [_project_to_card_vm(item) for item in items]


def to_detail_vm(project: dict[str, str]) -> ProjectDetailVM:
    """プロジェクトデータを詳細ViewModel に変換する。

    Args:
        project: プロジェクトデータ

    Returns:
        詳細表示用 ViewModel
    """
    return _project_to_detail_vm(project)


def _project_to_card_vm(project: dict[str, str]) -> ProjectCardVM:
    """プロジェクトデータをカードViewModel に変換する内部関数。

    Args:
        project: プロジェクトデータ

    Returns:
        カード表示用 ViewModel
    """
    # 基本情報
    project_id = str(project.get("id", ""))
    # TODO(実装者向け): フィールド名の統一
    # - サンプル互換のため title/name フォールバックを残していますが、
    #   本実装ではドメインモデル → Presenter で title に正規化してください。
    title = str(project.get("title", project.get("name", "")))
    description = str(project.get("description", ""))
    status = str(project.get("status", ""))

    # 進捗計算
    task_count = int(project.get("tasks_count", project.get("task_count", "0")))
    completed_count = int(project.get("completed_tasks", project.get("completed_count", "0")))
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{completed_count}/{task_count} タスク完了"

    # 表示用の値
    subtitle = f"{project.get('created_at', '')} 作成"
    status_color = _get_status_color(status)

    # 説明文の省略（カード表示用）
    max_desc_length = 80
    if len(description) > max_desc_length:
        description = description[:max_desc_length] + "..."

    return ProjectCardVM(
        id=project_id,
        title=title,
        subtitle=subtitle,
        description=description,
        status=status,
        status_color=status_color,
        progress_text=progress_text,
        progress_value=progress_value,
        task_count=task_count,
        completed_count=completed_count,
    )


def _project_to_detail_vm(project: dict[str, str]) -> ProjectDetailVM:
    """プロジェクトデータを詳細ViewModel に変換する内部関数。

    Args:
        project: プロジェクトデータ

    Returns:
        詳細表示用 ViewModel
    """
    # 基本情報
    project_id = str(project.get("id", ""))
    # TODO(実装者向け): フィールド名の統一（上記カードと同様）
    title = str(project.get("title", project.get("name", "")))
    description = str(project.get("description", ""))
    status = str(project.get("status", ""))

    # 進捗計算
    task_count = int(project.get("tasks_count", project.get("task_count", "0")))
    completed_count = int(project.get("completed_tasks", project.get("completed_count", "0")))
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{progress_value:.0%} 完了 ({completed_count} / {task_count} タスク)"

    # 日時フォーマット
    created_at = str(project.get("created_at", ""))
    updated_at = str(project.get("updated_at", ""))
    raw_due = project.get("due_date")
    due_date = None if raw_due in (None, "") else str(raw_due)

    # 表示用の値
    status_color = _get_status_color(status)

    return ProjectDetailVM(
        id=project_id,
        title=title,
        description=description,
        status=status,
        status_color=status_color,
        created_at=created_at,
        updated_at=updated_at,
        due_date=due_date,
        progress_text=progress_text,
        progress_value=progress_value,
        task_count=task_count,
        completed_count=completed_count,
    )


def _get_status_color(status: str) -> str:
    """ステータスに対応する色を取得する。

    Args:
        status: プロジェクトステータス

    Returns:
        ステータスに対応する色コード
    """
    # TODO(実装者向け): ステータス色の集中管理
    # - views.theme などに定義し、全画面で共通化してください（定数/Enum推奨）。
    status_colors = {
        "進行中": "#2196F3",  # Blue
        "active": "#2196F3",
        "完了": "#4CAF50",  # Green
        "completed": "#4CAF50",
        "保留": "#FF9800",  # Orange
        "on_hold": "#FF9800",
        "キャンセル": "#9E9E9E",  # Grey
        "cancelled": "#9E9E9E",
    }
    return status_colors.get(status, "#9E9E9E")  # デフォルトはグレー
