# views/__init__.py
# ビュー層の初期化とエクスポート

from views.home.view import create_home_view

__all__ = [
    "create_home_view",
]
