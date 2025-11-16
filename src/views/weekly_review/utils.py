"""週次レビュービューのユーティリティ関数

純粋関数群（フォーマット、計算、変換等）。
"""

from datetime import datetime, timedelta


def format_percentage(value: float) -> str:
    """パーセンテージを整形

    Args:
        value: 0.0 ~ 1.0 の値

    Returns:
        整形されたパーセンテージ文字列（例: "75%"）
    """
    return f"{int(value * 100)}%"


def format_trend(current: int, previous: int) -> str:
    """トレンドを整形

    Args:
        current: 現在の値
        previous: 前回の値

    Returns:
        トレンド文字列（例: "↑ 15%"）
    """
    if previous == 0:
        return "→ --"

    diff_percent = ((current - previous) / previous) * 100
    if diff_percent > 0:
        return f"↑ {abs(int(diff_percent))}%"
    if diff_percent < 0:
        return f"↓ {abs(int(diff_percent))}%"
    return "→ 0%"


def format_hours(minutes: int) -> str:
    """分数を時間表記に変換

    Args:
        minutes: 分数

    Returns:
        時間表記（例: "2.5h"）
    """
    hours = minutes / 60
    return f"{hours:.1f}h"


def format_count(count: int, singular: str = "件", plural: str | None = None) -> str:
    """カウントと単位を整形

    Args:
        count: カウント数
        singular: 単数形の単位
        plural: 複数形の単位（省略時はsingularを使用）

    Returns:
        整形されたカウント文字列（例: "3件"）
    """
    unit = plural if count != 1 and plural else singular
    return f"{count}{unit}"


def get_week_number(date: datetime | None = None) -> int:
    """ISO週番号を取得

    Args:
        date: 対象の日時（省略時は現在時刻）

    Returns:
        ISO週番号
    """
    target = date or datetime.now()
    return target.isocalendar()[1]


def get_week_date_range(date: datetime | None = None) -> tuple[datetime, datetime]:
    """指定日を含む週の開始日と終了日を取得

    Args:
        date: 対象の日時（省略時は現在時刻）

    Returns:
        (開始日, 終了日) のタプル
    """
    target = date or datetime.now()
    target = target.replace(hour=0, minute=0, second=0, microsecond=0)
    days_since_monday = target.weekday()
    week_start = target - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return week_start, week_end


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全な除算（ゼロ除算を回避）

    Args:
        numerator: 分子
        denominator: 分母
        default: 分母がゼロの場合のデフォルト値

    Returns:
        除算結果またはデフォルト値
    """
    return numerator / denominator if denominator != 0 else default


def calculate_completion_rate(completed: int, total: int) -> float:
    """完了率を計算

    Args:
        completed: 完了数
        total: 総数

    Returns:
        完了率（0.0 ~ 1.0）
    """
    return safe_divide(completed, total, 0.0)
