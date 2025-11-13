"""Term Utils Layer.

【責務】
    純粋関数群（フォーマット、軽量変換、predicate、safe_cast、
    正規化共通処理、並び順ポリシーのソートキー/ソート関数など）。
    UIコントロールや副作用は置かない。

【責務外（他層の担当）】
    - UI要素の構築 → Components/Presenter
    - 状態管理 → State
    - サービス呼び出し → Controller
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from views.sample import SampleTerm


def format_date(dt: datetime) -> str:
    """日時を日本語フォーマットに変換する。

    Args:
        dt: フォーマット対象の日時

    Returns:
        "YYYY年MM月DD日" 形式の文字列
    """
    return dt.strftime("%Y年%m月%d日")


def format_datetime(dt: datetime) -> str:
    """日時を詳細な日本語フォーマットに変換する。

    Args:
        dt: フォーマット対象の日時

    Returns:
        "YYYY年MM月DD日 HH:MM" 形式の文字列
    """
    return dt.strftime("%Y年%m月%d日 %H:%M")


def get_term_sort_key(term: SampleTerm) -> tuple[float, str]:
    """用語のソートキーを生成する。

    更新日時の降順、同一の場合はタイトルの昇順。

    Args:
        term: ソート対象の用語

    Returns:
        ソートキーのタプル（更新日時の逆順、タイトル）
    """
    return (-term.updated_at.timestamp(), term.title.lower())


def sort_terms(terms: list[SampleTerm]) -> list[SampleTerm]:
    """用語リストをソートする。

    Args:
        terms: ソート対象の用語リスト

    Returns:
        ソート済みの用語リスト
    """
    return sorted(terms, key=get_term_sort_key)


def safe_cast(value: str, default: str = "") -> str:
    """文字列を安全にキャストする。

    Args:
        value: キャスト対象の値
        default: 値がNoneの場合のデフォルト値

    Returns:
        文字列またはデフォルト値
    """
    return value if value is not None else default
