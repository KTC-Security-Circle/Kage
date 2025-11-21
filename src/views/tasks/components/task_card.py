"""タスクカードコンポーネント

Memo の MemoCard と同様に、Presenter で整形済みのデータクラスを受け取り描画する。
親コンポーネントは TaskCardData を生成して本コンポーネントへ渡す。
"""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import flet as ft

from views.tasks.components.shared.constants import TASK_STATUS_LABELS

if TYPE_CHECKING:
    from collections.abc import Callable


# ========================================
# TaskCard 専用定数
# ========================================

CARD_PADDING: Final[int] = 12
CARD_BORDER_RADIUS: Final[int] = 12
DEFAULT_BORDER_WIDTH: Final[float] = 1.0
SELECTED_BORDER_WIDTH: Final[float] = 2.0
DEFAULT_EMPTY_TITLE: Final[str] = "(無題)"


# ========================================
# TaskCard 専用データクラス
# ========================================


@dataclass(frozen=True, slots=True)
class TaskCardData:
    """タスクカード表示用データ。

    Attributes:
        task_id: タスクID（イベントハンドリング用）
        title: 表示用タイトル
        subtitle: 補助テキスト（更新日など）
        status: 内部ステータスキー（例: "progress"）
        status_label: 表示用ラベル（例: "進行中"）
        is_selected: 選択状態
        on_click: クリック時のコールバック
    """

    task_id: str
    title: str
    subtitle: str
    status: str
    status_label: str | None = None
    is_selected: bool = False
    on_click: Callable[[], None] | None = None


# ========================================
# コンポーネント本体
# ========================================


class TaskCard(ft.Container):
    """タスクカード表示コンポーネント。

    Presenter や View 側で整形済みの TaskCardData を受け取り、純粋に描画する。
    """

    def __init__(self, data: TaskCardData) -> None:
        self._data = data
        super().__init__(
            content=self._build_card_content(),
            padding=ft.padding.all(CARD_PADDING),
            margin=ft.margin.symmetric(vertical=4),
            border_radius=CARD_BORDER_RADIUS,
            border=ft.border.all(
                width=SELECTED_BORDER_WIDTH if data.is_selected else DEFAULT_BORDER_WIDTH,
                color=ft.Colors.BLUE_400 if data.is_selected else ft.Colors.OUTLINE,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER if data.is_selected else ft.Colors.SURFACE,
            on_click=self._handle_click if data.on_click else None,
            ink=True,
            key=data.task_id,
        )

    def _build_card_content(self) -> ft.Control:
        header_controls: list[ft.Control] = [
            ft.Text(
                self._data.title or DEFAULT_EMPTY_TITLE,
                style=ft.TextThemeStyle.TITLE_MEDIUM,
                weight=ft.FontWeight.BOLD,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True,
            )
        ]
        if self._data.is_selected:
            header_controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.BLUE_400, size=20))

        header = ft.Row(controls=header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        subtitle = ft.Text(
            self._data.subtitle,
            style=ft.TextThemeStyle.BODY_MEDIUM,
            color=ft.Colors.ON_SURFACE_VARIANT,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        footer_controls: list[ft.Control] = []
        status_text = self._data.status_label or TASK_STATUS_LABELS.get(self._data.status, self._data.status)
        if status_text:
            footer_controls.append(
                ft.Container(
                    content=ft.Text(status_text, size=10, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    border_radius=12,
                )
            )

        # Display due date or status timestamp in the footer, if available
        if hasattr(self._data, "due_date") and self._data.due_date:
            footer_controls.append(
                ft.Text(
                    f"期限: {self._data.due_date}",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            )
        elif hasattr(self._data, "status_timestamp") and self._data.status_timestamp:
            footer_controls.append(
                ft.Text(
                    f"更新: {self._data.status_timestamp}",
                    style=ft.TextThemeStyle.BODY_SMALL,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            )

        footer = ft.Row(controls=footer_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=8)

        return ft.Column(controls=[header, subtitle, footer], spacing=8, tight=True)

    def _handle_click(self, _: ft.ControlEvent) -> None:
        if self._data.on_click:
            self._data.on_click()
