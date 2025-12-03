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
    """タグ用のカラーパレット定義（Material Design 500 シェード）。"""

    red: str = "#F44336"  # Red 500
    pink: str = "#E91E63"  # Pink 500
    purple: str = "#9C27B0"  # Purple 500
    indigo: str = "#3F51B5"  # Indigo 500
    blue: str = "#2196F3"  # Blue 500
    cyan: str = "#00BCD4"  # Cyan 500
    green: str = "#4CAF50"  # Green 500
    orange: str = "#FF9800"  # Orange 500
    brown: str = "#795548"  # Brown 500
    grey: str = "#607D8B"  # Blue Grey 500


@dataclass
class StatusColors:
    """プロジェクト・タスクのステータス色定義（Material Design 準拠）。"""

    in_progress: str = "#2196F3"  # Blue 500 - 進行中
    planned: str = "#FF9800"  # Orange 500 - 計画中
    completed: str = "#4CAF50"  # Green 500 - 完了
    on_hold: str = "#9E9E9E"  # Grey 500 - 保留
    cancelled: str = "#F44336"  # Red 500 - 中止
    todays: str = "#2196F3"  # Blue 500 - 今日のタスク


@dataclass
class UIColors:
    """UI全般で使用する汎用色定義（Material Design Grey パレット）。"""

    # グレースケール (Material Design Grey)
    grey_50: str = "#FAFAFA"
    grey_100: str = "#F5F5F5"
    grey_200: str = "#EEEEEE"
    grey_300: str = "#E0E0E0"
    grey_400: str = "#BDBDBD"
    grey_500: str = "#9E9E9E"
    grey_600: str = "#757575"
    grey_700: str = "#616161"
    grey_800: str = "#424242"
    grey_900: str = "#212121"

    # 機能的な色（Material Design Blue パレット）
    primary: str = "#2196F3"  # Blue 500
    primary_light: str = "#64B5F6"  # Blue 300
    primary_dark: str = "#1976D2"  # Blue 700

    # セマンティックカラー（Material Design）
    error: str = "#F44336"  # Red 500
    error_light: str = "#EF5350"  # Red 400

    success: str = "#4CAF50"  # Green 500
    warning: str = "#FF9800"  # Orange 500
    info: str = "#2196F3"  # Blue 500

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
    primary="#2196F3",  # Blue - アプリ全体の統一プライマリカラー
    primary_variant="#1976D2",
    on_primary="#FFFFFF",
    secondary="#625B71",
    secondary_variant="#958DA5",
    on_secondary="#FFFFFF",
    background="#FAFAFA",  # Neutral grey background
    on_background="#1C1B1F",
    surface="#FFFFFF",  # Pure white for cards/panels
    on_surface="#1C1B1F",
    error="#D32F2F",  # Material Red 700
    on_error="#FFFFFF",
    success="#388E3C",  # Material Green 700
    warning="#F57C00",  # Material Orange 700
    info="#1976D2",  # Material Blue 700
)

# Dark theme color tokens (Material Design 3)
DARK_COLORS = ColorTokens(
    primary="#64B5F6",  # Light Blue - ダークモード用の明るいブルー
    primary_variant="#42A5F5",
    on_primary="#0D47A1",
    secondary="#CCC2DC",
    secondary_variant="#4A4458",
    on_secondary="#332D41",
    background="#121212",  # True dark background
    on_background="#E0E0E0",
    surface="#1E1E1E",  # Elevated surface
    on_surface="#E0E0E0",
    error="#EF5350",  # Light Red for dark mode
    on_error="#B71C1C",
    success="#66BB6A",  # Light Green for dark mode
    warning="#FFA726",  # Light Orange for dark mode
    info="#42A5F5",  # Light Blue for dark mode
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

    status_label_map = {
        # Task statuses
        "completed": "完了",
        "todays": "今日",
        "active": "進行中",
        # Project statuses
        "planned": "計画中",
        "on_hold": "保留",
        "cancelled": "中止",
    }
    normalized = status.strip().lower()
    return status_label_map.get(normalized, status)


# Material Design 3 セマンティックカラー取得関数
# NOTE: 現在はライトテーマのみ対応。将来的にはsettingsからテーマモードを取得して切り替える


def get_on_primary_color() -> str:
    """プライマリカラー上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        ボタンやチップなどのプライマリカラー背景上で使用するテキスト色。
        ライト/ダークテーマで自動的に適切なコントラスト比を保証。
    """
    # TODO: テーマモード取得後、DARK_COLORS.on_primary にも対応
    return LIGHT_COLORS.on_primary


def get_on_surface_color() -> str:
    """サーフェス上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        カードやパネル背景上で使用する基本テキスト色。
    """
    return LIGHT_COLORS.on_surface


def get_surface_color() -> str:
    """サーフェス（カード・パネル）背景色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return LIGHT_COLORS.surface


def get_background_color() -> str:
    """アプリ全体の背景色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return LIGHT_COLORS.background


def get_error_color() -> str:
    """エラー色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        エラーメッセージ、バリデーションエラー表示などに使用。
    """
    return LIGHT_COLORS.error


def get_success_color() -> str:
    """成功色を取得する。

    Returns:
        色コード（HEX形式）

    Note:
        成功メッセージ、完了ステータス表示などに使用。
    """
    return LIGHT_COLORS.success


def get_on_error_color() -> str:
    """エラー色背景上のテキスト色を取得する。

    Returns:
        色コード（HEX形式）
    """
    return LIGHT_COLORS.on_error


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
    accent_map = {
        "amber": UI_COLORS.warning,
        "blue": UI_COLORS.primary,
        "green": UI_COLORS.success,
        "primary": LIGHT_COLORS.primary,
        "purple": TAG_COLORS.purple,
    }
    return accent_map.get(color_name, LIGHT_COLORS.primary)


def get_accent_border_color(color_name: str = "primary") -> str:
    """アクセントカラーのボーダー色を取得する。

    Args:
        color_name: カラー名（primary, blue, amber など）

    Returns:
        色コード（HEX形式）
    """
    # amber は特別扱い（より明るいボーダー）
    if color_name == "amber":
        return "#FFC107"  # AMBER_400 相当

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
# - Priority: Medium (ユーザー体験向上)
# - 推奨実装時期: Settings View 統合完了後
