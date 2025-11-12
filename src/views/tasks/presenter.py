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
        priority: 優先度（数値/未設定は None）
        created_at: 作成日（文字列、未設定は None）
        updated_at: 更新日（文字列、未設定は None）
    """

    id: str
    title: str
    description: str
    status: str
    subtitle: str = ""
    priority: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


# TODO: 日付/時刻の整形 (subtitle のローカライズ) を集中管理するヘルパーを導入する。
# TODO: priority などの数値をラベル化 (例: 1=Low, 3=High) し、i18n対応する。
# TODO: パフォーマンス観点で to_card_vm はジェネレータやバッチ変換最適化を検討 (大量件数時)。


def to_card_vm(items: Iterable[dict]) -> list[TaskCardVM]:
    """辞書タスクを TaskCardVM に変換する。

    Args:
        items: タスク辞書イテラブル
    Returns:
        TaskCardVM リスト
    """
    return [
        TaskCardVM(
            id=str(x.get("id")),
            title=str(x.get("title", "(無題)")),
            subtitle=str(x.get("updated_at", "")),
            description=str(x.get("description", "")),
            status=str(x.get("status", "")),
        )
        for x in items
    ]


def to_detail_vm(item: dict) -> TaskDetailVM:
    """辞書タスクを TaskDetailVM に変換する。

    Args:
        item: タスク辞書
    Returns:
        TaskDetailVM
    """
    return TaskDetailVM(
        id=str(item.get("id")),
        title=str(item.get("title", "(無題)")),
        description=str(item.get("description", "")),
        status=str(item.get("status", "")),
        subtitle=str(item.get("updated_at", "")),
        priority=(int(item["priority"]) if "priority" in item and item.get("priority") is not None else None),
        created_at=str(item.get("created_at")) if item.get("created_at") is not None else None,
        updated_at=str(item.get("updated_at")) if item.get("updated_at") is not None else None,
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
    )


# TODO: View/Persistence 層からの属性差異を吸収する Mapper 層を検討。
#       例: DBのカラム名とViewModelのプロパティ名の差異 (updatedAt vs updated_at)。
