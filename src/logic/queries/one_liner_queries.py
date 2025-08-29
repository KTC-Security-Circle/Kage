"""一言コメント関連のクエリオブジェクト

Application Service層で使用するQuery DTOs (Data Transfer Objects)
"""

from __future__ import annotations

from dataclasses import dataclass


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
