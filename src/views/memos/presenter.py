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
        - create_action_bar_data(): HeaderData生成（汎用views.shared.components.HeaderData）
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

from models import AiSuggestionStatus, MemoStatus
from views.shared.components import HeaderButtonData, HeaderData
from views.theme import (
    get_error_color,
    get_on_primary_color,
    get_on_surface_color,
    get_outline_color,
    get_primary_color,
    get_status_color,
    get_surface_variant_color,
    get_text_secondary_color,
    get_warning_color,
)

from .components.filters import FilterConfig, FilterData
from .components.memo_card import DEFAULT_MEMO_TITLE, MAX_CONTENT_PREVIEW_LENGTH, MemoCardData, StatusBadgeData
from .components.shared.constants import DEFAULT_DATE_TEXT, DEFAULT_SEARCH_PLACEHOLDER, MIN_SEARCH_LENGTH
from .components.types import MemoListData

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from models import MemoRead

    from .state import AiSuggestedTask


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
) -> HeaderData:
    """HeaderDataを生成する（汎用HeaderData対応）。

    Args:
        title: タイトル
        subtitle: サブタイトル
        search_placeholder: 検索プレースホルダー
        on_create_memo: 新規作成コールバック
        on_search: 検索コールバック

    Returns:
        HeaderData
    """
    action_buttons = []
    if on_create_memo:
        action_buttons.append(
            HeaderButtonData(
                label="新しいメモ",
                icon=ft.Icons.ADD,
                on_click=on_create_memo,
                is_primary=True,
            )
        )

    return HeaderData(
        title=title,
        subtitle=subtitle,
        search_placeholder=search_placeholder,
        on_search=on_search,
        action_buttons=action_buttons if action_buttons else None,
        show_search=on_search is not None,
    )


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
        MemoStatus.INBOX: StatusBadgeData(text="新規", color=get_primary_color(), icon=ft.Icons.FIBER_NEW),
        MemoStatus.ACTIVE: StatusBadgeData(text="進行中", color=get_status_color("進行中"), icon=ft.Icons.PLAY_ARROW),
        MemoStatus.IDEA: StatusBadgeData(text="アイデア", color=get_warning_color(), icon=ft.Icons.LIGHTBULB),
        MemoStatus.ARCHIVE: StatusBadgeData(text="保管", color=get_outline_color(), icon=ft.Icons.ARCHIVE),
    }
    return badge_map.get(status, StatusBadgeData(text="メモ", color=get_outline_color()))


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
        MemoStatus.INBOX: get_primary_color(),
        MemoStatus.ACTIVE: get_status_color("進行中"),
        MemoStatus.IDEA: get_warning_color(),
        MemoStatus.ARCHIVE: get_outline_color(),
    }
    text_color_map = {
        MemoStatus.ARCHIVE: get_on_surface_color(),
    }

    label = label_map.get(status, "Memo")
    bgcolor = color_map.get(status, get_primary_color())
    text_color = text_color_map.get(status, get_on_primary_color())

    return ft.Container(
        content=ft.Text(
            label,
            theme_style=ft.TextThemeStyle.LABEL_SMALL,
            color=text_color,
            weight=ft.FontWeight.W_500,
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
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
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=get_text_secondary_color()),
                    ft.Text(
                        f"作成: {created_text}",
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=get_text_secondary_color(),
                    ),
                ],
                spacing=4,
            ),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.UPDATE, size=16, color=get_text_secondary_color()),
                    ft.Text(
                        f"更新: {updated_text}",
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=get_text_secondary_color(),
                    ),
                ],
                spacing=4,
            ),
        ],
        spacing=16,
    )


