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

        # ステータスフィルタ
        if status is not None:
            items = [x for x in items if x.get("status") == status.value]

        return items

    def add_project(self, project: dict[str, str]) -> None:
        """プロジェクトを追加する（テスト用）。

        Args:
            project: 追加するプロジェクトデータ
        """
        self._data.append(project)

    def clear(self) -> None:
        """全データをクリアする（テスト用）。"""
        self._data.clear()
