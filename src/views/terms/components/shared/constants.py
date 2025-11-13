"""Shared constants for term components."""

# Status badge configuration
STATUS_BADGE_CONFIG = {
    "APPROVED": {
        "text": "承認済み",
        "bgcolor": "primary",
        "color": "on_primary",
    },
    "DRAFT": {
        "text": "草案",
        "bgcolor": "outline_variant",
        "color": "outline",
    },
    "DEPRECATED": {
        "text": "非推奨",
        "bgcolor": "error_container",
        "color": "on_error_container",
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
