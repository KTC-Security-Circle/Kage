"""アプリケーション全体のテーマとデザイントークン定義。

このモジュールは、Fletアプリケーション全体で使用する
色、フォント、間隔、角丸等のデザイントークンを一元管理します。
明暗テーマの両方に対応し、一貫性のあるUIを提供します。

主要なカラー取得関数:
    get_primary_color(variant="base") -> str:
        プライマリカラーを取得（variant: "base", "light", "dark"）

    get_surface_color() -> str:
        サーフェス（カード・パネル）背景色を取得

    get_on_surface_color() -> str:
        サーフェス上のテキスト色を取得

    get_background_color() -> str:
        アプリ全体の背景色を取得

    get_outline_color() -> str:
        アウトライン（境界線・Divider）用の色を取得

    get_text_secondary_color() -> str:
        補助テキスト用の色を取得（キャプション、タイムスタンプなど）

    get_surface_variant_color() -> str:
        サーフェスバリアント（強調背景）色を取得（選択状態、ホバー状態など）

    get_status_color(status: str) -> str:
        ステータス名から対応する色コードを取得

    get_tag_color_palette() -> list[dict[str, str]]:
        タグ用のカラーパレットを取得

使用例:
    ```python
    import flet as ft
    from views.theme import (
        get_primary_color,
        get_surface_color,
        get_on_surface_color,
        get_outline_color,
        SPACING,
        BORDER_RADIUS,
    )

    # カード背景とテキスト色
    card = ft.Container(
        bgcolor=get_surface_color(),
        border=ft.border.all(1, get_outline_color()),
        border_radius=BORDER_RADIUS.md,
        padding=SPACING.md,
        content=ft.Text("カード", color=get_on_surface_color()),
    )

    # プライマリアクションボタン
    button = ft.ElevatedButton(
        text="保存",
        bgcolor=get_primary_color(),
        color=get_on_primary_color(),
    )
    ```
"""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft


class Palette:
    """基本カラーパレット定義（Material Design Colors）。

    DRY原則に基づき、色コードの定義を一箇所に集約します。
    """

    # Red
    RED_400 = "#EF5350"
    RED_500 = "#F44336"
    RED_700 = "#D32F2F"
    RED_900 = "#B71C1C"

    # Pink
    PINK_500 = "#E91E63"

    # Purple
    PURPLE_500 = "#9C27B0"

    # Indigo
    INDIGO_500 = "#3F51B5"

    # Blue
    BLUE_300 = "#64B5F6"
    BLUE_400 = "#42A5F5"
    BLUE_500 = "#2196F3"
    BLUE_700 = "#1976D2"
    BLUE_900 = "#0D47A1"

    # Cyan
    CYAN_500 = "#00BCD4"

    # Green
    GREEN_500 = "#4CAF50"
    GREEN_700 = "#388E3C"
    GREEN_400 = "#66BB6A"

    # Orange
    ORANGE_400 = "#FFA726"
    ORANGE_500 = "#FF9800"
    ORANGE_700 = "#F57C00"

    # Amber
    AMBER_500 = "#FFC107"

    # Brown
    BROWN_500 = "#795548"

    # Blue Grey
    BLUE_GREY_500 = "#607D8B"

    # Grey
    GREY_50 = "#FAFAFA"
    GREY_100 = "#F5F5F5"
    GREY_200 = "#EEEEEE"
    GREY_300 = "#E0E0E0"
    GREY_400 = "#BDBDBD"
    GREY_500 = "#9E9E9E"
    GREY_600 = "#757575"
    GREY_700 = "#616161"
    GREY_800 = "#424242"
    GREY_900 = "#212121"

    # Common
    WHITE = "#FFFFFF"
    BLACK = "#000000"

    # Dark Theme Specifics
    DARK_BG = "#121212"
    DARK_SURFACE = "#1E1E1E"
    DARK_ON_SURFACE = "#E0E0E0"
    DARK_ON_PRIMARY = "#0D47A1"  # Blue 900
    DARK_ON_ERROR = "#B71C1C"  # Red 900

    # Secondary Colors
    SECONDARY_LIGHT = "#625B71"
    SECONDARY_VARIANT_LIGHT = "#958DA5"
    SECONDARY_DARK = "#CCC2DC"
    SECONDARY_VARIANT_DARK = "#4A4458"
    ON_SECONDARY_DARK = "#332D41"

    # Text Colors
    TEXT_PRIMARY_LIGHT = "#1C1B1F"
    TEXT_PRIMARY_DARK = "#E0E0E0"


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
    """タグ用のカラーパレット定義（Material Design 500 シェード）。"""

    red: str = Palette.RED_500
    pink: str = Palette.PINK_500
    purple: str = Palette.PURPLE_500
    indigo: str = Palette.INDIGO_500
    blue: str = Palette.BLUE_500
    cyan: str = Palette.CYAN_500
    green: str = Palette.GREEN_500
    orange: str = Palette.ORANGE_500
    brown: str = Palette.BROWN_500
    grey: str = Palette.BLUE_GREY_500


