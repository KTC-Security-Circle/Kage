"""複数コンポーネントで共有する定数

【配置基準】
- 2つ以上のコンポーネントで使用される定数のみ
- アプリ全体のUI統一性に関わる定数（パディング、ボーダー、色等）

【単一コンポーネント専用の定数】
- 各コンポーネントファイル内で定義すること
  例: memo_card.py の MAX_CONTENT_LINES
      action_bar.py の MIN_SEARCH_LENGTH
"""

from typing import Final

# ========================================
# レイアウト共通定数
# ========================================

CARD_PADDING: Final[int] = 12
"""カードの内部パディング（複数のカード系コンポーネントで共有）"""

CARD_BORDER_RADIUS: Final[int] = 8
"""カードの角丸半径（複数のカード系コンポーネントで共有）"""

SELECTED_BORDER_WIDTH: Final[int] = 2
"""選択状態の枠線幅（複数のコンポーネントで共有）"""

DEFAULT_BORDER_WIDTH: Final[int] = 1
"""通常状態の枠線幅（複数のコンポーネントで共有）"""

ACTION_BAR_PADDING: Final[int] = 16
"""アクションバーのパディング"""

# ========================================
# デフォルト値共通定数
# ========================================

DEFAULT_DATE_TEXT: Final[str] = "—"
"""日付が不明な場合のデフォルト表示（複数のコンポーネントで共有）"""

DEFAULT_EMPTY_MESSAGE: Final[str] = "メモがありません"
"""リストが空の場合のデフォルトメッセージ"""

DEFAULT_SEARCH_PLACEHOLDER: Final[str] = "メモを検索..."
"""検索フィールドのデフォルトプレースホルダー（複数のコンポーネントで共有）"""

MIN_SEARCH_LENGTH: Final[int] = 2
"""検索クエリの最小文字数（複数のコンポーネントで共有）"""