def build_detail_actions(
    *,
    on_edit: Callable,
    on_delete: Callable,
) -> ft.Control:
    """詳細パネルのアクションボタンを構築する。

    Args:
        on_edit: 編集ボタンのコールバック
        on_delete: 削除ボタンのコールバック

    Returns:
        アクションボタンコントロール
    """
    return ft.Row(
        controls=[
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                tooltip="編集",
                icon_size=20,
                icon_color=get_text_secondary_color(),
                on_click=on_edit,
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip="削除",
                icon_size=20,
                icon_color=get_error_color(),
                on_click=on_delete,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
    )


def build_detail_panel(
    memo: MemoRead,
    *,
    on_ai_suggestion: Callable,
    on_edit: Callable,
    on_delete: Callable,
    extra_sections: tuple[ft.Control, ...] | None = None,
) -> ft.Container:
    """メモ詳細パネルを構築する。

    Args:
        memo: 表示するメモデータ
        on_ai_suggestion: AI提案ボタンのコールバック
        on_edit: 編集ボタンのコールバック
        on_delete: 削除ボタンのコールバック
        extra_sections: 詳細カードの下に追加表示する追加セクション群

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
                                theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            build_status_badge(memo.status),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # 内容（Markdownレンダリング、コンテンツ量に応じた高さ）
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Markdown(
                                    value=memo.content,
                                    selectable=True,
                                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    on_tap_link=lambda _: None,
                                    fit_content=True,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=get_surface_variant_color(),
                        border_radius=8,
                        # 高さは指定せず、コンテンツに応じて自動調整
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

    column_controls: list[ft.Control] = [detail_card]
    if extra_sections:
        column_controls.extend(extra_sections)

    return ft.Container(
        content=ft.Column(
            controls=column_controls,
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
                ft.Icon(ft.Icons.DESCRIPTION, size=64, color=get_outline_color()),
                ft.Text(
                    "メモを選択して詳細を表示",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                    color=get_text_secondary_color(),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "左側のリストからメモを選択すると、\nここに詳細が表示されます。",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=get_text_secondary_color(),
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def build_ai_task_flow_panel(  # noqa: PLR0913
    memo: MemoRead,
    *,
    ai_status: AiSuggestionStatus,
    tasks: tuple[AiSuggestedTask, ...],
    selected_task_ids: set[str],
    editing_task_id: str | None,
    error_message: str | None = None,
    on_request_ai: Callable[[ft.ControlEvent], None] | None = None,
    on_retry_ai: Callable[[ft.ControlEvent], None] | None = None,
    on_mark_as_idea: Callable[[ft.ControlEvent], None] | None = None,
    on_toggle_task: Callable[[str], None] | None = None,
    on_start_edit: Callable[[str], None] | None = None,
    on_cancel_edit: Callable[[ft.ControlEvent | None], None] | None = None,
    on_edit_field_change: Callable[[str, str, str], None] | None = None,
    on_save_edit: Callable[[str], None] | None = None,
    on_delete_task: Callable[[str], None] | None = None,
    on_add_task: Callable[[ft.ControlEvent | None], None] | None = None,
    on_approve_tasks: Callable[[ft.ControlEvent | None], None] | None = None,
) -> ft.Control:
    """AI提案→タスク承認フローのカードを構築する。"""
    header_title, header_description = _ai_flow_header_copy(memo.status)
    status_badge = _build_ai_status_badge(ai_status)

    body_controls: list[ft.Control] = []
    match ai_status:
        case AiSuggestionStatus.NOT_REQUESTED:
            body_controls.append(
                ft.Text(
                    "InboxメモはMemoToTaskAgentにタスク生成を依頼する前段階です。AIに生成を許可するとアクティブ状態に遷移します。",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            )
            actions = ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "AIにタスク生成を依頼",
                        icon=ft.Icons.AUTO_AWESOME,
                        on_click=on_request_ai,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "アイデアとして残す",
                        icon=ft.Icons.LIGHTBULB,
                        on_click=on_mark_as_idea,
                        expand=True,
                    ),
                ],
                spacing=12,
            )
            body_controls.append(actions)
        case AiSuggestionStatus.PENDING:
            body_controls.append(
                ft.Row(
                    controls=[
                        ft.ProgressRing(width=32, height=32),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "MemoToTaskAgentがタスクを生成しています",
                                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                ),
                                ft.Text(
                                    "生成が完了すると承認待ちとしてActiveメモに切り替わります",
                                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=16,
                )
            )
        case AiSuggestionStatus.AVAILABLE:
            body_controls.extend(
                _build_available_tasks_section(
                    tasks=tasks,
                    selected_task_ids=selected_task_ids,
                    editing_task_id=editing_task_id,
                    on_toggle_task=on_toggle_task,
                    on_start_edit=on_start_edit,
                    on_cancel_edit=on_cancel_edit,
                    on_edit_field_change=on_edit_field_change,
                    on_save_edit=on_save_edit,
                    on_delete_task=on_delete_task,
                    on_add_task=on_add_task,
                )
            )
            footer_row = ft.Row(
                controls=[
                    ft.OutlinedButton(
                        "アイデアとしてマーク",
                        icon=ft.Icons.LIGHTBULB,
                        on_click=on_mark_as_idea,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE),
                                ft.Text(f"{len(selected_task_ids)}件を承認"),
                            ],
                            spacing=8,
                            tight=True,
                        ),
                        on_click=on_approve_tasks,
                        disabled=len(selected_task_ids) == 0,
                        expand=True,
                    ),
                ],
                spacing=12,
            )
            body_controls.append(footer_row)
        case AiSuggestionStatus.FAILED:
            body_controls.append(
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR)],
                        ),
                        ft.Text(
                            error_message or "MemoToTaskAgentでの生成に失敗しました。もう一度お試しください。",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "再試行",
                                    icon=ft.Icons.REFRESH,
                                    on_click=on_retry_ai,
                                    expand=True,
                                ),
                                ft.OutlinedButton(
                                    "アイデアとして残す",
                                    icon=ft.Icons.LIGHTBULB,
                                    on_click=on_mark_as_idea,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                    ],
                    spacing=8,
                )
            )
        case _:
            body_controls.append(
                ft.Text(
                    "AI提案は処理済みです。詳細はタスク一覧で確認できます。",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                )
            )

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        header_title,
                                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        header_description,
                                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=4,
                            ),
                            status_badge,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Divider(),
                    *body_controls,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(20),
        )
    )


def _ai_flow_header_copy(memo_status: MemoStatus) -> tuple[str, str]:
    if memo_status == MemoStatus.INBOX:
        return (
            "Inbox → Active への準備",
            "MemoToTaskAgentがタスク化する前に、ユーザーの許可を得る状態です。",
        )
    if memo_status == MemoStatus.ACTIVE:
        return (
            "Active メモの承認待ち",
            "生成中または承認を待つタスクをレビューしてください。",
        )
    if memo_status == MemoStatus.IDEA:
        return (
            "アイデアとして保存済み",
            "このメモはタスク化せず、インスピレーションとして保持されています。",
        )
    return (
        "アーカイブ済みメモ",
        "関連タスクが完了したため、履歴として残っています。",
    )


def _build_ai_status_badge(status: AiSuggestionStatus) -> ft.Control:
    label_map = {
        AiSuggestionStatus.NOT_REQUESTED: ("許可待ち", ft.Colors.SECONDARY_CONTAINER),
        AiSuggestionStatus.PENDING: ("生成中", ft.Colors.PRIMARY_CONTAINER),
        AiSuggestionStatus.AVAILABLE: ("承認待ち", ft.Colors.TERTIARY_CONTAINER),
        AiSuggestionStatus.REVIEWED: ("承認済み", ft.Colors.SECONDARY_CONTAINER),
        AiSuggestionStatus.FAILED: ("失敗", ft.Colors.ERROR_CONTAINER),
    }
    text, color = label_map.get(status, (status.value, ft.Colors.SURFACE))
    return ft.Container(
        content=ft.Text(text, theme_style=ft.TextThemeStyle.BODY_SMALL),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        bgcolor=color,
        border_radius=16,
    )


def _build_available_tasks_section(  # noqa: PLR0913
    *,
    tasks: tuple[AiSuggestedTask, ...],
    selected_task_ids: set[str],
    editing_task_id: str | None,
    on_toggle_task: Callable[[str], None] | None,
    on_start_edit: Callable[[str], None] | None,
    on_cancel_edit: Callable[[ft.ControlEvent | None], None] | None,
    on_edit_field_change: Callable[[str, str, str], None] | None,
    on_save_edit: Callable[[str], None] | None,
    on_delete_task: Callable[[str], None] | None,
    on_add_task: Callable[[ft.ControlEvent | None], None] | None,
) -> list[ft.Control]:
    section_controls: list[ft.Control] = []
    task_cards: list[ft.Control] = []
    if not tasks:
        section_controls.append(
            ft.Container(
                content=ft.Text(
                    "AI提案タスクがまだありません。タスクを追加して承認フローをテストできます。",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                padding=ft.padding.symmetric(vertical=8),
            )
        )

    for task in tasks:
        is_selected = task.task_id in selected_task_ids
        if task.task_id == editing_task_id:
            card_body = _build_editable_task_body(
                task,
                on_edit_field_change=on_edit_field_change,
                on_save_edit=on_save_edit,
                on_cancel_edit=on_cancel_edit,
                on_delete_task=on_delete_task,
            )
        else:
            card_body = _build_task_summary_body(
                task,
                is_selected=is_selected,
                on_toggle_task=on_toggle_task,
                on_start_edit=on_start_edit,
                on_delete_task=on_delete_task,
            )
        task_cards.append(
            ft.Container(
                content=card_body,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.SECONDARY_CONTAINER if is_selected else ft.Colors.SURFACE,
            )
        )

    if task_cards:
        section_controls.append(ft.Column(controls=task_cards, spacing=12))

    add_button = ft.TextButton(
        "タスクを追加",
        icon=ft.Icons.ADD,
        on_click=on_add_task,
    )
    section_controls.append(ft.Row(controls=[add_button], alignment=ft.MainAxisAlignment.END))

    return section_controls


def _build_task_summary_body(
    task: AiSuggestedTask,
    *,
    is_selected: bool,
    on_toggle_task: Callable[[str], None] | None,
    on_start_edit: Callable[[str], None] | None,
    on_delete_task: Callable[[str], None] | None,
) -> ft.Control:
    due_date_text = format_datetime(task.due_date)
    detail_controls: list[ft.Control] = [
        ft.Text(task.title, theme_style=ft.TextThemeStyle.TITLE_SMALL, weight=ft.FontWeight.BOLD),
        ft.Text(task.description, theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT),
    ]
    if due_date_text:
        detail_controls.append(
            ft.Text(due_date_text, theme_style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT)
        )
    if task.tags:
        tag_row = ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text(tag, theme_style=ft.TextThemeStyle.BODY_SMALL),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                )
                for tag in task.tags
            ],
            spacing=6,
            wrap=True,
        )
        detail_controls.append(tag_row)

    return ft.Row(
        controls=[
            ft.Checkbox(
                value=is_selected,
                on_change=(lambda _: on_toggle_task(task.task_id)) if on_toggle_task else None,
            ),
            ft.Column(controls=detail_controls, spacing=4, expand=True),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="編集",
                        on_click=(lambda _: on_start_edit(task.task_id)) if on_start_edit else None,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="削除",
                        on_click=(lambda _: on_delete_task(task.task_id)) if on_delete_task else None,
                    ),
                ],
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def _build_editable_task_body(
    task: AiSuggestedTask,
    *,
    on_edit_field_change: Callable[[str, str, str], None] | None,
    on_save_edit: Callable[[str], None] | None,
    on_cancel_edit: Callable[[ft.ControlEvent | None], None] | None,
    on_delete_task: Callable[[str], None] | None,
) -> ft.Control:
    def _handle_change(field: str, value: str) -> None:
        if on_edit_field_change:
            on_edit_field_change(task.task_id, field, value)

    return ft.Column(
        controls=[
            ft.TextField(
                label="タスク名",
                value=task.title,
                on_change=lambda e: _handle_change("title", e.control.value or ""),
            ),
            ft.TextField(
                label="説明",
                multiline=True,
                min_lines=3,
                value=task.description,
                on_change=lambda e: _handle_change("description", e.control.value or ""),
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "保存",
                        icon=ft.Icons.SAVE,
                        on_click=(lambda _: on_save_edit(task.task_id)) if on_save_edit else None,
                    ),
                    ft.TextButton(
                        "キャンセル",
                        on_click=on_cancel_edit,
                    ),
                    ft.TextButton(
                        "削除",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=(lambda _: on_delete_task(task.task_id)) if on_delete_task else None,
                    ),
                ],
                spacing=8,
            ),
        ],
        spacing=8,
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
