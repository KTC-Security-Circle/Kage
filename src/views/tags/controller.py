"""Tags View Controller

ユースケースレベルの操作 (初期ロード/検索更新/選択/削除スタブ/更新) を
State に適用する。永続化やサービス呼び出しは後続で ApplicationServices に
差し替えるため、現在は軽量 Mock 実装。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import sort_tags_by_name

if TYPE_CHECKING:
    from .query import SearchQuery
    from .state import TagDict, TagsViewState


class TagsController:
    """Tags用Controller。"""

    def __init__(self, state: TagsViewState) -> None:
        self.state = state
        # TODO: ApplicationService依存注入
        # 理由: 永続化層への接続（TagApplicationService, MemoApplicationService, TaskApplicationService）
        # 実装: __init__(self, state: TagsViewState, tag_service: TagApplicationService, ...)
        # 置換先: src/logic/application/tag_application_service.py

        # 関連アイテムのMockデータ（将来はApplicationService経由で取得）
        self._mock_memos: list[dict[str, str]] = [
            {
                "id": "memo-1",
                "title": "緊急タスクのメモ",
                "description": "本日中に完了すべきタスクの詳細",
                "tag_name": "緊急",
            },
            {
                "id": "memo-2",
                "title": "開発ガイドライン",
                "description": "新規開発時の注意事項まとめ",
                "tag_name": "開発",
            },
        ]
        self._mock_tasks: list[dict[str, str]] = [
            {
                "id": "task-1",
                "title": "UI実装",
                "description": "ダッシュボード画面の実装",
                "status": "todays",
                "tag_name": "開発",
            },
            {
                "id": "task-2",
                "title": "バグ修正",
                "description": "ログイン画面のバグ修正",
                "status": "completed",
                "tag_name": "緊急",
            },
        ]

    # ------------------------------------------------------------------
    # Initial Load
    # ------------------------------------------------------------------
    def load_initial_tags(self) -> None:
        """初期タグをロードする (Mock)。"""
        # TODO: ApplicationService経由でタグ一覧を取得
        # 理由: DBからタグデータをロード（models.Tag → TagDict変換）
        # 実装: tags = await self.tag_service.get_all_tags()
        # 置換先: src/logic/application/tag_application_service.py の get_all_tags()
        if self.state.initial_loaded:
            return
        mock: list[TagDict] = [
            {
                "id": "1",
                "name": "緊急",
                "color": "#f44336",
                "description": "緊急度の高いタスクやメモに使用するタグです。",
                "created_at": "2024-01-15 10:30:00",
                "updated_at": "2024-03-20 14:45:00",
            },
            {
                "id": "2",
                "name": "開発",
                "color": "#2196f3",
                "description": "開発関連のタスクやメモに使用します。コーディング、レビュー、テストなど。",
                "created_at": "2024-01-10 09:00:00",
                "updated_at": "2024-03-18 16:20:00",
            },
            {
                "id": "3",
                "name": "デザイン",
                "color": "#e91e63",
                "description": "UI/UXデザイン関連のタスクやメモに付与します。",
                "created_at": "2024-01-20 11:15:00",
                "updated_at": "2024-02-28 10:00:00",
            },
        ]
        self.state.items = sort_tags_by_name(mock)
        self.state.initial_loaded = True

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def update_search(self, query: SearchQuery) -> None:
        """検索文字列を更新する。"""
        self.state.search_text = query.normalized

    # ------------------------------------------------------------------
    # Select
    # ------------------------------------------------------------------
    def select_tag(self, tag_id: str) -> None:
        """タグを選択。存在しなければ何もしない。"""
        if any(t["id"] == tag_id for t in self.state.items):
            self.state.selected_id = tag_id

    # ------------------------------------------------------------------
    # Delete (Stub)
    # ------------------------------------------------------------------
    def delete_tag_stub(self, tag_id: str) -> None:
        """削除スタブ。永続層未接続のため State 内配列から除去のみ。"""
        # TODO: ApplicationService経由でタグを削除
        # 理由: DB上のタグレコードを削除（カスケード: Task_Tag, Memo_Tag も削除）
        # 実装: await self.tag_service.delete_tag(tag_id)
        # 置換先: src/logic/application/tag_application_service.py の delete_tag()
        # 注意: 削除前に関連メモ・タスクの件数を確認し、ユーザーに警告ダイアログ表示が望ましい
        self.state.items = [t for t in self.state.items if t["id"] != tag_id]
        self.state.reconcile_after_delete()

    # ------------------------------------------------------------------
    # Create (Stub)
    # ------------------------------------------------------------------
    def create_tag_stub(self) -> None:
        """新規作成スタブ。Mockタグを追加。"""
        # TODO: ApplicationService経由でタグを作成
        # 理由: DB上にタグレコードを新規追加
        # 実装: new_tag = await self.tag_service.create_tag(name, color, description)
        # 置換先: src/logic/application/tag_application_service.py の create_tag()
        # 注意: 実際はダイアログから入力値を受け取る（name, color, description）
        from datetime import datetime

        new_id = str(len(self.state.items) + 1)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state.items.append(
            {
                "id": new_id,
                "name": f"新規タグ{new_id}",
                "color": "#607d8b",
                "description": "新規作成されたタグです(スタブ)",
                "created_at": now,
                "updated_at": now,
            }
        )
        self.state.items = sort_tags_by_name(self.state.items)

    # ------------------------------------------------------------------
    # Refresh (Stub)
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """更新処理スタブ。現在は並び替えのみ。"""
        # TODO: ApplicationService経由でタグ一覧を再取得
        # 理由: DBの最新状態を反映（他ユーザーの変更等）
        # 実装: tags = await self.tag_service.get_all_tags()
        # 置換先: src/logic/application/tag_application_service.py の get_all_tags()
        self.state.items = sort_tags_by_name(self.state.items)

    # ------------------------------------------------------------------
    # Get Related Items
    # ------------------------------------------------------------------
    def get_related_memos(self, tag_name: str) -> list[dict[str, str]]:
        """指定タグに関連するメモを取得する (Mock)。

        Args:
            tag_name: タグ名

        Returns:
            関連メモのリスト
        """
        # TODO: ApplicationService経由で関連メモを取得
        # 理由: Memo_Tag中間テーブルを使用してタグに紐づくメモを取得
        # 実装: memos = await self.memo_service.get_memos_by_tag_name(tag_name)
        # 置換先: src/logic/application/memo_application_service.py の get_memos_by_tag_name()
        # または: src/logic/queries/memo_queries.py に専用クエリを追加
        return [m for m in self._mock_memos if m.get("tag_name") == tag_name]

    def get_related_tasks(self, tag_name: str) -> list[dict[str, str]]:
        """指定タグに関連するタスクを取得する (Mock)。

        Args:
            tag_name: タグ名

        Returns:
            関連タスクのリスト
        """
        # TODO: ApplicationService経由で関連タスクを取得
        # 理由: Task_Tag中間テーブルを使用してタグに紐づくタスクを取得
        # 実装: tasks = await self.task_service.get_tasks_by_tag_name(tag_name)
        # 置換先: src/logic/application/task_application_service.py の get_tasks_by_tag_name()
        # または: src/logic/queries/task_queries.py に専用クエリを追加
        return [t for t in self._mock_tasks if t.get("tag_name") == tag_name]

    def get_tag_counts(self, tag_name: str) -> dict[str, int]:
        """指定タグのアイテムカウントを取得する (Mock)。

        Args:
            tag_name: タグ名

        Returns:
            カウント情報の辞書 (memo_count, task_count, total_count)
        """
        # TODO: ApplicationService/Queries経由で集計クエリを実行
        # 理由: 毎回全件取得は非効率。COUNT()クエリで件数のみ取得
        # 実装: counts = await self.tag_service.get_tag_item_counts(tag_name)
        # 置換先: src/logic/queries/tag_queries.py に count_memos_by_tag(), count_tasks_by_tag() 追加
        memo_count = sum(1 for m in self._mock_memos if m.get("tag_name") == tag_name)
        task_count = sum(1 for t in self._mock_tasks if t.get("tag_name") == tag_name)
        return {
            "memo_count": memo_count,
            "task_count": task_count,
            "total_count": memo_count + task_count,
        }
