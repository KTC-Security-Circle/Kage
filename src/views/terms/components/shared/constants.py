"""Shared constants for term components."""

from views.theme import (
    get_error_color,
    get_on_primary_color,
    get_outline_color,
    get_primary_color,
    get_surface_variant_color,
)


def get_status_badge_config() -> dict[str, dict[str, str]]:
    """ステータスバッジの設定を取得する。

    Returns:
        ステータスバッジの設定辞書

    Note:
        theme.py から動的に色を取得するため、関数として提供。
    """
    return {
        "APPROVED": {
            "text": "承認済み",
            "bgcolor": get_primary_color(),
            "color": get_on_primary_color(),
        },
        "DRAFT": {
            "text": "草案",
            "bgcolor": get_surface_variant_color(),
            "color": get_outline_color(),
        },
        "DEPRECATED": {
            "text": "非推奨",
            "bgcolor": get_error_color(),
            "color": get_on_primary_color(),
        },
    }


# Display limits
MAX_SYNONYMS_DISPLAY = 3
MAX_DESCRIPTION_LINES = 2

# Spacing
CARD_SPACING = 8
CARD_PADDING = 16
DETAIL_SPACING = 16
DETAIL_PADDING = 24