@dataclass
class StatusColors:
    """プロジェクト・タスクのステータス色定義（Material Design 準拠）。"""

    in_progress: str = Palette.BLUE_500  # Blue 500 - 進行中
    planned: str = Palette.ORANGE_500  # Orange 500 - 計画中
    completed: str = Palette.GREEN_500  # Green 500 - 完了
    on_hold: str = Palette.GREY_500  # Grey 500 - 保留
    cancelled: str = Palette.RED_500  # Red 500 - 中止
    todays: str = Palette.BLUE_500  # Blue 500 - 今日のタスク


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
    round: int = 50


@dataclass
class OpacityTokens:
    """透明度定義のデータクラス。"""

    subtle: float = 0.05
    light: float = 0.1
    border_light: float = 0.2
    border_medium: float = 0.3
    medium: float = 0.6
    high: float = 0.7
    full: float = 1.0


@dataclass
class BorderWidthTokens:
    """ボーダー幅定義のデータクラス。"""

    thin: int = 1
    medium: int = 2
    thick: int = 3


@dataclass
class ShadowTokens:
    """シャドウ定義のデータクラス。"""

    subtle_spread: int = 0
    subtle_blur: int = 2
    subtle_offset_y: int = 1
    subtle_opacity: float = 0.05

    medium_spread: int = 0
    medium_blur: int = 4
    medium_offset_y: int = 2
    medium_opacity: float = 0.1


@dataclass
class FontTokens:
    """フォント定義のデータクラス。"""

    family: str = "Roboto"
    size_sm: int = 12
    size_md: int = 14
    size_lg: int = 16
    size_xl: int = 20
    size_xxl: int = 24


# Light theme color tokens (Material Design 3)
LIGHT_COLORS = ColorTokens(
    primary=Palette.BLUE_500,  # Blue - アプリ全体の統一プライマリカラー
    primary_variant=Palette.BLUE_700,
    on_primary=Palette.WHITE,
    secondary=Palette.SECONDARY_LIGHT,
    secondary_variant=Palette.SECONDARY_VARIANT_LIGHT,
    on_secondary=Palette.WHITE,
    background=Palette.GREY_50,  # Neutral grey background
    on_background=Palette.TEXT_PRIMARY_LIGHT,
    surface=Palette.WHITE,  # Pure white for cards/panels
    on_surface=Palette.TEXT_PRIMARY_LIGHT,
    error=Palette.RED_700,  # Material Red 700
    on_error=Palette.WHITE,
    success=Palette.GREEN_700,  # Material Green 700
    warning=Palette.ORANGE_700,  # Material Orange 700
    info=Palette.BLUE_700,  # Material Blue 700
)

