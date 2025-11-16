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

from typing import TYPE_CHECKING, Any

from models import TermRead, TermStatus

from .components.term_card import TermCardData
from .components.term_detail import RelatedItemData, TermDetailData
from .utils import format_date, format_datetime

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def create_term_card_data(
    term: TermRead, *, is_selected: bool = False, on_click: Callable[[], None] | None = None
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
        synonyms=_extract_synonyms(term),
        status=term.status,
        status_text=format_status_text(term.status),
        is_selected=is_selected,
        on_click=on_click,
    )


def create_term_detail_data(
    term: TermRead,
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
        synonyms=_extract_synonyms(term),
        tags=_extract_tags(term),
        status=term.status,
        status_text=format_status_text(term.status),
        source_url=term.source_url,
        created_date=format_date(term.created_at),
        updated_date=format_datetime(term.updated_at),
        related_items=related_items or [],
    )


def format_status_text(status: TermStatus) -> str:
    """ステータスを日本語テキストに変換する。

    Args:
        status: 用語ステータス

    Returns:
        日本語ステータステキスト
    """
    status_map = {
        TermStatus.APPROVED: "承認済み",
        TermStatus.DRAFT: "草案",
        TermStatus.DEPRECATED: "非推奨",
    }
    return status_map.get(status, "不明")


def get_empty_message(status: TermStatus) -> str:
    """空状態のメッセージを取得する。

    Args:
        status: 現在のステータス

    Returns:
        空状態メッセージ
    """
    return f"{format_status_text(status)}の用語はありません"


def _extract_synonyms(term: TermRead) -> tuple[str, ...]:
    """TermReadから同義語を抽出して整形する。"""
    synonyms = getattr(term, "synonyms", None)
    return _extract_texts(synonyms, attr="text")


def _extract_tags(term: TermRead) -> tuple[str, ...]:
    """TermReadからタグ名を抽出して整形する。"""
    tags = getattr(term, "tags", None)
    return _extract_texts(tags, attr="name")


def _extract_texts(items: Sequence[Any] | None, *, attr: str) -> tuple[str, ...]:
    """Sequence内の要素から指定属性を抽出し文字列化する。"""
    if not items:
        return ()
    normalized: list[str] = []
    for item in items:
        if isinstance(item, str):
            normalized.append(item)
            continue
        if hasattr(item, attr):
            normalized.append(str(getattr(item, attr)))
            continue
        normalized.append(str(item))
    return tuple(normalized)
