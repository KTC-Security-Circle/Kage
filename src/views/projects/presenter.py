"""プロジェクト画面のプレゼンテーション層

Domain Model から Presentation Model への変換ロジックを提供。
UI に必要な形式でデータを整形し、表示ロジックを分離する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from models import ProjectStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

    from models import ProjectRead


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
    task_id: list[str]


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
        task_id: 関連タスクIDリスト
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
    task_id: list[str]


def to_card_vm(items: Iterable[dict[str, str]]) -> list[ProjectCardVM]:
    """プロジェクトデータをカードViewModel に変換する。

    Args:
        items: プロジェクトデータのイテラブル

    Returns:
        カード表示用 ViewModel のリスト
    """
    return [_project_to_card_vm(item) for item in items]


def to_card_vm_from_domain(items: Iterable[ProjectRead]) -> list[ProjectCardVM]:  # type: ignore[name-defined]
    """ProjectRead のドメインモデルから直接カードViewModel に変換する。

    Controller の dict 変換処理を不要にし、Presenter で責務を完結させる。

    Args:
        items: ProjectRead のイテラブル

    Returns:
        カード表示用 ViewModel のリスト
    """
    return [_project_read_to_card_vm(item) for item in items]


def to_detail_vm(project: dict[str, str]) -> ProjectDetailVM:
    """プロジェクトデータを詳細ViewModel に変換する。

    Args:
        project: プロジェクトデータ

    Returns:
        詳細表示用 ViewModel
    """
    return _project_to_detail_vm(project)


def to_detail_vm_from_domain(project: ProjectRead) -> ProjectDetailVM:  # type: ignore[name-defined]
    """ProjectRead のドメインモデルから直接詳細ViewModel に変換する。

    Args:
        project: ProjectRead モデル

    Returns:
        詳細表示用 ViewModel
    """
    return _project_read_to_detail_vm(project)


def _project_to_card_vm(project: dict[str, str]) -> ProjectCardVM:
    """プロジェクトデータをカードViewModel に変換する内部関数。

    Args:
        project: プロジェクトデータ

    Returns:
        カード表示用 ViewModel
    """
    # 基本情報
    project_id = str(project.get("id", ""))
    title = str(project.get("title", project.get("name", "")))
    description = str(project.get("description", ""))
    status = str(project.get("status", ""))

    # 進捗計算
    task_id_list = project.get("task_id", [])
    if isinstance(task_id_list, str):
        # 文字列で来た場合のフォールバック（本来はリストであるべき）
        task_id_list = []

    task_count = len(task_id_list)
    # completed_count は現状辞書から取得するしかない（タスクの状態を知る術がないため）
    completed_count = int(project.get("completed_tasks", project.get("completed_count", "0")))
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{completed_count}/{task_count} タスク完了"

    # 表示用の値（ステータス色は theme.py から取得）
    from views.theme import get_status_color

    subtitle = f"{project.get('created_at', '')} 作成"
    try:
        ProjectStatus.parse(status)  # Validate status
        status_color = get_status_color(status)
    except ValueError:
        status_color = get_status_color("on_hold")

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
        task_id=task_id_list,  # type: ignore[arg-type]
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
    title = str(project.get("title", project.get("name", "")))
    description = str(project.get("description", ""))
    status = str(project.get("status", ""))

    # 進捗計算
    task_id_list = project.get("task_id", [])
    if isinstance(task_id_list, str):
        task_id_list = []

    task_count = len(task_id_list)
    completed_count = int(project.get("completed_tasks", project.get("completed_count", "0")))
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{progress_value:.0%} 完了 ({completed_count} / {task_count} タスク)"

    # 日時フォーマット
    created_at = str(project.get("created_at", ""))
    updated_at = str(project.get("updated_at", ""))
    raw_due = project.get("due_date")
    due_date = None if raw_due in (None, "") else str(raw_due)

    # 表示用の値（theme.py を使用）
    from views.theme import get_status_color

    try:
        ProjectStatus.parse(status)  # Validate status
        status_color = get_status_color(status)
    except ValueError:
        status_color = get_status_color("on_hold")

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
        task_id=task_id_list,  # type: ignore[arg-type]
    )


def _project_read_to_card_vm(project: ProjectRead) -> ProjectCardVM:  # type: ignore[name-defined]
    """ProjectRead ドメインモデルをカードViewModel に変換する内部関数。

    Args:
        project: ProjectRead ドメインモデル

    Returns:
        カード表示用 ViewModel
    """
    # 基本情報
    project_id = str(getattr(project, "id", ""))
    title = str(getattr(project, "title", ""))
    description = str(getattr(project, "description", ""))
    status_enum = getattr(project, "status", ProjectStatus.ACTIVE)

    # 進捗計算
    # ProjectRead に task_id があると仮定
    task_id_list = getattr(project, "task_id", [])
    task_count = len(task_id_list)
    completed_count = 0  # 現状は未集計
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{completed_count}/{task_count} タスク完了"

    # 表示用の値
    created_at = str(getattr(project, "created_at", ""))
    subtitle = f"{created_at} 作成" if created_at else "作成日不明"

    # ステータス表示（theme.py を使用）
    from views.theme import get_status_color

    if isinstance(status_enum, ProjectStatus):
        status_display = ProjectStatus.display_label(status_enum)
        status_color = get_status_color(status_display)
    else:
        status_display = str(status_enum)
        status_color = get_status_color("on_hold")

    # 説明文の省略（カード表示用）
    max_desc_length = 80
    if len(description) > max_desc_length:
        description = description[:max_desc_length] + "..."

    return ProjectCardVM(
        id=project_id,
        title=title,
        subtitle=subtitle,
        description=description,
        status=status_display,
        status_color=status_color,
        progress_text=progress_text,
        progress_value=progress_value,
        task_count=task_count,
        completed_count=completed_count,
        task_id=task_id_list,
    )


def _project_read_to_detail_vm(project: ProjectRead) -> ProjectDetailVM:  # type: ignore[name-defined]
    """ProjectRead ドメインモデルを詳細ViewModel に変換する内部関数。

    Args:
        project: ProjectRead ドメインモデル

    Returns:
        詳細表示用 ViewModel
    """
    # 基本情報
    project_id = str(project.id)
    title = project.title
    description = project.description if project.description is not None else ""
    status_enum = project.status

    # 進捗計算
    task_id_list = getattr(project, "task_id", [])
    task_count = len(task_id_list)
    completed_count = 0  # 現状は未集計
    progress_value = (completed_count / task_count) if task_count > 0 else 0.0
    progress_text = f"{progress_value:.0%} 完了 ({completed_count} / {task_count} タスク)"

    # 日時フォーマット
    created_at = str(project.created_at)
    updated_at = str(project.updated_at)
    due_date_raw = getattr(project, "due_date", None)
    due_date = None if due_date_raw in (None, "") else str(due_date_raw)

    # ステータス表示（theme.py を使用）
    from views.theme import get_status_color

    if isinstance(status_enum, ProjectStatus):
        status_display = ProjectStatus.display_label(status_enum)
        status_color = get_status_color(status_display)
    else:
        status_display = str(status_enum)
        status_color = get_status_color("on_hold")

    return ProjectDetailVM(
        id=project_id,
        title=title,
        description=description,
        status=status_display,
        status_color=status_color,
        created_at=created_at,
        updated_at=updated_at,
        due_date=due_date,
        progress_text=progress_text,
        progress_value=progress_value,
        task_count=task_count,
        completed_count=completed_count,
        task_id=task_id_list,
    )
