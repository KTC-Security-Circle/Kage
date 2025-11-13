"""アプリケーション全体のテーマとデザイントークン定義。

このモジュールは、Fletアプリケーション全体で使用する
色、フォント、間隔、角丸等のデザイントークンを一元管理します。
明暗テーマの両方に対応し、一貫性のあるUIを提供します。
"""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft


@dataclass
class ColorTokens:
    """色定義のデータクラス。"""

    # Primary colors
    primary: str
    primary_variant: str
    on_primary: str

    # Secondary colors
    secondary: str
    secondary_variant: str
    on_secondary: str

    # Background colors
    background: str
    on_background: str
    surface: str
    on_surface: str

    # Error colors
    error: str
    on_error: str

    # Additional semantic colors
    success: str
    warning: str
    info: str


@dataclass
class TagColors:
    """タグ用のカラーパレット定義。"""

    red: str = "#f44336"
    pink: str = "#e91e63"
    purple: str = "#9c27b0"
    indigo: str = "#3f51b5"
    blue: str = "#2196f3"
    cyan: str = "#00bcd4"
    green: str = "#4caf50"
    orange: str = "#ff9800"
    brown: str = "#795548"
    grey: str = "#607d8b"


@dataclass
class StatusColors:
    """プロジェクト・タスクのステータス色定義。"""

    in_progress: str = "#2196f3"  # ブルー - 進行中
    planned: str = "#ff9800"  # オレンジ - 計画中
    completed: str = "#4caf50"  # グリーン - 完了
    on_hold: str = "#9e9e9e"  # グレー - 保留
    cancelled: str = "#f44336"  # レッド - 中止
    todays: str = "#2196f3"  # ブルー - 今日のタスク


@dataclass
class UIColors:
    """UI全般で使用する汎用色定義。"""

    # グレースケール
    grey_50: str = "#fafafa"
    grey_100: str = "#f5f5f5"
    grey_200: str = "#eeeeee"
    grey_300: str = "#e0e0e0"
    grey_400: str = "#bdbdbd"
    grey_500: str = "#9e9e9e"
    grey_600: str = "#757575"
    grey_700: str = "#616161"
    grey_800: str = "#424242"
    grey_900: str = "#212121"

    # 機能的な色
    primary: str = "#2196f3"
    primary_light: str = "#64b5f6"
    primary_dark: str = "#1976d2"

    error: str = "#f44336"
    error_light: str = "#ef5350"

    success: str = "#4caf50"
    warning: str = "#ff9800"
    info: str = "#2196f3"

    # タグ関連の透明度付き色
    tag_icon_bg_opacity: float = 0.1


@dataclass
class SpacingTokens:
    """間隔定義のデータクラス。"""

    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class BorderRadiusTokens:
    """角丸定義のデータクラス。"""

    sm: int = 4
    md: int = 8
    lg: int = 12
    xl: int = 16


@dataclass
class FontTokens:
    """フォント定義のデータクラス。"""

    family: str = "Roboto"
    size_sm: int = 12
    size_md: int = 14
    size_lg: int = 16
    size_xl: int = 20
    size_xxl: int = 24


# Light theme color tokens
LIGHT_COLORS = ColorTokens(
    primary="#6750A4",
    primary_variant="#958DA5",
    on_primary="#FFFFFF",
    secondary="#625B71",
    secondary_variant="#958DA5",
    on_secondary="#FFFFFF",
    background="#FFFBFE",
    on_background="#1C1B1F",
    surface="#FFFBFE",
    on_surface="#1C1B1F",
    error="#BA1A1A",
    on_error="#FFFFFF",
    success="#2E7D32",
    warning="#F57C00",
    info="#1976D2",
)

# Dark theme color tokens
DARK_COLORS = ColorTokens(
    primary="#D0BCFF",
    primary_variant="#625B71",
    on_primary="#381E72",
    secondary="#CCC2DC",
    secondary_variant="#4A4458",
    on_secondary="#332D41",
    background="#141218",
    on_background="#E6E0E9",
    surface="#141218",
    on_surface="#E6E0E9",
    error="#F2B8B5",
    on_error="#601410",
    success="#81C784",
    warning="#FFB74D",
    info="#64B5F6",
)