# Dark theme color tokens (Material Design 3)
DARK_COLORS = ColorTokens(
    primary=Palette.BLUE_300,  # Light Blue - ダークモード用の明るいブルー
    primary_variant=Palette.BLUE_400,
    on_primary=Palette.DARK_ON_PRIMARY,
    secondary=Palette.SECONDARY_DARK,
    secondary_variant=Palette.SECONDARY_VARIANT_DARK,
    on_secondary=Palette.ON_SECONDARY_DARK,
    background=Palette.DARK_BG,  # True dark background
    on_background=Palette.TEXT_PRIMARY_DARK,
    surface=Palette.DARK_SURFACE,  # Elevated surface
    on_surface=Palette.TEXT_PRIMARY_DARK,
    error=Palette.RED_400,  # Light Red for dark mode
    on_error=Palette.DARK_ON_ERROR,
    success=Palette.GREEN_400,  # Light Green for dark mode
    warning=Palette.ORANGE_400,  # Light Orange for dark mode
    info=Palette.BLUE_400,  # Light Blue for dark mode
)

# Common tokens
SPACING = SpacingTokens()
BORDER_RADIUS = BorderRadiusTokens()
FONT = FontTokens()
OPACITY = OpacityTokens()
BORDER_WIDTH = BorderWidthTokens()
SHADOW = ShadowTokens()

# Color palette instances
TAG_COLORS = TagColors()
STATUS_COLORS = StatusColors()
# UI_COLORS は廃止し、Palette を直接参照するか、必要なヘルパー関数経由でアクセスする
# UI_COLORS = UIColors()

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


STATUS_LABEL_MAP = {
    # Task statuses
    "completed": "完了",
    "todays": "今日",
    "active": "進行中",
    # Project statuses
    "planned": "計画中",
    "on_hold": "保留",
    "cancelled": "中止",
}


def _create_theme(colors: ColorTokens) -> ft.Theme:
    """共通のテーマ作成ロジック。"""
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


def create_light_theme() -> ft.Theme:
    """ライトテーマのFletテーマオブジェクトを作成する。

    Returns:
        ライト設定のFletテーマオブジェクト
    """
    return _create_theme(LIGHT_COLORS)


def create_dark_theme() -> ft.Theme:
    """ダークテーマのFletテーマオブジェクトを作成する。

    Returns:
        ダーク設定のFletテーマオブジェクト
    """
    return _create_theme(DARK_COLORS)


def _get_color_from_tokens(colors: ColorTokens, color_name: str) -> str:
    """トークンから色名で色コードを取得する共通ロジック。"""
    if not hasattr(colors, color_name):
        msg = f"Color '{color_name}' not found"
        raise AttributeError(msg)
    return getattr(colors, color_name)


def get_light_color(color_name: str) -> str:
    """ライトテーマから色名で色コードを取得する。

    Args:
        color_name: 取得したい色の名前

    Returns:
        色コード（HEX形式）

    Raises:
        AttributeError: 指定された色名が存在しない場合
    """
    return _get_color_from_tokens(LIGHT_COLORS, color_name)


def get_dark_color(color_name: str) -> str:
    """ダークテーマから色名で色コードを取得する。

    Args:
        color_name: 取得したい色の名前

    Returns:
        色コード（HEX形式）

    Raises:
        AttributeError: 指定された色名が存在しない場合
    """
    return _get_color_from_tokens(DARK_COLORS, color_name)


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
    # [AI GENERATED] get_status_color() を利用して重複を排除
    return get_status_color(status)


def get_grey_color(shade: int = 600) -> str:
    """グレー色を取得する。

    Args:
        shade: グレーのシェード（50, 100, 200, ..., 900）

    Returns:
        色コード（HEX形式）
    """
    shade_map = {
        50: Palette.GREY_50,
        100: Palette.GREY_100,
        200: Palette.GREY_200,
        300: Palette.GREY_300,
        400: Palette.GREY_400,
        500: Palette.GREY_500,
        600: Palette.GREY_600,
        700: Palette.GREY_700,
        800: Palette.GREY_800,
        900: Palette.GREY_900,
    }
    return shade_map.get(shade, Palette.GREY_600)


