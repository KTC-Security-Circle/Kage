"""ステータス表示値の正規化ユーティリティ。

英語内部コードと日本語表示ラベルの相互変換/正規化を一元管理する。

対象ステータス:
    active / 進行中
    planned / 計画中
    on_hold / 保留
    completed / 完了
    cancelled / 中止, キャンセル

利用指針:
    - 永続化/ドメイン層は英語小文字コードを使用する前提
    - UI入力(日本語/英語)は normalize_status で内部コードへ正規化
    - 表示には display_label で日本語ラベルへ変換

追加理由:
    - 既存コードで jp_map などの辞書が複数ファイルに重複
    - views.theme と整合した表示値(色取得)のため集中管理が必要
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class StatusMapping:
    """英語コードと日本語ラベルの双方向マッピング定義。"""

    # 英語→日本語
    EN_TO_JP: ClassVar[dict[str, str]] = {
        "active": "進行中",
        "planned": "計画中",
        "on_hold": "保留",
        "completed": "完了",
        "cancelled": "中止",  # 基本表示は「中止」で統一
    }

    # 日本語→英語（同義語吸収: キャンセル→cancelled）
    JP_TO_EN: ClassVar[dict[str, str]] = {
        "進行中": "active",
        "計画中": "planned",
        "保留": "on_hold",
        "完了": "completed",
        "中止": "cancelled",
        "キャンセル": "cancelled",
    }


def normalize_status(value: str) -> str:
    """任意のステータス文字列を内部英語コードへ正規化する。

    Args:
        value: 英語コードまたは日本語表示値

    Returns:
        内部英語コード（不明値はそのまま小文字化した値）
    """
    raw = value.strip()
    lower = raw.lower().replace("-", "_")
    # まず英語コード（小文字）判定
    if lower in StatusMapping.EN_TO_JP:  # type: ignore[arg-type]
        return lower
    # 次に日本語から英語変換
    if raw in StatusMapping.JP_TO_EN:
        return StatusMapping.JP_TO_EN[raw]
    return lower


def display_label(value: str) -> str:
    """内部英語コードまたは日本語値から標準日本語ラベルを取得する。

    Args:
        value: 英語コードまたは日本語値

    Returns:
        標準化された日本語表示ラベル（未知値は入力値そのまま）
    """
    raw = value.strip()
    lower = raw.lower().replace("-", "_")
    if lower in StatusMapping.EN_TO_JP:  # 英語→日本語
        return StatusMapping.EN_TO_JP[lower]
    # 日本語は正規化（同義語吸収）
    if raw in StatusMapping.JP_TO_EN:
        return StatusMapping.EN_TO_JP[StatusMapping.JP_TO_EN[raw]]
    return raw


def is_known_status(value: str) -> bool:
    """ステータス値が既知の定義か判定する。"""
    raw = value.strip()
    return raw.lower() in StatusMapping.EN_TO_JP or raw in StatusMapping.JP_TO_EN


__all__ = [
    "StatusMapping",
    "normalize_status",
    "display_label",
    "is_known_status",
]
