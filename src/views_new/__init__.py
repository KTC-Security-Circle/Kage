"""Kage Views package - Flet版実装。

このパッケージは、OpenSpec提案書に基づいて再実装されたFlet版のビュー層を提供します。
従来のAppBarベースの実装からSidebarベースの設計に移行し、
モダンで直感的なUIを提供します。

主要コンポーネント:
    - layout: メインレイアウトとルーティング管理
    - theme: アプリ全体のデザイントークン
    - shared: 共通コンポーネント（BaseView、Sidebar、ダイアログ等）
    - 各種画面: home, projects, tags, tasks, memos, terms, settings

使用例:
    from views_new import HomeView, ProjectsView
    from views_new.layout import build_layout
"""

from __future__ import annotations

# 主要Viewクラスのエクスポート（実装後に追加予定）
from .home.view import HomeView
from .projects.view import ProjectsView

# TODO: 各View実装完了後に以下をアンコメント
# from .tags.view import TagsView
# from .tasks.view import TasksView
# from .memos.view import MemosView
# from .terms.view import TermsView
# from .settings.view import SettingsView

__all__ = [
    "HomeView",
    "ProjectsView",
    # "TagsView",
    # "TasksView",
    # "MemosView",
    # "TermsView",
    # "SettingsView",
]
