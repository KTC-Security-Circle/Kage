"""プロジェクトカードコンポーネント

プロジェクト情報を表示するカードUIコンポーネント。
ステータスバッジ、説明、統計情報、アクションボタンを含む。

共通カードコンポーネント（views.shared.components.card）を使用。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from views.shared.components import Card, CardActionData, CardBadgeData, CardData, CardMetadataData
from views.theme import (
    get_error_color,
    get_outline_color,
    get_primary_color,
    get_status_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import flet as ft

    from views.projects.presenter import ProjectCardVM


def create_project_card(
    project: dict[str, Any],
    on_edit: Callable[[ft.ControlEvent, dict[str, Any]], None],
    on_delete: Callable[[ft.ControlEvent, dict[str, Any]], None],
) -> ft.Control:
    """プロジェクトカードを作成する（共通Cardコンポーネント使用）。

    Args:
        project: プロジェクトデータ（id, name, description, status, task_id, created_at）
        on_edit: 編集ボタンクリック時のコールバック
        on_delete: 削除ボタンクリック時のコールバック

    Returns:
        プロジェクトカードコンポーネント
    """
    import flet as ft

    # ステータス色はテーマに集約
    status_color = get_status_color(project["status"])

    # CardDataを構築
    card_data = CardData(
        title=project.get("title", project.get("name", "")),
        description=project["description"],
        badge=CardBadgeData(
            text=project["status"],
            color=status_color,
        ),
        metadata=[
            CardMetadataData(
                icon=ft.Icons.TASK_ALT,
                text=f"{len(project.get('task_id', []))} タスク",
            ),
            CardMetadataData(
                icon=ft.Icons.CALENDAR_TODAY,
                text=project["created_at"],
            ),
        ],
        actions=[
            CardActionData(
                icon=ft.Icons.EDIT_OUTLINED,
                tooltip="編集",
                on_click=lambda e, p=project: on_edit(e, p),
            ),
            CardActionData(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip="削除",
                on_click=lambda e, p=project: on_delete(e, p),
                icon_color=get_error_color(),
            ),
        ],
    )

    return Card(data=card_data)


def create_project_card_from_vm(
    vm: ProjectCardVM,  # type: ignore[name-defined]
    on_select: Callable[[str], None],
    *,
    is_selected: bool = False,
) -> ft.Control:  # type: ignore[name-defined]
    """ViewModel からプロジェクトカードを作成する（共通Cardコンポーネント使用）。

    View の直書きを置き換え、再利用性を高めた統一インターフェース。
    プログレスバーを含む特殊なレイアウトのため、ProjectCardWithProgressを使用。

    Args:
        vm: プロジェクトカードViewModel
        on_select: カード選択時のコールバック (project_id を引数に取る)
        is_selected: 選択状態フラグ

    Returns:
        プロジェクトカードコンポーネント
    """
    import flet as ft

    # CardDataを構築
    card_data = CardData(
        title=vm.title,
        description=vm.description,
        badge=CardBadgeData(
            text=vm.status,
            color=vm.status_color,
        ),
        metadata=[
            CardMetadataData(
                icon=ft.Icons.CALENDAR_TODAY,
                text=vm.subtitle,
            ),
        ],
        actions=[],
        on_click=lambda: on_select(vm.id),
        is_selected=is_selected,
    )

    return ProjectCardWithProgress(
        data=card_data,
        progress_text=vm.progress_text,
        progress_value=vm.progress_value,
    )


class ProjectCardWithProgress(Card):
    """プログレスバー付きプロジェクトカード

    共通Cardコンポーネントを継承し、プログレスバーを追加表示する。
    """

    def __init__(
        self,
        data: CardData,
        progress_text: str,
        progress_value: float,
    ) -> None:
        """プログレスバー付きカードを初期化。

        Args:
            data: カード表示データ
            progress_text: 進捗表示テキスト
            progress_value: 進捗値（0.0-1.0）
        """
        super().__init__(data)
        self._progress_text = progress_text
        self._progress_value = progress_value
        self._inject_progress_bar()

    def _inject_progress_bar(self) -> None:
        """プログレスバーをカードに追加する"""
        import flet as ft

        try:
            card_content = self.content
            if isinstance(card_content, ft.Card):
                container = card_content.content
                if isinstance(container, ft.Container):
                    column = container.content
                    if isinstance(column, ft.Column):
                        # フッターの後にプログレスバーを追加
                        progress_section = ft.Column(
                            controls=[
                                ft.Text(
                                    self._progress_text,
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                    color=get_text_secondary_color(),
                                ),
                                ft.ProgressBar(
                                    value=self._progress_value,
                                    color=get_primary_color(),
                                    bgcolor=get_outline_color(),
                                    height=6,
                                ),
                            ],
                            spacing=4,
                        )
                        column.controls.append(progress_section)
        except (AttributeError, IndexError):
            pass  # エラーは無視（デフォルト表示のまま）
