"""Task Detail Panel component.

選択中タスクの詳細表示とステータス変更 UI を提供する。
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.tasks.components.shared.constants import STATUS_ORDER, TASK_STATUS_LABELS
from views.theme import (
    get_grey_color,
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_success_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.tasks.presenter import RelatedTaskVM, TaskCardVM, TaskDetailVM


@dataclass(frozen=True)
class DetailPanelProps:
    """初期プロパティ。"""

    on_status_change: Callable[[str, str], None]
    on_edit: Callable[[str], None]  # タスクIDを受け取る編集コールバック
    on_task_select: Callable[[str], None] | None = None  # 関連タスク選択コールバック
    on_project_select: Callable[[str], None] | None = None  # プロジェクト選択コールバック


class TaskDetailPanel:
    """右ペインの詳細表示コンポーネント (非継承)。"""

    def __init__(self, props: DetailPanelProps) -> None:
        self._props = props
        # TaskDetailVM 優先。後方互換で TaskCardVM も許容
        self._vm: TaskDetailVM | TaskCardVM | None = None
        self._status_dd: ft.Dropdown | None = None
        # ルートは固定のコンテナを持ち、content を差し替える（コントロール参照の不一致を防ぐ）
        self._root: ft.Container = ft.Container(expand=True)

    @property
    def control(self) -> ft.Control:
        # 初期表示はプレースホルダ
        if self._root.content is None:
            self._root.content = self._placeholder()
        return self._root

    def set_item(self, vm: TaskDetailVM | TaskCardVM | None) -> None:
        """詳細対象を切り替えて再描画。"""
        self._vm = vm
        if not vm:
            # 既存ルートの content を置換
            self._root.content = self._placeholder()
            with contextlib.suppress(AssertionError):
                self._root.update()
            return
        # TODO: MVC化時はフォーム編集(タイトル/説明/期日等)をこのパネルに統合し、
        #       変更は Controller 経由で ApplicationService に送る。
        # TODO: ステータス→色 (Badge) のマッピングは constants に集約し、表示とロジックで共有。
        # TODO: 書き込み失敗時は楽観的更新のロールバックとエラーToastを表示する。

        # Flet Option は key/text を指定可能。value は key が使われる。
        status_options = [ft.dropdown.Option(key=s, text=TASK_STATUS_LABELS.get(s, s)) for s in STATUS_ORDER]
        self._status_dd = ft.Dropdown(
            label="ステータス",
            value=vm.status or "",
            options=status_options,
            # 余分な str() 二重変換を排除し、None 時は空文字へ正規化
            on_change=lambda e: self._handle_status_change(e.control.value or ""),  # type: ignore[arg-type]
            width=220,
        )

        # 詳細セクションを構築
        details_sections = [
            # ヘッダー
            ft.Text("タスク詳細", theme_style=ft.TextThemeStyle.BODY_LARGE, weight=ft.FontWeight.W_500),
            ft.Divider(height=1),
            # タイトル
            self._build_section("タイトル", ft.Text(vm.title, theme_style=ft.TextThemeStyle.BODY_MEDIUM)),
            # 説明
            self._build_section(
                "説明",
                ft.Text(
                    getattr(vm, "description", "") or "説明なし",
                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                    color=get_text_secondary_color(),
                ),
            ),
            # ステータス
            self._build_section("ステータス", self._status_dd),
        ]

        # タグ表示（タグがある場合）
        tags = getattr(vm, "tags", [])
        if tags:
            tag_badges = self._build_tag_badges(tags)
            details_sections.append(self._build_section("タグ", tag_badges))

        # 期限（設定されている場合）
        due_date = getattr(vm, "due_date", None)
        if due_date:
            details_sections.append(
                self._build_section("期限", ft.Text(str(due_date), theme_style=ft.TextThemeStyle.BODY_SMALL))
            )

        # 完了日時（設定されている場合）
        completed_at = getattr(vm, "completed_at", None)
        if completed_at:
            details_sections.append(
                self._build_section("完了", ft.Text(str(completed_at), theme_style=ft.TextThemeStyle.BODY_SMALL))
            )

        # 繰り返し（設定されている場合）
        is_recurring = getattr(vm, "is_recurring", False)
        if is_recurring:
            recurrence_rule = getattr(vm, "recurrence_rule", None)
            details_sections.append(
                self._build_section(
                    "繰り返し設定",
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "繰り返しタスク",
                                    size=11,
                                    weight=ft.FontWeight.W_500,
                                ),
                                border=ft.border.all(1, get_outline_color()),
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ),
                            ft.Text(
                                str(recurrence_rule) if recurrence_rule else "",
                                size=11,
                                color=get_text_secondary_color(),
                            )
                            if recurrence_rule
                            else ft.Container(),
                        ],
                        spacing=4,
                    ),
                )
            )

        # プロジェクト情報
        project_info = self._build_project_info(vm)
        if project_info.controls:  # プロジェクト情報がある場合のみ追加（Columnのcontrolsをチェック）
            details_sections.append(project_info)

        # 作成日
        created_at = getattr(vm, "created_at", None)
        if created_at:
            details_sections.append(
                self._build_section("作成日", ft.Text(str(created_at), theme_style=ft.TextThemeStyle.BODY_SMALL))
            )

        # 編集ボタン（最下部）
        edit_button = ft.OutlinedButton(
            text="編集",
            icon=ft.Icons.EDIT,
            on_click=lambda _: self._handle_edit(),
            expand=True,
        )
        details_sections.append(edit_button)

        card = ft.Card(
            expand=True,
            content=ft.Container(
                expand=True,
                content=ft.Column(
                    controls=details_sections,
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=16,
            ),
        )
        # ルートの content を差し替えて更新
        self._root.content = card
        with contextlib.suppress(AssertionError):
            self._root.update()

    # Internal
    def _placeholder(self) -> ft.Control:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.TASK_ALT,
                            size=48,
                            color=get_outline_color(),
                        ),
                        ft.Text(
                            "タスクを選択して詳細を表示",
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=get_text_secondary_color(),
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=48,
            ),
            expand=True,
        )

    def _build_section(self, label: str, content: ft.Control) -> ft.Column:
        """ラベル付きセクションを構築する。

        Args:
            label: セクションラベル
            content: セクションコンテンツ

        Returns:
            セクションColumn
        """
        return ft.Column(
            controls=[
                ft.Text(
                    label,
                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                    color=get_text_secondary_color(),
                ),
                content,
            ],
            spacing=4,
        )

    def _build_tag_badges(self, tags: list) -> ft.Row:
        """タグバッジのリストを構築する。

        Args:
            tags: タグのリスト

        Returns:
            タグバッジを含むRow
        """
        tag_controls = []
        for tag in tags:
            tag_name = getattr(tag, "name", str(tag))
            tag_color = getattr(tag, "color", None) or get_primary_color()
            badge = ft.Container(
                content=ft.Text(
                    tag_name,
                    size=12,
                    color=get_on_primary_color(),
                    weight=ft.FontWeight.W_500,
                ),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=tag_color,
                border_radius=12,
            )
            tag_controls.append(badge)

        return ft.Row(
            controls=tag_controls,
            spacing=8,
            wrap=True,
        )

    def _build_project_info(self, vm: TaskDetailVM | TaskCardVM) -> ft.Column:
        """プロジェクト情報を表示するコントロールを構築。

        Args:
            vm: タスクViewModel

        Returns:
            プロジェクト情報のセクション（ft.Column）
        """
        project_name = getattr(vm, "project_name", None)
        project_status = getattr(vm, "project_status", None)
        project_tasks = getattr(vm, "project_tasks", [])
        project_id = getattr(vm, "project_id", None)

        if not project_name:
            return ft.Column()  # 空のColumnを返す

        # プロジェクト画面への遷移コールバック
        def on_project_click(_: ft.ControlEvent) -> None:
            from loguru import logger

            logger.info(f"プロジェクトボタンがクリックされました: project_id={project_id}")
            if self._props.on_project_select and project_id:
                logger.debug(f"on_project_selectコールバックを呼び出します: {project_id}")
                try:
                    self._props.on_project_select(str(project_id))
                    logger.debug("コールバック呼び出しが完了しました")
                except Exception as e:
                    logger.error(f"コールバック呼び出しでエラーが発生: {e}", exc_info=True)
            else:
                logger.warning(
                    f"プロジェクト遷移がスキップされました: "
                    f"on_project_select={self._props.on_project_select}, project_id={project_id}"
                )

        # プロジェクト情報の表示コントロール
        project_button = ft.OutlinedButton(
            text=project_name,
            icon=ft.Icons.OPEN_IN_NEW,
            icon_color=get_grey_color(600),
            on_click=on_project_click,
        )

        project_status_text = ft.Text(
            f"ステータス: {project_status}",
            size=11,
            color=get_text_secondary_color(),
        )

        project_section_controls = [project_button, project_status_text]

        # 関連タスクセクション
        if project_tasks:
            # 展開状態を管理
            tasks_list = ft.Column(visible=False, spacing=4)
            toggle_button = ft.TextButton(
                text=f"関連タスクを表示 ({len(project_tasks)})",
                icon=ft.Icons.ARROW_DROP_DOWN,
            )

            def toggle_tasks(_: ft.ControlEvent) -> None:
                tasks_list.visible = not tasks_list.visible
                toggle_button.icon = ft.Icons.ARROW_DROP_UP if tasks_list.visible else ft.Icons.ARROW_DROP_DOWN
                toggle_button.text = (
                    "関連タスクを非表示" if tasks_list.visible else f"関連タスクを表示 ({len(project_tasks)})"
                )
                with contextlib.suppress(AssertionError):
                    toggle_button.update()
                    tasks_list.update()

            toggle_button.on_click = toggle_tasks

            # タスクリスト項目を作成
            def create_task_item(task: RelatedTaskVM) -> ft.Container:
                def on_jump_click(_: ft.ControlEvent) -> None:
                    if self._props.on_task_select:
                        self._props.on_task_select(task.id)

                return ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if task.is_completed else ft.Icons.CIRCLE_OUTLINED,
                                size=16,
                                color=get_success_color() if task.is_completed else get_grey_color(400),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        task.title,
                                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        task.status,
                                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                                        color=get_text_secondary_color(),
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD,
                                icon_size=16,
                                tooltip="このタスクを表示",
                                on_click=on_jump_click,
                            ),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(vertical=4, horizontal=0),
                )

            task_items = [create_task_item(task) for task in project_tasks]

            tasks_list.controls = task_items
            project_section_controls.extend([toggle_button, tasks_list])

        # プロジェクト情報全体をセクションとして返す
        return self._build_section(
            "プロジェクト",
            ft.Column(
                controls=project_section_controls,
                spacing=8,
            ),
        )

    def _handle_status_change(self, new_status: str) -> None:
        """ステータス変更イベントを親へ通知する。

        Args:
            new_status: ドロップダウンで選択された新ステータスキー
        """
        if not self._vm:
            return
        # self._vm.id は VM 内部で文字列前提。安全のため明示的に str にしておく。
        self._props.on_status_change(str(self._vm.id), new_status)

    def _handle_edit(self) -> None:
        """編集ボタンクリック時の処理。"""
        if not self._vm:
            return
        self._props.on_edit(str(self._vm.id))
