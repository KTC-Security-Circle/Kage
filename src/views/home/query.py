"""Home Query Definitions.

【責務】
    ホーム画面のデータ取得を抽象化する。
    ControllerとDataSource間のインターフェースを明確化する。

    - デイリーレビュー情報の取得
    - Inboxメモの取得
    - 統計情報の取得

【責務外（他層の担当）】
    - UI表示 → View/Presenter
    - 状態保持 → State
    - 実際のデータ永続化 → ApplicationService/Repository

【設計上の特徴】
    - Protocolによる抽象化（依存性逆転）
    - テスト用のインメモリ実装を提供
    - 型安全なインターフェース定義

【アーキテクチャ上の位置づけ】
    Controller → HomeQuery (Protocol)
                    ↓
                InMemoryHomeQuery (実装)
                    ↓
                サンプルデータ
"""

from __future__ import annotations

from typing import Any, Protocol


# TODO: [ロジック担当者向け] 実際のApplicationServiceと連携するHomeQueryの実装
# 実装箇所: src/logic/application/home_application_service.py
# 依存: TaskApplicationService, MemoApplicationService, ProjectApplicationService
# 優先度: High (Home View統合完了後に必須)
# 担当: TBD
class HomeQuery(Protocol):
    """ホーム画面データ取得のポート。"""

    def get_daily_review(self) -> dict[str, Any]:
        """デイリーレビュー情報を取得する。

        Returns:
            デイリーレビュー情報を含む辞書
        """
        ...

    def get_inbox_memos(self) -> list[dict[str, Any]]:
        """Inboxメモを取得する。

        Returns:
            Inboxメモのリスト
        """
        ...

    def get_stats(self) -> dict[str, int]:
        """統計情報を取得する。

        Returns:
            統計情報を含む辞書
        """
        ...


class InMemoryHomeQuery:
    """軽量なデフォルト実装。テスト・プロトタイピング用。"""

    def __init__(
        self,
        daily_review: dict[str, Any] | None = None,
        inbox_memos: list[dict[str, Any]] | None = None,
        stats: dict[str, int] | None = None,
    ) -> None:
        """InMemoryHomeQueryを初期化する。

        Args:
            daily_review: デイリーレビュー情報
            inbox_memos: Inboxメモのリスト
            stats: 統計情報
        """
        self._daily_review = dict(daily_review) if daily_review else {}
        self._inbox_memos = list(inbox_memos) if inbox_memos else []
        self._stats = dict(stats) if stats else {}

    def get_daily_review(self) -> dict[str, Any]:
        """デイリーレビュー情報を取得する。

        Returns:
            デイリーレビュー情報を含む辞書
        """
        return self._daily_review

    def get_inbox_memos(self) -> list[dict[str, Any]]:
        """Inboxメモを取得する。

        Returns:
            Inboxメモのリスト
        """
        return self._inbox_memos

    def get_stats(self) -> dict[str, int]:
        """統計情報を取得する。

        Returns:
            統計情報を含む辞書
        """
        return self._stats
