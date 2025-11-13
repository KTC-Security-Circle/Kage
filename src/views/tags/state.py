"""Tags View の状態モデル。

表示状態の単一ソースとして、タグ一覧、検索、選択、ロード状態を管理する。
UIやサービス層から独立した純粋なデータクラスであり、副作用は持たない。
"""

from __future__ import annotations

from dataclasses import dataclass, field

TagDict = dict[str, str]


@dataclass(slots=True)
class TagsViewState:
    """タグビュー状態。

    Attributes:
        items: 取得済みタグの生配列 (辞書ベースの軽量DTO)
        search_text: 現在の検索文字列 (正規化後を保持)
        selected_id: 選択中タグのID（未選択時None）
        initial_loaded: 初回ロード済みフラグ
    """

    items: list[TagDict] = field(default_factory=list)
    search_text: str = ""
    selected_id: str | None = None
    initial_loaded: bool = False

    # 派生プロパティ（簡易実装: 都度計算）
    @property
    def filtered_tags(self) -> list[TagDict]:
        """検索条件に合致したタグ配列を返す。

        Returns:
            フィルタ済みタグ一覧
        """
        if not self.search_text:
            return list(self.items)
        q = self.search_text
        return [t for t in self.items if q in t.get("name", "").lower() or q in t.get("description", "").lower()]

    @property
    def filtered_count(self) -> int:
        """表示中件数を返す。"""
        return len(self.filtered_tags)

    def reconcile_after_delete(self) -> None:
        """削除後に選択状態と一貫性を調整する。"""
        if self.selected_id and not any(t["id"] == self.selected_id for t in self.items):
            self.selected_id = None
