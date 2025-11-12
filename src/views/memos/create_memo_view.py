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

from models import MemoStatus
from views.shared.base_view import BaseView

from .components.create_form import CreateForm, FormCallbacks
from .components.create_header import CreateHeader


@dataclass(slots=True)
class CreateMemoState:
    """メモ作成ページの一時入力状態を保持する。

    Attributes:
        title: メモのタイトル
        content: 本文
        status: メモのステータス
        tags: 選択されたタグ名のリスト（暫定）
        active_tab: 編集/プレビュー切替
    """

    title: str = ""
    content: str = ""
    status: MemoStatus = MemoStatus.INBOX
    tags: list[str] = field(default_factory=list)
    active_tab: Literal["edit", "preview"] = "edit"


class CreateMemoView(BaseView):
    """メモ作成用のフルスクリーンビュー。"""

    def __init__(self, page: ft.Page) -> None:  # type: ignore[name-defined]
        super().__init__(page)
        self.state_local = CreateMemoState()

        # UI controls (late init)
        self._header: CreateHeader | None = None
        self._form: CreateForm | None = None

        self.did_mount()

    # BaseView hook
    def build_content(self) -> ft.Control:
        """メモ作成ページのUIを構築する。"""
        header = self._build_header()
        body = self._build_body()
        return ft.Column(controls=[header, body], spacing=0, expand=True)

    def _build_header(self) -> ft.Control:
        """固定ヘッダー（戻る/タイトル/キャンセル/保存）。"""
        self._header = CreateHeader(
            on_back=self._handle_back,
            on_cancel=self._handle_cancel,
            on_save=self._handle_save,
            can_save=self._can_save(),
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
                        border=ft.border.only(left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
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
        """右カラム: タグ選択(暫定)とヒント。"""
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

        # タグ選択 (後続で ApplicationService と統合)
        # TODO: タグ一覧を ApplicationService から取得し、選択UIへ反映する。
        #       - 取得: tag_app.get_all() 等（未統合）
        #       - 状態: self.state_local.tags に保持
        #       - 保存: _handle_save() で tags を一緒に渡す
        tags_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("タグ", weight=ft.FontWeight.BOLD),
                        ft.Text("タグ機能は後続で統合予定", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                    spacing=6,
                ),
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
        self.state_local.content = value
        # TODO: Ctrl+Enter で保存のキーハンドリングを追加（TextField.on_keyboard_event）
        #       - 重複送信防止のため、保存中は無効化
        self._update_save_button()
        # プレビュー更新は CreateForm 側が担当
        self.safe_update()

    def _can_save(self) -> bool:
        return bool(self.state_local.content.strip())

    def _update_save_button(self) -> None:
        # ヘッダーの保存ボタンの状態を直接更新
        if self._header is not None:
            if self._can_save():
                self._header.enable_save()
            else:
                self._header.disable_save()
        else:
            # フォールバック: 画面全体を更新
            try:
                self.safe_update()
            except Exception as e:
                logger.debug(f"update save button ignored: {e}")

    def _handle_back(self) -> None:
        self.page.go("/memos")

    def _handle_cancel(self) -> None:
        # 入力がある場合の確認は後続で実装
        self.page.go("/memos")

    def _handle_save(self) -> None:
        if not self._can_save():
            self.show_snack_bar("内容を入力してください", bgcolor=ft.Colors.ERROR)
            return
        title = self.state_local.title.strip() or "無題のメモ"
        content = self.state_local.content.strip()
        status = self.state_local.status

        # TODO: ApplicationService 統合
        #  1) controller.create_memo(title, content, status, tags=self.state_local.tags)
        #  2) 成功: MemosView 側 state 反映 (upsert or 再読込) / 作成メモ選択
        #  3) 失敗: notify_error でユーザ通知
        #  4) 保存ボタン連打対策（保存中はdisabled）
        # 現状は Controller 経由の永続化は未実装のため通知のみ
        logger.info(f"Create memo requested: status={status}, title_length={len(title)}, content_length={len(content)}")
        self.show_success_snackbar("メモを作成しました（暫定）")
        self.page.go("/memos")


