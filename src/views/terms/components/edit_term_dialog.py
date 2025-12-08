"""用語編集ダイアログコンポーネント。

【責務】
    既存の用語を編集するためのダイアログUIを提供。
    - フォーム入力（キー、タイトル、説明、ステータス、出典URL、同義語、タグ）
    - バリデーション
    - 更新コールバックの呼び出し

【非責務】
    - データベース操作 → Controller/ApplicationService
    - 状態管理 → State/Controller
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import flet as ft

from models import TermStatus
from views.terms.components.shared import TagSelectorMixin
from views.theme import (
    get_error_color,
    get_text_secondary_color,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class EditTermDialogProps:
    """用語編集ダイアログの初期化プロパティ。"""

    term_data: dict[str, Any]
    on_update: Callable[[dict[str, object]], None]
    on_cancel: Callable[[], None] | None = None
    all_tags: list[Any] | None = None


class EditTermDialog(TagSelectorMixin):
    """用語編集ダイアログコンポーネント

    TagSelectorMixinを使用してタグ選択UIの共通ロジックを継承。
    """

    # フィールド長の制限（フォーム定義とバリデーションで共有）
    MAX_KEY_LENGTH = 100
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_URL_LENGTH = 500

    def __init__(self, props: EditTermDialogProps) -> None:
        """Initialize edit term dialog.

        Args:
            props: ダイアログプロパティ
        """
        self._props = props
        self._dialog: ft.AlertDialog | None = None

        # フォームフィールド
        self._key_field: ft.TextField | None = None
        self._title_field: ft.TextField | None = None
        self._description_field: ft.TextField | None = None
        self._status_dropdown: ft.Dropdown | None = None
        self._source_url_field: ft.TextField | None = None
        self._synonyms_field: ft.TextField | None = None

        # タグ選択
        self._selected_tag_ids: set[str] = set()
        self._tag_dropdown: ft.Dropdown | None = None
        self._selected_tags_container: ft.Row | None = None

        # エラーバナー（動的に表示/非表示）
        self._error_banner: ft.Container | None = None
        self._form_column: ft.Column | None = None

        # 既存タグを初期化
        self._initialize_tags()

        self._build_dialog()

    def _initialize_tags(self) -> None:
        """既存の用語のタグを初期化する。"""
        if not self._props.all_tags:
            return

        # term_dataからタグを取得
        term_tags = self._props.term_data.get("tags", [])
        for tag in term_tags:
            tag_name = tag.get("name") if isinstance(tag, dict) else getattr(tag, "name", None)
            if tag_name:
                self._selected_tag_ids.add(tag_name)

    def _build_dialog(self) -> None:
        """ダイアログを構築する。"""
        term_data = self._props.term_data

        # キーフィールド（必須、ユニーク）
        self._key_field = ft.TextField(
            label="キー *",
            hint_text="例: LLM, RAG, SDLC",
            value=term_data.get("key", ""),
            max_length=self.MAX_KEY_LENGTH,
            autofocus=True,
            helper_text="英数字とアンダースコアを推奨（一意である必要があります）",
        )

        # タイトルフィールド（必須）
        self._title_field = ft.TextField(
            label="タイトル *",
            hint_text="例: Large Language Model",
            value=term_data.get("title", ""),
            max_length=self.MAX_TITLE_LENGTH,
        )

        # 説明フィールド
        self._description_field = ft.TextField(
            label="説明",
            hint_text="用語の定義や説明を入力してください",
            value=term_data.get("description", "") or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            max_length=self.MAX_DESCRIPTION_LENGTH,
        )

        # ステータスドロップダウン
        current_status = term_data.get("status", TermStatus.DRAFT.value)
        if isinstance(current_status, TermStatus):
            current_status = current_status.value

        self._status_dropdown = ft.Dropdown(
            label="ステータス",
            options=[
                ft.dropdown.Option(key=TermStatus.DRAFT.value, text="草案"),
                ft.dropdown.Option(key=TermStatus.APPROVED.value, text="承認済み"),
                ft.dropdown.Option(key=TermStatus.DEPRECATED.value, text="非推奨"),
            ],
            value=current_status,
        )

        # 出典URLフィールド
        self._source_url_field = ft.TextField(
            label="出典URL",
            hint_text="https://example.com/definition",
            value=term_data.get("source_url", "") or "",
            max_length=self.MAX_URL_LENGTH,
        )

        # 同義語フィールド（カンマ区切り）
        synonyms = term_data.get("synonyms", [])
        synonyms_text = ", ".join(synonyms) if isinstance(synonyms, list) else ""
        self._synonyms_field = ft.TextField(
            label="同義語",
            hint_text="カンマ区切りで複数入力可能（例: LLM, 大規模言語モデル）",
            value=synonyms_text,
            helper_text="別名や略称を入力してください",
        )

        # タグ選択UI
        tag_controls: list[ft.Control] = []
        if self._props.all_tags:
            self._tag_dropdown = ft.Dropdown(
                label="タグを追加",
                hint_text="タグを選択...",
                options=[ft.dropdown.Option(key=tag.name, text=tag.name) for tag in self._props.all_tags],
                on_change=self._on_tag_select,
            )
            self._selected_tags_container = ft.Row(wrap=True, spacing=8, run_spacing=8)

            tag_controls = [
                ft.Divider(height=1),
                ft.Text("タグ", weight=ft.FontWeight.BOLD, size=14),
                self._tag_dropdown,
                self._selected_tags_container,
            ]

        # エラーバナー（初期状態は非表示）
        self._error_banner = ft.Container(
            visible=False,
            bgcolor=ft.Colors.with_opacity(0.1, get_error_color()),
            border=ft.border.all(2, get_error_color()),
            padding=12,
            border_radius=8,
        )

        # フォームカラム（エラーバナーを含む）
        self._form_column = ft.Column(
            controls=[
                self._error_banner,
                self._key_field,
                self._title_field,
                self._description_field,
                self._status_dropdown,
                self._source_url_field,
                self._synonyms_field,
                *tag_controls,
                ft.Container(height=8),
                ft.Text(
                    "* 必須項目",
                    size=12,
                    color=get_text_secondary_color(),
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        # 初期タグバッジを表示
        self._update_selected_tags_display()

        # ダイアログ本体
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("用語を編集"),
            content=ft.Container(
                content=self._form_column,
                width=500,
                height=600,
            ),
            actions=[
                ft.TextButton(
                    "キャンセル",
                    on_click=lambda _: self._handle_cancel(),
                ),
                ft.ElevatedButton(
                    "更新",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self._handle_update(),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    @property
    def dialog(self) -> ft.AlertDialog:
        """ダイアログコントロールを取得する。

        Returns:
            AlertDialogコントロール
        """
        return self._dialog  # type: ignore[return-value]

    def _validate_form(self) -> tuple[bool, str]:
        """フォームをバリデーションする。

        Returns:
            (成功フラグ, エラーメッセージ)のタプル
        """
        # 必須フィールドの検証
        key_error = self._validate_required_field(self._key_field, "キー", self.MAX_KEY_LENGTH)
        if key_error:
            return False, key_error

        title_error = self._validate_required_field(self._title_field, "タイトル", self.MAX_TITLE_LENGTH)
        if title_error:
            return False, title_error

        # 説明の検証（任意だが長さチェック）
        if self._description_field and self._description_field.value:
            description = self._description_field.value.strip()
            if len(description) > self.MAX_DESCRIPTION_LENGTH:
                return False, f"説明は{self.MAX_DESCRIPTION_LENGTH}文字以内で入力してください"

        # URLの検証（任意だが形式チェック）
        url_error = self._validate_url()
        if url_error:
            return False, url_error

        return True, ""

    def _validate_required_field(
        self,
        field: ft.TextField | None,
        field_name: str,
        max_length: int,
    ) -> str | None:
        """必須フィールドをバリデーションする。

        Args:
            field: 検証対象のテキストフィールド
            field_name: フィールド名（エラーメッセージ用）
            max_length: 最大文字数

        Returns:
            エラーメッセージ（正常時はNone）
        """
        if not field or not field.value or not field.value.strip():
            return f"{field_name}は必須です"

        value = field.value.strip()
        if len(value) > max_length:
            return f"{field_name}は{max_length}文字以内で入力してください"

        return None

    def _validate_url(self) -> str | None:
        """URLフィールドをバリデーションする。

        Returns:
            エラーメッセージ（正常時はNone）
        """
        max_url_length = 500

        if not self._source_url_field or not self._source_url_field.value:
            return None

        url = self._source_url_field.value.strip()
        if len(url) > max_url_length:
            return f"URLは{max_url_length}文字以内で入力してください"
        if not url.startswith(("http://", "https://")):
            return "URLはhttp://またはhttps://で始まる必要があります"

        return None

    def _handle_update(self) -> None:
        """更新ボタンのクリックをハンドリングする。"""
        # バリデーション
        is_valid, error_message = self._validate_form()
        if not is_valid:
            # エラーバナーを表示（既存のフォーム内容は保持）
            self._show_error(error_message)
            return

        # バリデーション成功時はエラーを非表示
        self._hide_error()

        # フォームデータの収集
        description_value = (
            self._description_field.value.strip() if self._description_field and self._description_field.value else None
        )
        source_url_value = (
            self._source_url_field.value.strip() if self._source_url_field and self._source_url_field.value else None
        )

        form_data: dict[str, object] = {
            "key": self._key_field.value.strip() if self._key_field and self._key_field.value else "",
            "title": self._title_field.value.strip() if self._title_field and self._title_field.value else "",
            "description": description_value,
            "status": self._status_dropdown.value if self._status_dropdown else TermStatus.DRAFT.value,
            "source_url": source_url_value,
        }

        # 同義語の処理（カンマ区切り）
        if self._synonyms_field and self._synonyms_field.value:
            synonyms_text = self._synonyms_field.value.strip()
            synonyms = [s.strip() for s in synonyms_text.split(",") if s.strip()]
            form_data["synonyms"] = synonyms
        else:
            form_data["synonyms"] = []

        # タグIDの処理
        if self._props.all_tags:
            tag_ids = [str(tag.id) for tag in self._props.all_tags if tag.name in self._selected_tag_ids]
            form_data["tag_ids"] = tag_ids
        else:
            form_data["tag_ids"] = []

        # コールバック呼び出し
        self._props.on_update(form_data)

    def _handle_cancel(self) -> None:
        """キャンセルボタンのクリックをハンドリングする。"""
        if self._props.on_cancel:
            self._props.on_cancel()

    def _show_error(self, error_message: str) -> None:
        """エラーバナーを表示する。

        Args:
            error_message: エラーメッセージ
        """
        if self._error_banner:
            self._error_banner.content = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=get_error_color(), size=24),
                    ft.Text(
                        error_message,
                        color=get_error_color(),
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        expand=True,
                    ),
                ],
                spacing=8,
            )
            self._error_banner.visible = True

            # 重複キーエラーの場合、キーフィールドにエラー表示を追加
            if "用語キー" in error_message and self._key_field:
                self._key_field.error_text = "このキーは既に使用されています"
                self._key_field.border_color = get_error_color()

            if self._dialog:
                with suppress(AssertionError):
                    self._dialog.update()

    def _hide_error(self) -> None:
        """エラーバナーを非表示にする。"""
        if self._error_banner:
            self._error_banner.visible = False

            # キーフィールドのエラー表示をクリア
            if self._key_field:
                self._key_field.error_text = None
                self._key_field.border_color = None

            if self._dialog:
                with suppress(AssertionError):
                    self._dialog.update()

    def show_error(self, error_message: str) -> None:
        """エラーメッセージを表示する（外部から呼び出し可能）。

        Args:
            error_message: 表示するエラーメッセージ
        """
        self._show_error(error_message)

    # _on_tag_select と _update_selected_tags_display は TagSelectorMixin で提供
