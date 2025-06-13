# views/__init__.py
# ビュー層の初期化とエクスポート

from views.home.view import create_home_view
from views.task.view import create_task_view

__all__ = [
    "create_home_view",
    "create_task_view",
]
