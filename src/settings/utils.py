"""設定ユーティリティ関数群。

DRY 原則に従い、設定関連で重複している小さな変換ロジックを集約する。
"""

from __future__ import annotations

from loguru import logger

from settings.models import AgentDetailLevel


def parse_detail_level(raw: object, default: AgentDetailLevel = AgentDetailLevel.BALANCED) -> AgentDetailLevel:
    """生の値を ``AgentDetailLevel`` に変換する。

    Args:
        raw: 変換対象の値。列挙型インスタンス、または列挙値の文字列を想定。
        default: 変換に失敗した場合に返すデフォルト値。

    Returns:
        変換された ``AgentDetailLevel``。失敗時は ``default`` を返す。
    """
    if isinstance(raw, AgentDetailLevel):
        return raw
    if isinstance(raw, str):
        try:
            return AgentDetailLevel(raw)
        except ValueError:
            logger.warning("Invalid detail level value: %s", raw)
    return default
