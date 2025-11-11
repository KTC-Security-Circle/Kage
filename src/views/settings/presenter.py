"""Settings View Presenter Layer.

【責務】
    Presenter層は設定値を UI 表示用に整形する。
    View層から表示用ロジックを切り出し、純粋な変換処理を提供する。

    - テーマ値の表示用ラベル変換
    - ウィンドウサイズ・位置の表示形式変換
    - 選択肢リストの生成
    - セクション用のデータ構造生成

【責務外（他層の担当）】
    - 状態の保持 → State
    - イベントハンドリング → Controller
    - データの取得 → Query
    - UI要素の構築 → View/Components

【設計上の特徴】
    - 全関数が純粋関数（副作用なし）
    - 型安全な引数と返り値
    - データクラスによる構造化

【アーキテクチャ上の位置づけ】
    View → Presenter.format_xxx()  # 表示用整形
         → Presenter.get_xxx_options()  # 選択肢取得
"""

from __future__ import annotations

# ウィンドウサイズ・位置の要素数
_SIZE_POSITION_ELEMENT_COUNT = 2

# ウィンドウサイズの制限
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
MAX_WINDOW_WIDTH = 3840
MAX_WINDOW_HEIGHT = 2160


def format_theme_label(theme: str) -> str:
    """テーマ値を表示用ラベルに変換する。

    Args:
        theme: テーマ値 ("light" or "dark")

    Returns:
        表示用ラベル
    """
    theme_labels = {
        "light": "ライト",
        "dark": "ダーク",
    }
    return theme_labels.get(theme, theme)


def format_window_size(size: list[int]) -> str:
    """ウィンドウサイズを表示用文字列に変換する。

    Args:
        size: [幅, 高さ] のリスト

    Returns:
        表示用文字列 (例: "1280 x 720")
    """
    if len(size) != _SIZE_POSITION_ELEMENT_COUNT:
        return "不明"
    return f"{size[0]} x {size[1]}"


def format_window_position(position: list[int]) -> str:
    """ウィンドウ位置を表示用文字列に変換する。

    Args:
        position: [X, Y] のリスト

    Returns:
        表示用文字列 (例: "X: 100, Y: 100")
    """
    if len(position) != _SIZE_POSITION_ELEMENT_COUNT:
        return "不明"
    return f"X: {position[0]}, Y: {position[1]}"


def get_theme_options() -> list[tuple[str, str]]:
    """テーマの選択肢を返す。

    Returns:
        (value, label) のタプルのリスト
    """
    return [
        ("light", "ライト"),
        ("dark", "ダーク"),
    ]


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

    return True, None
