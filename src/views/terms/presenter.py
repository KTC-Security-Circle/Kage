"""Term Presenter Layer.

【責務】
    UI表示用のデータ整形・フォーマット・コンポーネントデータ作成・安全な差分更新を担当。

    - コンポーネント用Props生成
    - フォーマット済みテキスト（日付、ステータス等）の提供
    - 差分更新ヘルパー
    - 空状態メッセージの生成

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

from dataclasses import dataclass
from typing import TYPE_CHECKING

from views.sample import SampleTermStatus

from .utils import format_date, format_datetime

if TYPE_CHECKING:
    from views.sample import SampleTerm


@dataclass(frozen=True, slots=True)
class TermCardData:
    """用語カード表示用のデータ。"""

    term_id: str
    title: str
    key: str
    description: str
    synonyms: list[str]
    status: SampleTermStatus
    is_selected: bool


@dataclass(frozen=True, slots=True)
class TermDetailData:
    """用語詳細表示用のデータ。"""

    title: str
    key: str
    description: str
    synonyms: list[str]
    tags: list[str]
    status: SampleTermStatus
    status_text: str
    source_url: str | None
    created_date: str
    updated_date: str


def create_term_card_data(term: SampleTerm, *, is_selected: bool = False) -> TermCardData:
    """用語カード表示用のデータを生成する。

    Args:
        term: ソース用語データ
        is_selected: 選択状態

    Returns:
        カード表示用データ
    """
    return TermCardData(
        term_id=str(term.id),
        title=term.title,
        key=term.key,
        description=term.description or "説明なし",
        synonyms=term.synonyms[:],
        status=term.status,
        is_selected=is_selected,
    )


def create_term_detail_data(term: SampleTerm) -> TermDetailData:
    """用語詳細表示用のデータを生成する。

    Args:
        term: ソース用語データ

    Returns:
        詳細表示用データ
    """
    return TermDetailData(
        title=term.title,
        key=term.key,
        description=term.description or "説明が登録されていません",
        synonyms=term.synonyms[:],
        tags=term.tags[:],
        status=term.status,
        status_text=format_status_text(term.status),
        source_url=term.source_url,
        created_date=format_date(term.created_at),
        updated_date=format_datetime(term.updated_at),
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
