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
        """
        logger.info("週次レビューの統計データを読み込み中")

        # タスク統計を取得（簡易実装）
        # TODO: 実際のタスクデータを取得するメソッドを実装
        tasks_by_status = {}

        # 統計データを計算
        inbox_tasks = tasks_by_status.get("inbox", [])
        waiting_tasks = tasks_by_status.get("waiting", [])
        someday_tasks = tasks_by_status.get("someday", [])
        completed_tasks = tasks_by_status.get("completed", [])

        # アクティブなプロジェクト数（簡易実装: Noneで代用）
        active_projects = 0

        # 今週完了したタスク数を計算
        completed_last_week = sum(1 for task in completed_tasks if self._is_completed_this_week(task))

        # 状態を更新
        self.state.stats = WeeklyStats(
            completed_tasks=len(completed_tasks),
            focus_hours=0.0,  # TODO: 集中時間の取得機能実装
            inbox_count=len(inbox_tasks),
            waiting_count=len(waiting_tasks),
            someday_count=len(someday_tasks),
            active_projects=active_projects,
            completed_last_week=completed_last_week,
        )

        logger.info(f"統計データ読み込み完了: {self.state.stats}")
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

    def get_tasks_by_status(self, _status: str) -> list:
        """指定ステータスのタスクを取得

        Args:
            _status: タスクステータス (next/waiting/someday)

        Returns:
            タスクリスト
        """
        # TODO: 実際のタスク取得メソッドを実装
        # 現在は簡易実装として空リストを返す
        return []

    def _is_completed_this_week(self, _task: dict) -> bool:
        """タスクが今週完了したかチェック

        Args:
            _task: タスクオブジェクト

        Returns:
            今週完了した場合True
        """
        # TODO: タスクの完了日時を取得して判定
        # 現在は簡易実装としてFalseを返す
        return False
