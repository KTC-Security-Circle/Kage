"""Shared constants for term components."""
import flet as ft

# Status badge configuration
STATUS_BADGE_CONFIG = {
    "APPROVED": {
        "text": "承認済み",
        "bgcolor": ft.colors.PRIMARY,
        "color": ft.colors.ON_PRIMARY,
    },
    "DRAFT": {
        "text": "草案",
        "bgcolor": ft.colors.OUTLINE_VARIANT,
        "color": ft.colors.OUTLINE,
    },
    "DEPRECATED": {
        "text": "非推奨",
        "bgcolor": ft.colors.ERROR_CONTAINER,
        "color": ft.colors.ON_ERROR_CONTAINER,
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
