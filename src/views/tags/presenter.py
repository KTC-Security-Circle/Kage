"""Tags View Presenter

StateからUIコンポーネント用のPropsを生成する責務を担う。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

    from .controller import TagsController
    from .state import TagDict, TagsViewState

from views.theme import get_status_label

from .components.action_bar import TagsActionBarProps
from .components.tag_detail_panel import (
    RelatedItem,
    TagDetailData,
    TagDetailPanelProps,
)
from .components.tag_list_item import TagListItemProps


class TagsPresenter:
    """Tags用のPresenter。"""

    def build_action_bar_props(
        self,
        _state: TagsViewState,  # 仕様上保持 (将来: 件数/フィルタ状態反映など)
        *,
        on_create: Callable[[ft.ControlEvent], None],
        on_search: Callable[[ft.ControlEvent], None],
        on_refresh: Callable[[ft.ControlEvent], None],
    ) -> TagsActionBarProps:
        """アクションバーPropsを生成する。"""
        return TagsActionBarProps(
            search_placeholder="タグを検索…",
            on_create=on_create,
            on_search=on_search,
            on_refresh=on_refresh,
        )

    def build_tag_list_item_props(
        self,
        tag: TagDict,
        controller: TagsController,
        *,
        selected: bool,
        on_click: Callable[[ft.ControlEvent, str], None],
    ) -> TagListItemProps:
        """タグリストアイテムPropsを生成する。

        Args:
            tag: タグデータ
            controller: カウント情報取得用のコントローラ
            selected: 選択状態
            on_click: クリックハンドラ

        Returns:
            TagListItemProps
        """
        counts = controller.get_tag_counts(tag["id"])
        return TagListItemProps(
            tag_id=tag["id"],
            name=tag["name"],
            color=tag["color"],
            total_count=counts["total_count"],
            memo_count=counts["memo_count"],
            task_count=counts["task_count"],
            selected=selected,
            on_click=on_click,
        )

    def build_tag_detail_panel_props(
        self,
        tag: TagDict | None,
        controller: TagsController,
        *,
        on_edit: Callable[[ft.ControlEvent], None],
        on_memo_click: Callable[[ft.ControlEvent, str], None],
        on_task_click: Callable[[ft.ControlEvent, str], None],
    ) -> TagDetailPanelProps:
        """タグ詳細パネルPropsを生成する。

        Args:
            tag: 選択されたタグ（未選択時None）
            controller: 関連アイテム取得用のコントローラ
            on_edit: 編集ハンドラ
            on_memo_click: メモクリックハンドラ
            on_task_click: タスククリックハンドラ

        Returns:
            TagDetailPanelProps
        """
        if not tag:
            return TagDetailPanelProps(
                detail_data=None,
                on_edit=on_edit,
                on_memo_click=on_memo_click,
                on_task_click=on_task_click,
            )

        # 関連アイテム取得
        memos = controller.get_related_memos(tag["id"])
        tasks = controller.get_related_tasks(tag["id"])

        # RelatedItem変換
        related_memos = [
            RelatedItem(
                id=m["id"],
                title=m["title"],
                description=m["description"],
            )
            for m in memos
        ]

        related_tasks = [
            RelatedItem(
                id=t["id"],
                title=t["title"],
                description=t["description"],
                status=t.get("status"),
                status_label=get_status_label(t.get("status")),
            )
            for t in tasks
        ]

        counts = controller.get_tag_counts(tag["id"])
        detail_data = TagDetailData(
            tag_id=tag["id"],
            name=tag["name"],
            color=tag["color"],
            description=tag.get("description", ""),
            created_at=tag.get("created_at", "不明"),
            updated_at=tag.get("updated_at", "不明"),
            total_count=counts["total_count"],
            memo_count=counts["memo_count"],
            task_count=counts["task_count"],
            related_memos=related_memos,
            related_tasks=related_tasks,
        )

        return TagDetailPanelProps(
            detail_data=detail_data,
            on_edit=on_edit,
            on_memo_click=on_memo_click,
            on_task_click=on_task_click,
        )
