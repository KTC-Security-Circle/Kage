"""週次レビュービューのコントローラー

ユースケース実行・状態更新・ApplicationService連携を担当。
"""

from loguru import logger

from logic.application.review_application_service import WeeklyReviewApplicationService
from views.weekly_review.components import MemoAction, ZombieTaskAction

from .state import WeeklyReviewState, WeeklyStats


class WeeklyReviewController:
    """週次レビューのビジネスロジック調整

    ApplicationServiceとの連携、状態の更新を担当。
    """

    def __init__(
        self,
        review_app_service: WeeklyReviewApplicationService,
        state: WeeklyReviewState,
    ) -> None:
        """コントローラーを初期化

        Args:
            review_app_service: 週次レビューのApplicationService
            state: レビュー状態
        """
        self.review_app_service = review_app_service
        self.state = state

    def load_initial_data(self) -> None:
        """初期データを読み込み

        WeeklyReviewApplicationService を使用して週次レビューデータを取得する。
        """
        logger.info("週次レビューデータを読み込み中")

        try:
            # WeeklyReviewInsights を取得
            insights = self.review_app_service.fetch_insights()

            # State にデータを格納
            self.state.completed_tasks_this_week = []  # TODO: insights から変換
            self.state.achievement_highlights = [item.description for item in insights.highlights.items]
            self.state.zombie_tasks = []  # TODO: insights.zombie_tasks.tasks から変換
            self.state.unprocessed_memos = []  # TODO: insights.memo_audits.audits から変換
            self.state.recommendations = []  # TODO: 推奨事項を生成

            # 統計データを設定（暫定）
            self.state.stats = WeeklyStats(
                completed_tasks=len(insights.highlights.items),
                focus_hours=0.0,
                inbox_count=0,
                waiting_count=len(insights.zombie_tasks.tasks),
                someday_count=0,
                active_projects=0,
                completed_last_week=0,
            )

            logger.info(
                f"週次レビューデータ読み込み完了: "
                f"highlights={len(insights.highlights.items)}, "
                f"zombies={len(insights.zombie_tasks.tasks)}, "
                f"memos={len(insights.memo_audits.audits)}"
            )

        except Exception as e:
            logger.exception("週次レビューデータの読み込みに失敗")
            error_msg = f"週次レビューデータの初期化に失敗しました: {e}"
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

    def next_step(self) -> None:
        """次のステップへ進む"""
        self.state.next_step()
        logger.info(f"ステップ {self.state.current_step} へ進む")

    def prev_step(self) -> None:
        """前のステップへ戻る"""
        self.state.prev_step()
        logger.info(f"ステップ {self.state.current_step} へ戻る")

    def set_zombie_task_decision(self, task_id: str, action: ZombieTaskAction) -> None:
        """ゾンビタスクの意思決定を記録

        Args:
            task_id: タスクID
            action: 選択されたアクション
        """
        self.state.set_zombie_task_decision(task_id, action)
        logger.debug(f"ゾンビタスク決定: {task_id} -> {action}")

    def set_memo_decision(self, memo_id: str, action: MemoAction) -> None:
        """メモの意思決定を記録

        Args:
            memo_id: メモID
            action: 選択されたアクション
        """
        self.state.set_memo_decision(memo_id, action)
        logger.debug(f"メモ決定: {memo_id} -> {action}")

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
