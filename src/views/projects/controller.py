"""プロジェクト画面のコントローラー

イベント→状態更新→データ取得→並び替え→ViewModel生成→再描画の調停役。
MVP パターンの Presenter と View の橋渡しを行う。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .query import ProjectQuery

from loguru import logger

from .ordering import apply_order, get_order_strategy
from .presenter import ProjectCardVM, ProjectDetailVM, to_card_vm, to_detail_vm
from .state import ProjectState


class ProjectController:
    """プロジェクト画面のメインコントローラー。

    UI状態の管理、データ取得、並び替え、ViewModel生成を調停し、
    View層への更新通知を行う。状態管理とビジネスロジックを分離する。

    Attributes:
        _query: プロジェクトデータ取得用クエリ
        _state: 現在のUI状態
        _on_list_change: リスト更新時のコールバック
        _on_detail_change: 詳細更新時のコールバック
    """

    def __init__(
        self,
        query: ProjectQuery,
        on_list_change: Callable[[list[ProjectCardVM]], None],
        on_detail_change: Callable[[ProjectDetailVM | None], None],
    ) -> None:
        """ProjectController を初期化する。

        Args:
            query: プロジェクトデータ取得用クエリ
            on_list_change: リスト更新時のコールバック関数
            on_detail_change: 詳細更新時のコールバック関数
        """
        self._query = query
        self._state = ProjectState()
        self._on_list_change = on_list_change
        self._on_detail_change = on_detail_change

    def show_error_snackbar(self, message: str) -> None:
        """ユーザー向けにエラーを通知する。

        デフォルト実装では loguru にエラーを記録するだけで、実際の UI 表示
        (例: Flet の SnackBar/AlertDialog) は View 層でこのメソッドをオーバーライド
        して実装してください。

        Args:
            message: ユーザーに表示するエラーメッセージ
        """
        # デフォルトはログ出力のみ
        logger.error(message)

    @property
    def state(self) -> ProjectState:
        """現在のUI状態を取得する。

        Returns:
            現在の ProjectState インスタンス
        """
        return self._state

    def set_keyword(self, keyword: str) -> None:
        """検索キーワードを設定する。

        Args:
            keyword: 新しい検索キーワード
        """
        logger.debug(f"検索キーワード設定: '{keyword}'")
        new_state = self._state.update(keyword=keyword)
        self._update_and_render(new_state)

    def set_status(self, status: str | None) -> None:
        """ステータスフィルタを設定する。

        Args:
            status: 新しいステータスフィルタ（None の場合は全て）
        """
        from models import ProjectStatus

        status_filter = None
        if status:
            # TODO: 正規化をドメイン層へ
            #  - normalize_status は現在 views.shared.status_utils にありますが、
            #    将来的には models 側（例: models/project.py）で ProjectStatus と
            #    一緒に提供し、UI層はドメインの変換APIのみを利用する設計にする。
            from views.shared.status_utils import normalize_status

            normalized = normalize_status(status)
            try:
                status_filter = ProjectStatus(normalized)
            except ValueError:
                logger.warning(f"無効なステータス値: {status}")
                return

        logger.debug(f"ステータスフィルタ設定: {status_filter}")
        new_state = self._state.update(status=status_filter)
        self._update_and_render(new_state)

    def set_sort(self, key: str, *, desc: bool | None = None) -> None:
        """並び替え設定を変更する。

        Args:
            key: 並び替えキー
            desc: 降順フラグ（None の場合は現在の設定を維持）
        """
        current_desc = desc if desc is not None else self._state.sort_desc
        logger.debug(f"並び替え設定: key={key}, desc={current_desc}")

        try:
            # 並び替えキーの妥当性チェック
            get_order_strategy(key)
            new_state = self._state.update(sort_key=key, sort_desc=current_desc)
            self._update_and_render(new_state)
        except KeyError as e:
            logger.error(f"並び替えキーエラー: {e}")

    def set_sort_asc(self, key: str) -> None:
        """並び替えを昇順で設定する。

        Args:
            key: 並び替えキー
        """
        self.set_sort(key, desc=False)

    def set_sort_desc(self, key: str) -> None:
        """並び替えを降順で設定する。

        Args:
            key: 並び替えキー
        """
        self.set_sort(key, desc=True)

    def toggle_sort_direction(self) -> None:
        """並び替え方向を切り替える。"""
        new_state = self._state.toggle_sort_direction()
        logger.debug(f"並び替え方向切替: desc={new_state.sort_desc}")
        self._update_and_render(new_state)

    def select_project(self, project_id: str) -> None:
        """プロジェクトを選択する。

        Args:
            project_id: 選択するプロジェクトのID
        """
        logger.debug(f"プロジェクト選択: {project_id}")
        new_state = self._state.update(selected_id=project_id)
        self._update_and_render(new_state)

    def clear_selection(self) -> None:
        """プロジェクト選択をクリアする。"""
        logger.debug("プロジェクト選択クリア")
        new_state = self._state.clear_selection()
        self._update_and_render(new_state)

    def refresh(self) -> None:
        """データを再読み込みして画面を更新する。"""
        logger.debug("データ再読み込み")
        self._update_and_render(self._state)

    def create_project(self, project: dict[str, str], *, select: bool = True) -> None:
        """新規プロジェクトを追加し、必要に応じて選択・再描画する。

        テスト/デモ用の `InMemoryProjectQuery` では `add_project` を持つため、
        それを利用してデータを追加する。実運用では Repository 経由の作成に置き換える。

        Args:
            project: 追加するプロジェクト辞書（Presenterが扱えるキーを推奨）
            select: 追加後に選択状態にするかどうか
        """
        try:
            # TODO: 作成処理の本実装
            # - 現状は InMemory 用の add_project があれば呼び出す暫定実装です。
            # - 実装では ApplicationService.create_project(...) を呼び出し、
            #   成功時に refresh() で再取得してください（ID で選択維持する場合は応答の ID を使用）。
            add_fn = getattr(self._query, "add_project", None)
            if callable(add_fn):
                add_fn(project)  # type: ignore[misc]
            else:
                logger.warning("クエリが add_project をサポートしていません。")

            # 追加後に選択する場合は state を更新
            new_state = self._state
            if select:
                new_state = new_state.update(selected_id=str(project.get("id", "")))

            # 内部更新関数を用いて強制的にリスト/詳細を再描画
            self._state = new_state
            self._update_list()
            self._update_detail()
        except ValueError as e:
            logger.error(f"プロジェクトデータのバリデーションエラー: {e}")
            # TODO: ユーザーへの通知処理（例: Fletの AlertDialog や SnackBar を使用）
        except Exception as e:
            logger.exception(f"プロジェクト追加中に予期しないエラーが発生しました: {e}")
            # TODO: ユーザーへの通知処理（例: Fletの AlertDialog や SnackBar を使用）

    def _update_and_render(self, new_state: ProjectState) -> None:
        """状態を更新してUIを再描画する。

        Args:
            new_state: 新しいUI状態
        """
        old_state = self._state
        self._state = new_state

        # リスト更新（検索・フィルタ・並び替えが変更された場合）
        if (
            old_state.keyword != new_state.keyword
            or old_state.status != new_state.status
            or old_state.sort_key != new_state.sort_key
            or old_state.sort_desc != new_state.sort_desc
        ):
            self._update_list()

        # 詳細更新（選択が変更された場合）
        if old_state.selected_id != new_state.selected_id:
            self._update_detail()

    def _update_list(self) -> None:
        """プロジェクトリストを更新する。"""
        try:
            # データ取得
            # TODO: ページング/ソートをサーバーサイドへ委譲する検討
            # - 件数が増える場合は list_projects に cursor/limit 等の引数を追加し、
            #   ApplicationService → Repository で最適化してください。
            items = self._query.list_projects(
                keyword=self._state.keyword,
                status=self._state.status,
            )

            # 並び替え
            strategy = get_order_strategy(self._state.sort_key)
            ordered_items = apply_order(items, strategy, desc=self._state.sort_desc)

            # ViewModel変換
            view_models = to_card_vm(ordered_items)

            # UI更新通知
            self._on_list_change(view_models)
            logger.debug(f"プロジェクトリスト更新: {len(view_models)}件")

        except Exception as e:
            logger.error(f"プロジェクトリスト更新エラー: {e}")
            # エラー時は空リストで更新
            self._on_list_change([])

    def _update_detail(self) -> None:
        """プロジェクト詳細を更新する。"""
        try:
            if not self._state.selected_id:
                # 選択なしの場合
                self._on_detail_change(None)
                logger.debug("プロジェクト詳細クリア")
                return

            # 選択されたプロジェクトを検索
            # TODO: ID 取得 API の利用
            # - list → 探索は暫定です。ProjectQuery に get_project_by_id を追加し、
            #   Repository で最適に取得してください。
            items = self._query.list_projects()
            selected_project = None
            for item in items:
                if str(item.get("id")) == self._state.selected_id:
                    selected_project = item
                    break

            if selected_project:
                # ViewModel変換
                detail_vm = to_detail_vm(selected_project)
                self._on_detail_change(detail_vm)
                logger.debug(f"プロジェクト詳細更新: {selected_project.get('title', '')}")
            else:
                # 選択されたプロジェクトが見つからない場合
                logger.warning(f"選択されたプロジェクトが見つかりません: {self._state.selected_id}")
                self._on_detail_change(None)

        except Exception as e:
            # ログ出力（長文を分割して可読性と行長制限を両立）
            msg = f"プロジェクト詳細更新中にエラーが発生しました: project_id={self._state.selected_id}, error={e}"
            logger.exception(msg)
            # [AI GENERATED] ユーザーにエラー内容を通知
            if hasattr(self, "show_error_snackbar") and callable(self.show_error_snackbar):
                user_msg = (
                    f"プロジェクト詳細の取得中にエラーが発生しました（ID: {self._state.selected_id}）。"
                    "詳細はログを参照してください。"
                )
                self.show_error_snackbar(user_msg)
            self._on_detail_change(None)