# Common tokens
SPACING = SpacingTokens()
BORDER_RADIUS = BorderRadiusTokens()
FONT = FontTokens()

# Color palette instances
TAG_COLORS = TagColors()
STATUS_COLORS = StatusColors()
UI_COLORS = UIColors()

# Tag color palette for UI components
TAG_COLOR_PALETTE = [
    {"name": "レッド", "value": TAG_COLORS.red, "hex": TAG_COLORS.red[1:].upper()},
    {"name": "ピンク", "value": TAG_COLORS.pink, "hex": TAG_COLORS.pink[1:].upper()},
    {"name": "パープル", "value": TAG_COLORS.purple, "hex": TAG_COLORS.purple[1:].upper()},
    {"name": "インディゴ", "value": TAG_COLORS.indigo, "hex": TAG_COLORS.indigo[1:].upper()},
    {"name": "ブルー", "value": TAG_COLORS.blue, "hex": TAG_COLORS.blue[1:].upper()},
    {"name": "シアン", "value": TAG_COLORS.cyan, "hex": TAG_COLORS.cyan[1:].upper()},
    {"name": "グリーン", "value": TAG_COLORS.green, "hex": TAG_COLORS.green[1:].upper()},
    {"name": "オレンジ", "value": TAG_COLORS.orange, "hex": TAG_COLORS.orange[1:].upper()},
    {"name": "ブラウン", "value": TAG_COLORS.brown, "hex": TAG_COLORS.brown[1:].upper()},
    {"name": "グレー", "value": TAG_COLORS.grey, "hex": TAG_COLORS.grey[1:].upper()},
]

# Status color mapping for projects and tasks
# 備考:
# - 表示ラベル(日本語)と内部コード(英語: active/completed/on_hold/cancelled)の両方を許容する
# - 既存画面では「キャンセル」という日本語表記も使われているため、同義語として扱う
STATUS_COLOR_MAP = {
    # Japanese display labels
    "進行中": STATUS_COLORS.in_progress,
    "計画中": STATUS_COLORS.planned,
    "完了": STATUS_COLORS.completed,
    "保留": STATUS_COLORS.on_hold,
    "中止": STATUS_COLORS.cancelled,
    "キャンセル": STATUS_COLORS.cancelled,
    "今日": STATUS_COLORS.todays,
    # Internal English codes
    "active": STATUS_COLORS.in_progress,
    "planned": STATUS_COLORS.planned,
    "completed": STATUS_COLORS.completed,
    "on_hold": STATUS_COLORS.on_hold,
    "cancelled": STATUS_COLORS.cancelled,
    "todays": STATUS_COLORS.todays,
}


def create_light_theme() -> ft.Theme:
    """ライトテーマのFletテーマオブジェクトを作成する。

    Returns:
        ライト設定のFletテーマオブジェクト
    """
    colors = LIGHT_COLORS

    color_scheme = ft.ColorScheme(
        primary=colors.primary,
        on_primary=colors.on_primary,
        secondary=colors.secondary,
        on_secondary=colors.on_secondary,
        background=colors.background,
        on_background=colors.on_background,
        surface=colors.surface,
        on_surface=colors.on_surface,
        error=colors.error,
        on_error=colors.on_error,
    )

    return ft.Theme(color_scheme=color_scheme)


def create_dark_theme() -> ft.Theme:
    """ダークテーマのFletテーマオブジェクトを作成する。

    Returns:
        ダーク設定のFletテーマオブジェクト
    """
    colors = DARK_COLORS

    color_scheme = ft.ColorScheme(
        primary=colors.primary,
        on_primary=colors.on_primary,
        secondary=colors.secondary,
        on_secondary=colors.on_secondary,
        background=colors.background,
        on_background=colors.on_background,
        surface=colors.surface,
        on_surface=colors.on_surface,
        error=colors.error,
        on_error=colors.on_error,
    )

    return ft.Theme(color_scheme=color_scheme)


