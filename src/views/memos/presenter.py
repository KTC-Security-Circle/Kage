"""Memo Presenter Layer.

【責務】
    Presenter層はMVPパターンにおける「Presenter」の役割を担う。
    View層から表示用ロジックを切り出し、UI構築・更新を担当する。

    - データのフォーマット変換（日付→文字列、UUID→文字列）
    - UI要素の生成（純粋関数として提供）
    - 既存UI要素の差分更新（安全な例外ハンドリング付き）
    - 表示用メッセージの提供（ステータス別空メッセージ等）
    - ステータスバッジの生成（色・ラベルのマッピング）
    - 詳細パネル・空パネルの構築

【責務外（他層の担当）】
    - 状態の保持 → State
    - イベントハンドリング → View
    - データの取得 → Controller
    - レイアウトの配置 → View

【設計上の特徴】
    - 全関数が副作用を最小化（純粋関数または安全な更新）
    - Viewから呼び出される関数のみ公開
    - 型安全なCallable引数（イベントハンドラー）
    - ログ出力による観測性（更新失敗時）

【アーキテクチャ上の位置づけ】
    View → Presenter.build_xxx()
         → Presenter.update_xxx()
         → Presenter.format_xxx()
         → Presenter.get_xxx_message()

【提供する関数カテゴリ】
    1. フォーマット変換
        - format_datetime(): 日付→表示文字列
        - memo_id_to_str(): UUID→文字列

    2. UI要素生成
        - build_status_badge(): ステータスバッジ
        - build_detail_metadata(): メタデータ行
        - build_detail_actions(): アクションボタン群
        - build_detail_panel(): 詳細パネル全体
        - build_empty_detail_panel(): 空状態パネル

    3. UI更新
        - update_detail_panel_content(): 詳細パネル差分更新

    4. メッセージ提供
        - get_empty_message_for_status(): ステータス別空メッセージ
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models import MemoStatus

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from models import MemoRead


def format_datetime(value: object) -> str:
    """日付表示を安全に整形する。

    Args:
        value: datetime オブジェクトまたはその他の値

    Returns:
        整形された日付文字列。datetime以外や None はダッシュで返す。
    """
    return value.strftime("%Y年%m月%d日 %H:%M") if isinstance(value, datetime) else "—"


def build_status_badge(status: MemoStatus) -> ft.Container:
    """メモステータスバッジを構築する。

    Args:
        status: メモのステータス

    Returns:
        ステータスバッジコンテナ
    """
    label_map = {
        MemoStatus.INBOX: "Inbox",
        MemoStatus.ACTIVE: "Active",
        MemoStatus.IDEA: "Idea",
        MemoStatus.ARCHIVE: "Archived",
    }
    color_map = {
        MemoStatus.INBOX: ft.Colors.PRIMARY,
        MemoStatus.ACTIVE: ft.Colors.SECONDARY,
        MemoStatus.IDEA: ft.Colors.TERTIARY,
        MemoStatus.ARCHIVE: ft.Colors.OUTLINE_VARIANT,
    }
    text_color_map = {
        MemoStatus.ARCHIVE: ft.Colors.ON_SURFACE,
    }

    label = label_map.get(status, "Memo")
    bgcolor = color_map.get(status, ft.Colors.PRIMARY)
    text_color = text_color_map.get(status, ft.Colors.ON_PRIMARY)

    return ft.Container(
        content=ft.Text(label, size=12, color=text_color, weight=ft.FontWeight.BOLD),
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
        bgcolor=bgcolor,
        border_radius=12,
    )


def build_detail_metadata(created_text: str, updated_text: str) -> ft.Control:
    """詳細メタデータ行（作成日・更新日）を構築する。

    Args:
        created_text: 作成日の表示文字列
        updated_text: 更新日の表示文字列

    Returns:
        メタデータ行コントロール
    """
    return ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("作成日", style=ft.TextThemeStyle.BODY_SMALL, weight=ft.FontWeight.BOLD),
                    ft.Text(created_text, style=ft.TextThemeStyle.BODY_SMALL),
                ],
                spacing=4,
            ),
            ft.Column(
                controls=[
                    ft.Text("更新日", style=ft.TextThemeStyle.BODY_SMALL, weight=ft.FontWeight.BOLD),
                    ft.Text(updated_text, style=ft.TextThemeStyle.BODY_SMALL),
                ],
                spacing=4,
            ),
        ],
        spacing=32,
    )


def build_detail_actions(
    *,
    on_ai_suggestion: Callable,
    on_edit: Callable,
    on_delete: Callable,
) -> ft.Control:
    """詳細パネルのアクションボタンを構築する。

    Args:
        on_ai_suggestion: AI提案ボタンのコールバック
        on_edit: 編集ボタンのコールバック
        on_delete: 削除ボタンのコールバック

    Returns:
        アクションボタンコントロール
    """
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.AUTO_AWESOME, size=16),
                                ft.Text("AIでタスクを生成"),
                            ],
                            spacing=8,
                            tight=True,
                        ),
                        on_click=on_ai_suggestion,
                        expand=True,
                    ),
                ],
            ),
            ft.Row(
                controls=[
                    ft.OutlinedButton(
                        "編集",
                        icon=ft.Icons.EDIT,
                        on_click=on_edit,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "削除",
                        icon=ft.Icons.DELETE,
                        on_click=on_delete,
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
        ],
        spacing=8,
    )


def build_detail_panel(
    memo: MemoRead,
    *,
    on_ai_suggestion: Callable,
    on_edit: Callable,
    on_delete: Callable,
) -> ft.Container:
    """メモ詳細パネルを構築する。

    Args:
        memo: 表示するメモデータ
        on_ai_suggestion: AI提案ボタンのコールバック
        on_edit: 編集ボタンのコールバック
        on_delete: 削除ボタンのコールバック

    Returns:
        詳細パネルコンテナ
    """
    # 日付表示の安全な整形
    created_text = format_datetime(getattr(memo, "created_at", None))
    updated_text = format_datetime(getattr(memo, "updated_at", None))

    # メモ詳細カード
    detail_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    # ヘッダー
                    ft.Row(
                        controls=[
                            ft.Text(
                                memo.title or "無題のメモ",
                                style=ft.TextThemeStyle.HEADLINE_SMALL,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            build_status_badge(memo.status),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # 内容
                    ft.Container(
                        content=ft.Text(
                            memo.content,
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            selectable=True,
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        border_radius=8,
                    ),
                    # メタデータ
                    build_detail_metadata(created_text, updated_text),
                    # アクションボタン
                    build_detail_actions(
                        on_ai_suggestion=on_ai_suggestion,
                        on_edit=on_edit,
                        on_delete=on_delete,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.all(20),
        ),
    )

    return ft.Container(
        content=ft.Column(
            controls=[detail_card],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )


def build_empty_detail_panel() -> ft.Control:
    """空の詳細パネルを構築する。

    Returns:
        空の詳細パネルコントロール
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.DESCRIPTION, size=64, color=ft.Colors.OUTLINE),
                ft.Text(
                    "メモを選択して詳細を表示",
                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "左側のリストからメモを選択すると、\nここに詳細が表示されます。",
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


# --- UI更新ヘルパー関数 ---


def update_detail_panel_content(container: ft.Container, new_panel: ft.Container) -> None:
    """詳細パネルの内容を更新する。

    Args:
        container: 更新対象のコンテナ
        new_panel: 新しいパネル内容
    """
    container.content = new_panel.content
    try:
        container.update()
    except AssertionError as e:
        if "Control must be added to the page first" not in str(e):
            raise
        logger.warning(f"Skipping detail panel update: {e}")


# --- メッセージ提供関数 ---


def get_empty_message_for_status(status: MemoStatus | None) -> str:
    """ステータスに応じた空メッセージを取得する。

    Args:
        status: メモのステータス

    Returns:
        空メッセージ文字列
    """
    messages = {
        MemoStatus.INBOX: "Inboxメモはありません",
        MemoStatus.ACTIVE: "アクティブなメモはありません",
        MemoStatus.IDEA: "アイデアメモはありません",
        MemoStatus.ARCHIVE: "アーカイブされたメモはありません",
    }
    if status is None:
        return "メモはありません"
    return messages.get(status, "メモはありません")


# --- 型変換ヘルパー ---


def memo_id_to_str(memo_id: UUID | None) -> str | None:
    """メモIDを文字列に変換する。

    Args:
        memo_id: メモのUUID

    Returns:
        文字列化されたID、またはNone
    """
    return str(memo_id) if memo_id is not None else None
