"""Settings View Validation Layer.

【責務】
    設定値の妥当性を検証する純粋関数を提供する。

    - ウィンドウサイズの範囲検証
    - データベースURLの形式検証
    - その他の設定値バリデーション

【責務外（他層の担当）】
    - 表示用整形 → Presenter
    - 永続化 → SettingsService
    - 状態管理 → State

【設計上の特徴】
    - 全関数が純粋関数（副作用なし）
    - 型安全な引数と返り値
    - ドメインルールの明示化
"""

from __future__ import annotations

from urllib.parse import urlparse

# ウィンドウサイズの制限
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
MAX_WINDOW_WIDTH = 3840
MAX_WINDOW_HEIGHT = 2160


def validate_window_size(width: int, height: int) -> tuple[bool, str | None]:
    """ウィンドウサイズの妥当性を検証する。

    Args:
        width: ウィンドウ幅
        height: ウィンドウ高さ

    Returns:
        (is_valid, error_message) のタプル
    """
    if width < MIN_WINDOW_WIDTH or height < MIN_WINDOW_HEIGHT:
        return False, f"ウィンドウサイズは {MIN_WINDOW_WIDTH}x{MIN_WINDOW_HEIGHT} 以上にしてください"

    if width > MAX_WINDOW_WIDTH or height > MAX_WINDOW_HEIGHT:
        return False, f"ウィンドウサイズは {MAX_WINDOW_WIDTH}x{MAX_WINDOW_HEIGHT} 以下にしてください"

    return True, None


def validate_database_url(url: str) -> tuple[bool, str | None]:
    """データベースURLの妥当性を検証する。

    Args:
        url: データベースURL

    Returns:
        (is_valid, error_message) のタプル
    """
    if not url:
        return False, "データベースURLを入力してください"

    if not url.startswith(("sqlite:///", "postgresql://", "mysql://")):
        return False, "サポートされていないデータベースURLです"

    # URL形式の基本的な検証
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.path:
            return False, "データベースURLの形式が不正です"
    except Exception:
        return False, "データベースURLの解析に失敗しました"

    return True, None


def validate_theme(theme: str) -> tuple[bool, str | None]:
    """テーマ値の妥当性を検証する。

    Args:
        theme: テーマ値

    Returns:
        (is_valid, error_message) のタプル
    """
    if theme not in ("light", "dark"):
        return False, f"無効なテーマ値です: {theme}"

    return True, None