def get_light_color(color_name: str) -> str:
    """ライトテーマから色名で色コードを取得する。

    Args:
        color_name: 取得したい色の名前

    Returns:
        色コード（HEX形式）

    Raises:
        AttributeError: 指定された色名が存在しない場合
    """
    colors = LIGHT_COLORS

    if not hasattr(colors, color_name):
        msg = f"Color '{color_name}' not found"
        raise AttributeError(msg)

    return getattr(colors, color_name)


def get_dark_color(color_name: str) -> str:
    """ダークテーマから色名で色コードを取得する。

    Args:
        color_name: 取得したい色の名前

    Returns:
        色コード（HEX形式）

    Raises:
        AttributeError: 指定された色名が存在しない場合
    """
    colors = DARK_COLORS

    if not hasattr(colors, color_name):
        msg = f"Color '{color_name}' not found"
        raise AttributeError(msg)

    return getattr(colors, color_name)


def get_status_color(status: str) -> str:
    """ステータス名から対応する色コードを取得する。

    Args:
        status: ステータス名（進行中、計画中、完了、保留、中止）

    Returns:
        色コード（HEX形式）
    """
    # 英語コードは小文字で来る前提が多いため、まず lower() を試す
    normalized = status.strip()
    lower = normalized.lower()
    if lower in STATUS_COLOR_MAP:
        return STATUS_COLOR_MAP[lower]
    return STATUS_COLOR_MAP.get(normalized, STATUS_COLORS.on_hold)


def get_tag_color_palette() -> list[dict[str, str]]:
    """タグ用のカラーパレットを取得する。

    Returns:
        カラーパレットのリスト（name, value, hex を含む辞書）
    """
    return TAG_COLOR_PALETTE.copy()


def get_task_status_color(status: str) -> str:
    """タスクステータスから対応する色コードを取得する。

    Args:
        status: タスクステータス（completed, todays, active など）

    Returns:
        色コード（HEX形式）
    """
    normalized = status.strip().lower()
    if normalized == "completed":
        return STATUS_COLORS.completed
    if normalized == "todays":
        return STATUS_COLORS.todays
    return STATUS_COLORS.on_hold


def get_grey_color(shade: int = 600) -> str:
    """グレー色を取得する。

    Args:
        shade: グレーのシェード（50, 100, 200, ..., 900）

    Returns:
        色コード（HEX形式）
    """
    shade_map = {
        50: UI_COLORS.grey_50,
        100: UI_COLORS.grey_100,
        200: UI_COLORS.grey_200,
        300: UI_COLORS.grey_300,
        400: UI_COLORS.grey_400,
        500: UI_COLORS.grey_500,
        600: UI_COLORS.grey_600,
        700: UI_COLORS.grey_700,
        800: UI_COLORS.grey_800,
        900: UI_COLORS.grey_900,
    }
    return shade_map.get(shade, UI_COLORS.grey_600)


def get_primary_color(variant: str = "base") -> str:
    """プライマリカラーを取得する。

    Args:
        variant: カラーバリアント（base, light, dark）

    Returns:
        色コード（HEX形式）
    """
    if variant == "light":
        return UI_COLORS.primary_light
    if variant == "dark":
        return UI_COLORS.primary_dark
    return UI_COLORS.primary


def get_tag_icon_bg_opacity() -> float:
    """タグアイコン背景の透明度を取得する。

    Returns:
        透明度（0.0 - 1.0）

    Note:
        Fletでの使用例: ft.Colors.with_opacity(get_tag_icon_bg_opacity(), color)
    """
    return UI_COLORS.tag_icon_bg_opacity


# TODO: 統合フェーズで settings から現在のテーマモード設定を取得する機能を追加
# 理由: ユーザー設定の永続化機能が未実装のため
# 置換先: settings/application_service.py から theme_mode を取得
