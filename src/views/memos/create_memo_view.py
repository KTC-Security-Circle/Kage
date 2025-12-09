"""Create Memo View.

テンプレートの CreateMemoScreen.tsx を参考にした、メモ作成用のフルスクリーンビュー。

設計方針:
- BaseView を継承し、ヘッダー(戻る/キャンセル/保存) + 2カラム(フォーム/ヒント)で構成
- 初期段階では永続化は行わず、保存アクションは Controller の create_memo 呼び出し骨格に接続
- Markdown プレビューは最小限の疑似レンダリングで提供（将来 markdown-it-py 等へ差し替え）

注意:
- ルーティングは layout.py にて "/memos/create" を本ビューに紐付ける
- MemosView からは page.go("/memos/create") で遷移
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import flet as ft
from loguru import logger

from logic.application.memo_application_service import MemoApplicationService
from logic.application.tag_application_service import TagApplicationService
from models import MemoStatus
from views.shared.base_view import BaseView, BaseViewProps
from views.shared.components import Header, HeaderButtonData
from views.theme import get_dark_color, get_light_color, get_outline_color

from .components.create_form import CreateForm, FormCallbacks
from .components.tag_selector import TagSelector, TagSelectorProps


@dataclass(slots=True)
class CreateMemoState:
    """メモ作成ページの一時入力状態を保持する。

    Attributes:
        title: メモのタイトル
        content: 本文
        status: メモのステータス
        tags: 選択されたタグ名のリスト
        all_tags: 全タグリスト（タグ名からUUIDへの変換に使用）
        active_tab: 編集/プレビュー切替
    """

    title: str = ""
    content: str = ""
    status: MemoStatus = MemoStatus.INBOX
    tags: list[str] = field(default_factory=list)
    all_tags: list = field(default_factory=list)
    active_tab: Literal["edit", "preview"] = "edit"


class CreateMemoView(BaseView):
    """メモ作成用のフルスクリーンビュー。"""

    def __init__(
        self,
        props: BaseViewProps,
        *,
        memo_app: MemoApplicationService | None = None,
        tag_app: TagApplicationService | None = None,
    ) -> None:
        super().__init__(props)
        self._memo_app = memo_app or self.apps.get_service(MemoApplicationService)
        self._tag_app = tag_app or self.apps.get_service(TagApplicationService)
        self.state_local = CreateMemoState()

        # UI controls (late init)
        self._header: Header | None = None
        self._form: CreateForm | None = None
        self._tag_selector: TagSelector | None = None

        self.did_mount()
        self._load_tags()

    # BaseView hook
    def build_content(self) -> ft.Control:
        """メモ作成ページのUIを構築する。"""
        header = self._build_header()
        body = self._build_body()
        return ft.Column(controls=[header, body], spacing=0, expand=True)

    def _build_header(self) -> ft.Control:
        """固定ヘッダー（戻る/タイトル/キャンセル/保存）。"""
        self._header = self.create_header(
            title="新しいメモを作成",
            subtitle="マークダウン形式で記述できます",
            show_search=False,
            leading_buttons=[
                HeaderButtonData(
                    label="戻る",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self._handle_back,
                    is_outlined=True,
                    is_primary=False,
                ),
            ],
            action_buttons=[
                HeaderButtonData(
                    label="キャンセル",
                    icon=None,
                    on_click=self._handle_cancel,
                    is_outlined=True,
                    is_primary=False,
                ),
                HeaderButtonData(
                    label="保存",
                    icon=ft.Icons.SAVE,
                    on_click=self._handle_save,
                    is_primary=True,
                    button_id="save_button",
                    disabled=not self._can_save(),
                ),
            ],
        )
        return self._header

    def _build_body(self) -> ft.Control:
        """メイン2カラムの本体部分を構築する。"""
        left = self._build_left_form()
        right = self._build_right_sidebar()
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(content=left, expand=True, padding=ft.padding.all(12)),
                    ft.Container(
                        content=right,
                        width=320,
                        padding=ft.padding.only(left=12, top=12, bottom=12),
                        border=ft.border.only(left=ft.BorderSide(1, get_outline_color())),
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
        )

    def _build_left_form(self) -> ft.Control:
        """左カラム: 基本情報 + 本文編集/プレビュー (CreateFormコンポーネント利用)。"""
        callbacks = FormCallbacks(
            on_title_change=lambda v: self._update_title(v),
            on_status_change=lambda s: self._update_status(s.value),
            on_content_change=lambda v: self._update_content(v),
            on_tab_change=lambda t: self._on_tab_change(0 if t == "edit" else 1),
        )
        self._form = CreateForm(
            title=self.state_local.title,
            status=self.state_local.status,
            content=self.state_local.content,
            active_tab=self.state_local.active_tab,
            callbacks=callbacks,
        )
        return self._form

    def _build_right_sidebar(self) -> ft.Control:
        """右カラム: タグ選択とヒント。"""
        hint = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("💡 ヒント", weight=ft.FontWeight.BOLD),
                        ft.Text("• まずは INBOX に保存し、後で整理できます", size=12),
                        ft.Text("• プレビュータブで表示を確認できます", size=12),
                        ft.Text("• 長文は見出しを使って構造化しましょう", size=12),
                    ],
                    spacing=6,
                ),
                padding=ft.padding.all(12),
            )
        )

        # タグ選択UI
        try:
            all_tags = self._tag_app.get_all_tags()
        except Exception:
            logger.warning("Failed to load tags for CreateMemoView")
            all_tags = []

        self._tag_selector = TagSelector(
            TagSelectorProps(
                all_tags=all_tags,
                selected_tag_names=self.state_local.tags,
                on_tag_toggle=self._handle_tag_toggle,
            )
        )

        tags_card = ft.Card(
            content=ft.Container(
                content=self._tag_selector,
                padding=ft.padding.all(12),
            )
        )

        return ft.Column([tags_card, hint], spacing=12)

    # -------------------------
    # イベントハンドラ/内部ロジック
    # -------------------------
    def _on_tab_change(self, selected_index: int) -> None:
        self.state_local.active_tab = "edit" if selected_index == 0 else "preview"
        # プレビュー更新は CreateForm 側で処理されるためここでは不要
        self.safe_update()

    def _update_title(self, value: str) -> None:
        self.state_local.title = value
        self._update_save_button()

    def _update_status(self, value: str) -> None:
        try:
            self.state_local.status = MemoStatus(value)
        except Exception:
            self.state_local.status = MemoStatus.INBOX
        self._update_save_button()

    def _update_content(self, value: str) -> None:
        """コンテンツ更新時のハンドラ。"""
        self.state_local.content = value
        self._update_save_button()

    def _can_save(self) -> bool:
        return bool(self.state_local.content.strip())

    def _update_save_button(self) -> None:
        # ヘッダーの保存ボタンの状態を直接更新
        if self._header is not None:
            if self._can_save():
                self._header.enable_button("save_button")
            else:
                self._header.disable_button("save_button")

    def _handle_back(self) -> None:
        self.page.go("/memos")

    def _handle_cancel(self) -> None:
        # 入力がある場合の確認は後続で実装
        self.page.go("/memos")

    def _handle_tag_toggle(self, tag_name: str) -> None:
        """タグのトグル処理。

        Args:
            tag_name: トグルするタグ名
        """
        if tag_name in self.state_local.tags:
            self.state_local.tags.remove(tag_name)
        else:
            self.state_local.tags.append(tag_name)

        # タグセレクターを更新
        if self._tag_selector is not None:
            try:
                all_tags = self._tag_app.get_all_tags()
                self._tag_selector.set_props(
                    TagSelectorProps(
                        all_tags=all_tags,
                        selected_tag_names=self.state_local.tags,
                        on_tag_toggle=self._handle_tag_toggle,
                    )
                )
            except Exception:
                logger.warning("Failed to update tag selector")

    def _load_tags(self) -> None:
        """タグ一覧を読み込む。"""
        try:
            all_tags = self._tag_app.get_all_tags()
            self.state_local.all_tags = all_tags
            logger.debug(f"Loaded {len(all_tags)} tags for CreateMemoView")
        except Exception:
            logger.warning("Failed to load tags in CreateMemoView")

    def _handle_save(self) -> None:
        if not self._can_save():
            is_dark = getattr(self.page, "theme_mode", ft.ThemeMode.LIGHT) == ft.ThemeMode.DARK
            error_color = get_dark_color("error") if is_dark else get_light_color("error")
            self.show_snack_bar("内容を入力してください", bgcolor=error_color)
            return
        title = self.state_local.title.strip() or "無題のメモ"
        content = self.state_local.content.strip()
        status = self.state_local.status
        selected_tag_names = self.state_local.tags

        # タグ名からUUIDに変換
        tag_ids = [tag.id for tag in self.state_local.all_tags if tag.name in selected_tag_names]

        def _save() -> None:
            if self._header is not None:
                self._header.disable_button("save_button")
            try:
                created = self._memo_app.create(
                    title=title,
                    content=content,
                    status=status,
                    tag_ids=tag_ids,
                )
                logger.info(
                    "Memo created via CreateMemoView: id=%s, status=%s, tags=%s",
                    created.id,
                    created.status,
                    selected_tag_names,
                )
            except Exception:
                if self._header is not None:
                    self._header.enable_button("save_button")
                raise

            self.show_success_snackbar("メモを作成しました")
            self.page.go("/memos")

        self.with_loading(_save, user_error_message="メモの作成に失敗しました")