def get_primary_color(variant: str = "base") -> str:
    """プライマリカラーを取得する。

    Args:
        variant: カラーバリアント（base, light, dark）

    Returns:
        色コード（HEX形式）
    """
    colors = _get_current_theme_colors()
    if variant == "dark":
        # primary_variant を dark として扱う
        return colors.primary_variant
    if variant == "light":
        # TODO: ColorTokensにlight variantを追加するか、Tonal Paletteを導入する
        # 現状はprimaryと同じか、ハードコードで対応
        return Palette.BLUE_300  # Blue 300
    return colors.primary


def get_tag_icon_bg_opacity() -> float:
    """タグアイコン背景の透明度を取得する。

    Returns:
        透明度（0.0 - 1.0）

    Note:
        Fletでの使用例: ft.Colors.with_opacity(get_tag_icon_bg_opacity(), color)
    """
    return OPACITY.light


def get_status_label(status: str | None) -> str | None:
    """ステータスコードから日本語ラベルを取得する。

    Args:
        status: ステータスコード（active, completed, on_hold, cancelled, todays など）

    Returns:
        日本語ラベル（進行中、完了、保留、中止、今日など）
        status が None の場合は None を返す

    Note:
        ステータスラベルの一元管理。presenter等で重複実装しない。
    """
    if not status:
        return None

    normalized = status.strip().lower()
    return STATUS_LABEL_MAP.get(normalized, status)


# Material Design 3 セマンティックカラー取得関数
# NOTE: 現在はライトテーマのみ対応。将来的にはsettingsからテーマモードを取得して切り替える


def _get_current_theme_colors() -> ColorTokens:
    """現在のテーマ設定に基づいたカラートークンを取得する。

    Note:
        現在はLIGHT_COLORS固定だが、将来的には設定に基づいて
        LIGHT_COLORS / DARK_COLORS を切り替える分岐点となる。
    """
    # TODO: settingsからテーマモードを取得して分岐
    return LIGHT_COLORS


def get_on_primary_color() -> str:
    """プライマリカラー上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        ボタンやチップなどのプライマリカラー背景上で使用するテキスト色。
        ライト/ダークテーマで自動的に適切なコントラスト比を保証。
    """
    return _get_current_theme_colors().on_primary


def get_on_surface_color() -> str:
    """サーフェス上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        カードやパネル背景上で使用する基本テキスト色。
    """
    return _get_current_theme_colors().on_surface


def get_surface_color() -> str:
    """サーフェス（カード・パネル）背景色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return _get_current_theme_colors().surface


def get_background_color() -> str:
    """アプリ全体の背景色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return _get_current_theme_colors().background


def get_error_color() -> str:
    """エラー色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        エラーメッセージ、バリデーションエラー表示などに使用。
    """
    return _get_current_theme_colors().error


def get_success_color() -> str:
    """成功色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        成功メッセージ、完了ステータス表示などに使用。
    """
    return _get_current_theme_colors().success


def get_warning_color() -> str:
    """警告色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        警告メッセージ、注意喚起表示などに使用。
    """
    return _get_current_theme_colors().warning


def get_info_color() -> str:
    """情報色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        情報メッセージ、インフォメーション表示などに使用。
    """
    return _get_current_theme_colors().info


