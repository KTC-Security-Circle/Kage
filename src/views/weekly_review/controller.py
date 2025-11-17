"""週次レビュービューのコントローラー

ユースケース実行・状態更新・ApplicationService連携を担当。
"""

from loguru import logger

from logic.application.task_application_service import TaskApplicationService

from .state import WeeklyReviewState, WeeklyStats


class WeeklyReviewController:
    """週次レビューのビジネスロジック調整

    ApplicationServiceとの連携、状態の更新を担当。
    """

    def __init__(
        self,
        task_app_service: TaskApplicationService,
        state: WeeklyReviewState,
    ) -> None:
        """コントローラーを初期化

        Args:
            task_app_service: タスク管理のApplicationService
            state: レビュー状態
        """
        self.task_app_service = task_app_service
        self.state = state

    def load_initial_data(self) -> None:
        """初期データを読み込み

        タスク統計を取得して状態を更新する。

        Note:
            現在は TaskApplicationService からのデータ取得が未実装のため、
            すべての統計値を 0 で初期化している。
            実装時は task_app_service を使用してタスクデータを取得する。
        """
        logger.info("週次レビューの統計データを読み込み中")

        try:
            # TODO: TaskApplicationService を使用してタスクデータを取得
            # 実装例:
            # all_tasks = self.task_app_service.get_all_tasks()
            # tasks_by_status = self._group_tasks_by_status(all_tasks)
            # completed_this_week = self._filter_completed_this_week(all_tasks)

            # 暫定: 空の統計データで初期化
            self.state.stats = WeeklyStats(
                completed_tasks=0,
                focus_hours=0.0,
                inbox_count=0,
                waiting_count=0,
                someday_count=0,
                active_projects=0,
                completed_last_week=0,
            )

            logger.info(f"統計データ読み込み完了（暫定値）: {self.state.stats}")

        except Exception as e:
            logger.exception("統計データの読み込みに失敗")
            error_msg = f"統計データの初期化に失敗しました: {e}"
            raise RuntimeError(error_msg) from e


    def toggle_checklist_item(self, item_id: str) -> None:
        """チェックリスト項目の完了状態を切り替え

        Args:
            item_id: 項目ID
        """
        self.state.toggle_checklist_item(item_id)
        logger.debug(f"チェックリスト項目を切り替え: {item_id}")

    def start_wizard(self) -> None:
        """レビューウィザードを開始"""
        self.state.wizard_active = True
        logger.info("レビューウィザードを開始")

    def end_wizard(self) -> None:
        """レビューウィザードを終了"""
        self.state.wizard_active = False
        logger.info("レビューウィザードを終了")

    def reset_checklist(self) -> None:
        """チェックリストをリセット"""
        for item in self.state.checklist:
            item.completed = False
        logger.info("チェックリストをリセット")

    def get_tasks_by_status(self, status: str) -> list:
        """指定ステータスのタスクを取得

        Args:
            status: タスクステータス (todo/progress/waiting/completed など)

        Returns:
            タスクリスト

        Note:
            実装時は TaskApplicationService を使用してフィルタリングを行う。
            現在は暫定実装として空リストを返す。
        """
        # TODO: task_app_service を使用した実装
        # return self.task_app_service.get_tasks_by_status(status)
        logger.debug(f"get_tasks_by_status called with status={status} (not implemented)")
        return []
