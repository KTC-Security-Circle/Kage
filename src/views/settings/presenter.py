"""Settings View Presenter Layer.

【責務】
    Presenter層は設定値を UI 表示用に整形する。
    View層から表示用ロジックを切り出し、純粋な変換処理を提供する。

    - テーマ値の表示用ラベル変換
    - ウィンドウサイズ・位置の表示形式変換

【責務外（他層の担当）】
    - 状態の保持 → State
    - イベントハンドリング → Controller
    - データの取得 → SettingsService
    - UI要素の構築 → View/Components
    - バリデーション → validation.py

【設計上の特徴】
    - 全関数が純粋関数（副作用なし）
    - 型安全な引数と返り値
    - データクラスによる構造化

【アーキテクチャ上の位置づけ】
    View → Presenter.format_xxx()  # 表示用整形
"""

from __future__ import annotations

from settings.models import AVAILABLE_THEMES

# ウィンドウサイズ・位置の要素数
_SIZE_POSITION_ELEMENT_COUNT = 2


def format_theme_label(theme: str) -> str:
    """テーマ値を表示用ラベルに変換する。

    Args:
        theme: テーマ値 ("light" or "dark")

    Returns:
        表示用ラベル
    """
    theme_dict = dict(AVAILABLE_THEMES)
    return theme_dict.get(theme, theme)


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
    return list(AVAILABLE_THEMES)