def get_on_error_color() -> str:
    """エラー色背景上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return _get_current_theme_colors().on_error


# 役割ベースのカラーヘルパー（MD3ガイドライン準拠）


def get_outline_color() -> str:
    """アウトライン（境界線・Divider）用の色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        カードの枠線、Divider、入力フィールドのボーダーなど。
    """
    return get_grey_color(300)


def get_text_secondary_color() -> str:
    """補助テキスト用の色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        キャプション、タイムスタンプ、補足説明など、主要テキストより優先度が低い情報。
    """
    return get_grey_color(600)


def get_surface_variant_color() -> str:
    """サーフェスバリアント（強調背景）色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        選択状態、ホバー状態など、通常のサーフェスより少し強調したい背景。
    """
    return get_grey_color(100)


def create_subtle_shadow() -> ft.BoxShadow:
    """微妙なシャドウエフェクトを作成する。

    Returns:
        BoxShadow オブジェクト

    Note:
        カード、パネルなどに使用。
    """
    return ft.BoxShadow(
        spread_radius=SHADOW.subtle_spread,
        blur_radius=SHADOW.subtle_blur,
        color=ft.Colors.with_opacity(SHADOW.subtle_opacity, ft.Colors.BLACK),
        offset=ft.Offset(0, SHADOW.subtle_offset_y),
    )


def create_medium_shadow() -> ft.BoxShadow:
    """中程度のシャドウエフェクトを作成する。

    Returns:
        BoxShadow オブジェクト

    Note:
        アイコンコンテナ、強調表示要素などに使用。
    """
    return ft.BoxShadow(
        spread_radius=SHADOW.medium_spread,
        blur_radius=SHADOW.medium_blur,
        color=ft.Colors.with_opacity(SHADOW.medium_opacity, ft.Colors.BLACK),
        offset=ft.Offset(0, SHADOW.medium_offset_y),
    )


def get_accent_background_color(color_name: str = "primary") -> str:
    """アクセントカラーの背景色を取得する。

    Args:
        color_name: カラー名（primary, blue, amber など）

    Returns:
        色コード（HEX形式）

    Note:
        デイリーレビューカードなどのアクセント背景に使用。
        色名に応じた適切な背景色を返す。
    """
    colors = _get_current_theme_colors()
    accent_map = {
        "amber": colors.warning,
        "blue": colors.primary,
        "green": colors.success,
        "primary": colors.primary,
        "purple": TAG_COLORS.purple,
    }
    return accent_map.get(color_name, colors.primary)


def get_accent_border_color(color_name: str = "primary") -> str:
    """アクセントカラーのボーダー色を取得する。

    Args:
        color_name: カラー名（primary, blue, amber など）

    Returns:
        色コード（HEX形式）
    """
    # amber は特別扱い（より明るいボーダー）
    if color_name == "amber":
        return Palette.AMBER_500  # AMBER_500

    # その他は get_outline_color() をベースにする
    return get_outline_color()


# TODO: 統合フェーズで settings から現在のテーマモード設定を取得する機能を追加
# 理由: ユーザー設定の永続化機能が未実装のため
# 置換先: settings/application_service.py から theme_mode を取得

# TODO: [ロジック担当者向け] ダークモード対応の実装計画
# 実装箇所: src/views/theme.py
# 依存: settings/application_service.py のテーマモード管理機能
#
# 【実装内容】
# 1. テーマモード取得関数の追加
#    - def get_current_theme_mode() -> ThemeMode:
#      settings からユーザーの選択テーマ(light/dark/system)を取得
#
# 2. 動的カラー取得関数の修正
#    現在ライトテーマ固定の以下の関数をテーマモード対応に:
#    - get_on_primary_color()   → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_on_surface_color()   → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_surface_color()      → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_background_color()   → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_error_color()        → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_on_error_color()     → LIGHT_COLORS / DARK_COLORS 切り替え
#    - get_outline_color()      → グレーシェードをテーマで切り替え
#    - get_text_secondary_color() → グレーシェードをテーマで切り替え
#    - get_surface_variant_color() → グレーシェードをテーマで切り替え
#
# 3. システムテーマ検出の実装
#    - Flet の page.platform_brightness を使用してOSのダーク/ライト設定を検出
#    - ThemeMode.SYSTEM 選択時に自動切り替え
#
# 【影響範囲】
# - 全Viewで自動的にダークモード対応完了(ハードコードゼロのため)
# - presenter.py などは修正不要
#
# 【優先度】
# - 週次レビューの対応: 高
# - Priority: Medium (ユーザー体験向上)
# - 推奨実装時期: Settings View 統合完了後
