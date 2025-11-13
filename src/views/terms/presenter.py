"""Term Presenter Layer.

【責務】
    UI表示用のデータ整形・フォーマット・コンポーネントデータ作成・安全な差分更新を担当。

    - コンポーネント用Props生成
    - フォーマット済みテキスト（日付、ステータス等）の提供
    - 差分更新ヘルパー
    - 空状態メッセージの生成
    - 関連アイテムデータの整形

【責務外（他層の担当）】
    - 状態管理 → State
    - ビジネスロジック → Controller
    - UI構築 → Components/View
    - 純粋関数 → utils

【設計方針】
    - Propsは不変データクラス（frozen=True, slots=True）
    - 重い変換処理はここで実施し、コンポーネントには整形済みデータを渡す
    - フォーマット・変換の共通処理はutilsに委譲
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from views.sample import SampleTermStatus

from .components.term_card import TermCardData
from .components.term_detail import RelatedItemData, TermDetailData
from .utils import format_date, format_datetime

if TYPE_CHECKING:
    from collections.abc import Callable

    from views.sample import SampleTerm


def create_term_card_data(
    term: SampleTerm, *, is_selected: bool = False, on_click: Callable[[], None] | None = None
) -> TermCardData:
    """用語カード表示用のデータを生成する。

    Args:
        term: ソース用語データ
        is_selected: 選択状態
        on_click: クリック時のコールバック

    Returns:
        カード表示用データ
    """
    return TermCardData(
        term_id=str(term.id),
        title=term.title,
        key=term.key,
        description=term.description or "説明なし",
        synonyms=tuple(term.synonyms),
        status=term.status,
        status_text=format_status_text(term.status),
        is_selected=is_selected,
        on_click=on_click,
    )


def create_term_detail_data(
    term: SampleTerm,
    *,
    related_items: list[RelatedItemData] | None = None,
) -> TermDetailData:
    """用語詳細表示用のデータを生成する。

    Args:
        term: ソース用語データ
        related_items: 関連アイテムリスト（オプション）

    Returns:
        詳細表示用データ
    """
    return TermDetailData(
        term_id=str(term.id),
        title=term.title,
        key=term.key,
        description=term.description or "説明が登録されていません",
        synonyms=tuple(term.synonyms),
        tags=tuple(term.tags),
        status=term.status,
        status_text=format_status_text(term.status),
        source_url=term.source_url,
        created_date=format_date(term.created_at),
        updated_date=format_datetime(term.updated_at),
        related_items=related_items or [],
    )


def format_status_text(status: SampleTermStatus) -> str:
    """ステータスを日本語テキストに変換する。

    Args:
        status: 用語ステータス

    Returns:
        日本語ステータステキスト
    """
    status_map = {
        SampleTermStatus.APPROVED: "承認済み",
        SampleTermStatus.DRAFT: "草案",
        SampleTermStatus.DEPRECATED: "非推奨",
    }
    return status_map.get(status, "不明")


def get_empty_message(status: SampleTermStatus) -> str:
    """空状態のメッセージを取得する。

    Args:
        status: 現在のステータス

    Returns:
        空状態メッセージ
    """
    return f"{format_status_text(status)}の用語はありません"
