"""Memo Presenter Layer.

【責務】
    Presenter層はMVPパターンにおける「Presenter」の役割を担う。
    View層から表示用ロジックを切り出し、UI構築・更新を担当する。

    - データのフォーマット変換（日付→文字列、UUID→文字列）
    - コンポーネント用データモデルの生成（MemoCardData等）
    - UI要素の生成（純粋関数として提供）
    - 既存UI要素の差分更新（安全な例外ハンドリング付き）
    - 表示用メッセージの提供（ステータス別空メッセージ等）
    - ステータスバッジの生成（色・ラベルのマッピング）
    - 詳細パネル・空パネルの構築
    - 入力バリデーション（検索クエリ等）

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
    - データクラスによる型安全なコンポーネント連携

【アーキテクチャ上の位置づけ】
    View → Presenter.create_xxx_data()  # データクラス生成
         → Presenter.build_xxx()         # UI要素生成
         → Presenter.update_xxx()        # UI更新
         → Presenter.format_xxx()        # フォーマット
         → Presenter.validate_xxx()      # バリデーション
         → Presenter.get_xxx_message()   # メッセージ取得

【提供する関数カテゴリ】
    1. データクラス生成
        - create_memo_card_data(): MemoCardData生成
        - create_action_bar_data(): ActionBarData生成
        - create_status_tabs_data(): StatusTabsData生成
        - create_filter_data(): FilterData生成
        - create_memo_list_data(): MemoListData生成

    2. フォーマット変換
        - format_datetime(): 日付→表示文字列
        - format_memo_date_short(): 日付→短縮形式
        - truncate_content(): コンテンツ切り詰め
        - memo_id_to_str(): UUID→文字列

    3. バリデーション
        - validate_search_query(): 検索クエリ検証

    4. UI要素生成
        - build_status_badge(): ステータスバッジ
        - build_detail_metadata(): メタデータ行
        - build_detail_actions(): アクションボタン群
        - build_detail_panel(): 詳細パネル全体
        - build_empty_detail_panel(): 空状態パネル

    5. UI更新
        - update_detail_panel_content(): 詳細パネル差分更新

    6. メッセージ提供
        - get_empty_message_for_status(): ステータス別空メッセージ
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import flet as ft
from loguru import logger

from models import MemoStatus

from .components.action_bar import (
    DEFAULT_SEARCH_PLACEHOLDER,
    MIN_SEARCH_LENGTH,
    ActionBarData,
)
from .components.filters import FilterConfig, FilterData
from .components.memo_card import (
    DEFAULT_MEMO_TITLE,
    MAX_CONTENT_PREVIEW_LENGTH,
    MemoCardData,
    StatusBadgeData,
)
from .components.memo_list import MemoListData
from .components.shared.constants import DEFAULT_DATE_TEXT
from .components.status_tabs import StatusTabsData, TabData

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from models import MemoRead


# ========================================
# データクラス生成関数
# ========================================


def create_memo_card_data(
    memo: MemoRead,
    *,
    is_selected: bool = False,
    on_click: Callable[[], None] | None = None,
    show_badge: bool = True,
) -> MemoCardData:
    """MemoReadからMemoCardDataを生成する。

    データ変換・フォーマットを実行し、コンポーネントが直接表示できる形に整形する。

    Args:
        memo: 元のメモデータ
        is_selected: 選択状態
        on_click: クリック時のコールバック
        show_badge: バッジ表示有無

    Returns:
        整形済みのMemoCardData
    """
    # タイトル整形
    title = memo.title.strip() if memo.title else DEFAULT_MEMO_TITLE

    # コンテンツ切り詰め
    content_preview = truncate_content(memo.content, MAX_CONTENT_PREVIEW_LENGTH)

    # 日付整形
    formatted_date = format_memo_date_short(getattr(memo, "created_at", None))

    # バッジデータ生成
    badge_data = _create_status_badge_data(memo.status) if show_badge else None

    return MemoCardData(
        memo_id=memo.id,
        title=title,
        content_preview=content_preview,
        formatted_date=formatted_date,
        badge_data=badge_data,
        is_selected=is_selected,
        on_click=on_click,
    )


def create_action_bar_data(
    *,
    title: str = "メモ",
    subtitle: str = "思考とアイデアを記録し、AIでタスクに変換",
    search_placeholder: str = DEFAULT_SEARCH_PLACEHOLDER,
    on_create_memo: Callable[[], None] | None = None,
    on_search: Callable[[str], None] | None = None,
) -> ActionBarData:
    """ActionBarDataを生成する。

    Args:
        title: タイトル
        subtitle: サブタイトル
        search_placeholder: 検索プレースホルダー
        on_create_memo: 新規作成コールバック
        on_search: 検索コールバック

    Returns:
        ActionBarData
    """
    return ActionBarData(
        title=title,
        subtitle=subtitle,
        search_placeholder=search_placeholder,
        on_create_memo=on_create_memo,
        on_search=on_search,
    )


def create_status_tabs_data(
    *,
    active_status: MemoStatus,
    memo_counts: dict[MemoStatus, int],
    on_tab_change: Callable[[MemoStatus], None] | None = None,
) -> StatusTabsData:
    """StatusTabsDataを生成する。

    Args:
        active_status: アクティブなステータス
        memo_counts: ステータス毎の件数
        on_tab_change: タブ切り替えコールバック

    Returns:
        StatusTabsData
    """
    tab_definitions = [
        (MemoStatus.INBOX, "Inbox", ft.Icons.INBOX),
        (MemoStatus.ACTIVE, "アクティブ", ft.Icons.AUTO_AWESOME),
        (MemoStatus.IDEA, "アイデア", ft.Icons.LIGHTBULB),
        (MemoStatus.ARCHIVE, "アーカイブ", ft.Icons.ARCHIVE),
    ]

    tabs = tuple(
        TabData(
            status=status,
            label=label,
            icon=icon,
            count=memo_counts.get(status, 0),
            is_active=(status == active_status),
        )
        for status, label, icon in tab_definitions
    )

    return StatusTabsData(tabs=tabs, on_tab_change=on_tab_change)


def create_filter_data(
    *,
    show_date_filter: bool = True,
    show_ai_status_filter: bool = True,
    show_tag_filter: bool = False,
    on_filter_change: Callable[[dict[str, object]], None] | None = None,
) -> FilterData:
    """FilterDataを生成する。

    Args:
        show_date_filter: 日付フィルタ表示
        show_ai_status_filter: AIフィルタ表示
        show_tag_filter: タグフィルタ表示
        on_filter_change: フィルタ変更コールバック

    Returns:
        FilterData
    """
    config = FilterConfig(
        show_date_filter=show_date_filter,
        show_ai_status_filter=show_ai_status_filter,
        show_tag_filter=show_tag_filter,
    )
    return FilterData(config=config, on_filter_change=on_filter_change)


def create_memo_list_data(
    memos: list[MemoRead],
    *,
    selected_memo_id: UUID | None = None,
    on_memo_click: Callable[[UUID], None] | None = None,
    empty_message: str | None = None,
) -> MemoListData:
    """MemoListDataを生成する。

    Args:
        memos: メモリスト
        selected_memo_id: 選択中のメモID
        on_memo_click: メモクリックコールバック
        empty_message: 空メッセージ

    Returns:
        MemoListData
    """

    def create_click_handler(memo_id: UUID) -> Callable[[], None]:
        """クリックハンドラーを生成（クロージャで値をキャプチャ）"""
        return lambda: on_memo_click(memo_id) if on_memo_click else None

    cards = tuple(
        create_memo_card_data(
            memo,
            is_selected=(memo.id == selected_memo_id),
            on_click=create_click_handler(memo.id) if on_memo_click else None,
        )
        for memo in memos
    )

    return MemoListData(cards=cards, empty_message=empty_message)


def _create_status_badge_data(status: MemoStatus) -> StatusBadgeData:
    """ステータスからバッジデータを生成する（内部関数）。

    Args:
        status: メモステータス

    Returns:
        StatusBadgeData
    """
    badge_map = {
        MemoStatus.INBOX: StatusBadgeData(text="新規", color=ft.Colors.BLUE_100, icon=ft.Icons.FIBER_NEW),
        MemoStatus.ACTIVE: StatusBadgeData(text="進行中", color=ft.Colors.GREEN_100, icon=ft.Icons.PLAY_ARROW),
        MemoStatus.IDEA: StatusBadgeData(text="アイデア", color=ft.Colors.YELLOW_100, icon=ft.Icons.LIGHTBULB),
        MemoStatus.ARCHIVE: StatusBadgeData(text="保管", color=ft.Colors.GREY_300, icon=ft.Icons.ARCHIVE),
    }
    return badge_map.get(status, StatusBadgeData(text="メモ", color=ft.Colors.GREY_100))


# ========================================
# フォーマット関数
# ========================================


def format_memo_date_short(created_at: datetime | None) -> str:
    """メモ作成日を短縮形式でフォーマット（カード表示用）。

    Args:
        created_at: 作成日時

    Returns:
        フォーマット済み日付文字列（例: "2025/01/15"）
    """
    return created_at.strftime("%Y/%m/%d") if created_at else DEFAULT_DATE_TEXT


def truncate_content(content: str, max_length: int = MAX_CONTENT_PREVIEW_LENGTH) -> str:
    """コンテンツを指定長で切り詰める。

    Args:
        content: 元のコンテンツ
        max_length: 最大文字数

    Returns:
        切り詰められたコンテンツ（必要に応じて"..."付き）
    """
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


# ========================================
# バリデーション関数
# ========================================


def validate_search_query(query: str) -> tuple[bool, str | None]:
    """検索クエリをバリデーションする。

    Args:
        query: 検索クエリ文字列

    Returns:
        (検証結果, エラーメッセージ) のタプル
        検証成功時は (True, None)
        検証失敗時は (False, エラーメッセージ)
    """
    if not query:
        return True, None  # 空クエリは許可（全件表示）

    if len(query) < MIN_SEARCH_LENGTH:
        return False, f"検索は{MIN_SEARCH_LENGTH}文字以上で入力してください"

    return True, None


# ========================================
# UI要素生成関数（既存）
# ========================================


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
