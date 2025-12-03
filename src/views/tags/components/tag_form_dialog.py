"""タグ作成・編集ダイアログコンポーネント

タグの作成と編集に使用する汎用ダイアログ。
カラーパレットからの色選択、名前・説明の入力、バリデーションを含む。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from views.theme import (
    TAG_COLORS,
    get_error_color,
    get_grey_color,
    get_on_primary_color,
    get_primary_color,
    get_tag_color_palette,
    get_tag_icon_bg_opacity,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TagFormData:
    """タグフォームのデータ"""

    name: str
    color: str
    description: str


class TagFormDialog(ft.AlertDialog):
    """タグ作成・編集用の汎用ダイアログ"""

    def __init__(
        self,
        *,
        title: str,
        initial_name: str = "",
        initial_color: str | None = None,
        initial_description: str = "",
        on_submit: Callable[[TagFormData], None],
        on_cancel: Callable[[], None],
    ) -> None:
        """ダイアログを初期化する。

        Args:
            title: ダイアログのタイトル
            initial_name: 初期タグ名（編集時）
            initial_color: 初期色（編集時）
            initial_description: 初期説明（編集時）
            on_submit: 送信時のコールバック
            on_cancel: キャンセル時のコールバック
        """
        super().__init__()
        self._on_submit = on_submit
        self._on_cancel = on_cancel
        self._selected_color = initial_color or TAG_COLORS.blue

        # フォームフィールド
        self._name_field = ft.TextField(
            label="タグ名",
            hint_text="例: 重要, 開発, バグ",
            value=initial_name,
            max_length=50,
            autofocus=True,
            on_change=self._on_name_change,
        )

        self._description_field = ft.TextField(
            label="説明（任意）",
            hint_text="このタグの用途を説明してください",
            value=initial_description,
            multiline=True,
            min_lines=3,
            max_lines=5,
            max_length=200,
        )

        # エラーメッセージ
        self._error_text = ft.Text(
            "",
            color=get_error_color(),
            size=12,
            visible=False,
        )

        # 選択された色のプレビュー
        self._color_preview = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.LABEL,
                        color=self._selected_color,
                        size=24,
                    ),
                    ft.Text(
                        "選択された色",
                        color=get_grey_color(700),
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(get_tag_icon_bg_opacity(), self._selected_color),
            padding=12,
            border_radius=ft.border_radius.all(8),
            border=ft.border.all(2, self._selected_color),
        )

        # カラーパレット
        self._color_palette = self._build_color_palette()

        # ダイアログ設定
        self.modal = True
        self.title = ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_LARGE)
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self._name_field,
                    self._description_field,
                    ft.Divider(),
                    ft.Text(
                        "カラー",
                        theme_style=ft.TextThemeStyle.TITLE_SMALL,
                        weight=ft.FontWeight.W_500,
                    ),
                    self._color_preview,
                    self._color_palette,
                    self._error_text,
                ],
                spacing=16,
                tight=True,
            ),
            width=500,
            padding=ft.padding.symmetric(vertical=10),
        )
        self.actions = [
            ft.TextButton("キャンセル", on_click=self._handle_cancel),
            ft.ElevatedButton(
                "保存",
                icon=ft.Icons.SAVE,
                on_click=self._handle_submit,
                bgcolor=get_primary_color(),
                color=get_on_primary_color(),
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _build_color_palette(self) -> ft.Control:
        """カラーパレットを構築する"""
        colors = get_tag_color_palette()
        color_buttons = []

        for color_info in colors:
            color_value = color_info["value"]
            is_selected = color_value == self._selected_color

            button = ft.Container(
                content=ft.Stack(
                    controls=[
                        ft.Container(
                            bgcolor=color_value,
                            border_radius=ft.border_radius.all(8),
                        ),
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECK,
                                color=get_on_primary_color(),
                                size=20,
                            ),
                            alignment=ft.alignment.center,
                            visible=is_selected,
                        ),
                    ],
                ),
                width=50,
                height=50,
                border_radius=ft.border_radius.all(8),
                border=ft.border.all(
                    3 if is_selected else 1, get_on_primary_color() if is_selected else get_grey_color(300)
                ),
                on_click=lambda _e, c=color_value: self._handle_color_select(c),
                tooltip=color_info["name"],
                ink=True,
            )
            color_buttons.append(button)

        return ft.Container(
            content=ft.Row(
                controls=color_buttons,
                wrap=True,
                spacing=8,
                run_spacing=8,
            ),
            height=120,
        )

    def _handle_color_select(self, color: str) -> None:
        """色選択ハンドラ"""
        self._selected_color = color
        # プレビュー更新
        self._color_preview.bgcolor = ft.Colors.with_opacity(get_tag_icon_bg_opacity(), color)
        self._color_preview.border = ft.border.all(2, color)
        icon = self._color_preview.content.controls[0]  # type: ignore[attr-defined]
        icon.color = color
        # パレット再構築
        self._color_palette.content = self._build_color_palette().content  # type: ignore[attr-defined]
        self.update()

    def _on_name_change(self, _e: ft.ControlEvent) -> None:
        """名前入力時のリアルタイムバリデーション"""
        self._clear_error()

    def _validate(self) -> tuple[bool, str]:
        """入力内容をバリデーションする。

        Returns:
            (バリデーション結果, エラーメッセージ)
        """
        max_name_length = 50
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]

        name = self._name_field.value or ""
        name = name.strip()

        if not name:
            return False, "タグ名は必須です"

        if len(name) > max_name_length:
            return False, f"タグ名は{max_name_length}文字以内で入力してください"

        if any(char in name for char in invalid_chars):
            return False, "タグ名に使用できない文字が含まれています"

        return True, ""

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示する"""
        self._error_text.value = message
        self._error_text.visible = True
        self.update()

    def _clear_error(self) -> None:
        """エラーメッセージをクリアする"""
        self._error_text.visible = False
        self.update()

    def _handle_submit(self, _e: ft.ControlEvent) -> None:
        """送信ハンドラ"""
        is_valid, error_message = self._validate()

        if not is_valid:
            self._show_error(error_message)
            return

        form_data = TagFormData(
            name=self._name_field.value.strip(),  # type: ignore[union-attr]
            color=self._selected_color,
            description=self._description_field.value.strip() if self._description_field.value else "",  # type: ignore[union-attr]
        )

        self._on_submit(form_data)
        self.open = False
        self.update()

    def _handle_cancel(self, _e: ft.ControlEvent) -> None:
        """キャンセルハンドラ"""
        self._on_cancel()
        self.open = False
        self.update()


def show_tag_create_dialog(
    page: ft.Page,
    on_submit: Callable[[TagFormData], None],
) -> None:
    """タグ作成ダイアログを表示する。

    Args:
        page: Fletページオブジェクト
        on_submit: 送信時のコールバック
    """

    def on_cancel() -> None:
        """キャンセル時の処理"""

    dialog = TagFormDialog(
        title="新規タグ作成",
        on_submit=on_submit,
        on_cancel=on_cancel,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_tag_edit_dialog(
    page: ft.Page,
    tag: dict[str, str],
    on_submit: Callable[[TagFormData], None],
) -> None:
    """タグ編集ダイアログを表示する。

    Args:
        page: Fletページオブジェクト
        tag: 編集対象のタグデータ
        on_submit: 送信時のコールバック
    """

    def on_cancel() -> None:
        """キャンセル時の処理"""

    dialog = TagFormDialog(
        title="タグを編集",
        initial_name=tag.get("name", ""),
        initial_color=tag.get("color"),
        initial_description=tag.get("description", ""),
        on_submit=on_submit,
        on_cancel=on_cancel,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
