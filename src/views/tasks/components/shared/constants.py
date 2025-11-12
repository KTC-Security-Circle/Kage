"""Tasks View Shared Constants.

UIのステータス表記や順序を集中管理し、Presenter/View/Controller で再利用する。
"""

from __future__ import annotations

# ステータスの表示名（短いラベル）。React テンプレート準拠
TASK_STATUS_LABELS: dict[str, str] = {
    "todo": "TODO",
    "todays": "今日",
    "progress": "進行中",
    "waiting": "待機中",
    "completed": "完了",
    "canceled": "キャンセル",
    "overdue": "期限超過",
}

# タブに表示する順序（React テンプレートの並び）
STATUS_ORDER: list[str] = [
    "todo",
    "todays",
    "progress",
    "waiting",
    "completed",
    "canceled",
    "overdue",
]

# 空サブタイトルなどのデフォルト
DEFAULT_EMPTY_SUBTITLE = ""
