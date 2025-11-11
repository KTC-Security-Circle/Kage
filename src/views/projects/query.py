"""プロジェクト取得系クエリの抽象化

CQRS の Query 側として、プロジェクトデータの取得ロジックを抽象化。
Repository層との疎結合を実現し、テスタビリティを向上させる。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterable

    from models import ProjectStatus


class ProjectQuery(Protocol):
    """プロジェクト取得系クエリの抽象インターフェース。

    Repository層や外部データソースへの依存を抽象化し、
    テスト時のモック化と本番環境での実装の切り替えを容易にする。
    """

    def list_projects(
        self,
        keyword: str = "",
        status: ProjectStatus | None = None,
    ) -> Iterable[dict[str, str]]:
        """プロジェクト一覧を取得する。

        Args:
            keyword: 検索キーワード（タイトルと説明で部分一致検索）
            status: ステータスフィルタ（None の場合は全ステータス）

        Returns:
            フィルタリングされたプロジェクトのイテラブル
        """
        ...
        # TODO(実装者向け): 将来拡張の検討事項
        # - ページング(cursor/limit)、サーバーサイドソート(sort_key/direction)
        # - get_project_by_id(project_id: str) の追加で詳細取得を効率化
        # - これらは ApplicationService → Repository 層で実装し、ここでは抽象化のみ提供


class InMemoryProjectQuery:
    """軽量なインメモリプロジェクトクエリ実装。

    テスト・プロトタイピング用のデフォルト実装。
    実際のプロダクションでは Repository 連携の実装に置き換える。

    Attributes:
        _data: プロジェクトデータのリスト
    """

    def __init__(self, data: list[dict[str, str]] | None = None) -> None:
        """InMemoryProjectQuery を初期化する。

        Args:
            data: 初期データ（None の場合は空リスト）
        """
        self._data = data or []

    def list_projects(
        self,
        keyword: str = "",
        status: ProjectStatus | None = None,
    ) -> list[dict[str, str]]:
        """プロジェクト一覧を取得する。

        Args:
            keyword: 検索キーワード
            status: ステータスフィルタ

        Returns:
            フィルタリングされたプロジェクトのリスト
        """
        items = self._data

        # キーワード検索（タイトルと説明で部分一致）
        if keyword:
            k = keyword.lower()
            items = [
                x for x in items if k in str(x.get("title", "")).lower() or k in str(x.get("description", "")).lower()
            ]

        # ステータスフィルタ（日本語/英語の両方に対応）
        if status is not None:
            jp_map = {
                "active": "進行中",
                "on_hold": "保留",
                "completed": "完了",
                "cancelled": "キャンセル",
            }
            english = status.value
            japanese = jp_map.get(english, english)
            items = [x for x in items if x.get("status") in (english, japanese)]
        return items

    # TODO(実装者向け): プロダクション実装の観点
    # - Repository 経由のクエリ実装では、DB/検索エンジンでの LIKE/全文検索を使用してください。
    # - project_id 単体取得用のメソッドを追加し、詳細画面の取得効率を最適化すると良いです。

    def add_project(self, project: dict[str, str]) -> None:
        """プロジェクトを追加する（テスト用）。

        Args:
            project: 追加するプロジェクトデータ
        """
        self._data.append(project)

    def clear(self) -> None:
        """全データをクリアする（テスト用）。"""
        self._data.clear()
