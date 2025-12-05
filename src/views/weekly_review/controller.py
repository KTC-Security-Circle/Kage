"""週次レビュービューのコントローラー

ユースケース実行・状態更新・ApplicationService連携を担当。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from views.weekly_review.components import MemoAction, PlanTaskData, RecommendationData, ZombieTaskAction

from .state import MemoReviewItem, WeeklyReviewState, WeeklyStats, ZombieTaskReviewItem

if TYPE_CHECKING:  # pragma: no cover - 型チェック専用
    from uuid import UUID

    from logic.application.memo_application_service import MemoApplicationService
    from logic.application.review_application_service import WeeklyReviewApplicationService
    from logic.application.task_application_service import TaskApplicationService
    from models import (
        MemoAuditInsight,
        MemoRead,
        TaskRead,
        WeeklyReviewHighlightsItem,
        WeeklyReviewInsights,
        WeeklyReviewMemoAuditPayload,
        WeeklyReviewZombiePayload,
        ZombieTaskInsight,
    )


class WeeklyReviewController:
    """週次レビューのビジネスロジック調整

    ApplicationServiceとの連携、状態の更新を担当。
    """

    def __init__(
        self,
        task_app_service: TaskApplicationService,
        review_app_service: WeeklyReviewApplicationService,
        memo_app_service: MemoApplicationService,
        state: WeeklyReviewState,
    ) -> None:
        """コントローラーを初期化

        Args:
            task_app_service: タスク管理のApplicationService
            review_app_service: 週次レビュー Application Service
            memo_app_service: メモ Application Service
            state: レビュー状態
        """
        self.task_app_service = task_app_service
        self.review_app_service = review_app_service
        self.memo_app_service = memo_app_service
        self.state = state

    def load_initial_data(self) -> None:
        """初期データを読み込み Application Service の結果で状態を更新する。"""
        logger.info("週次レビューのインサイトを取得中")

        try:
            insights = self.review_app_service.fetch_insights()
            self._update_state_from_insights(insights)
            logger.info("週次レビューのインサイト読み込み完了")
        except Exception as exc:
            logger.exception("週次レビューインサイトの読み込みに失敗")
            error_msg = f"週次レビューデータの取得に失敗しました: {exc}"
            raise RuntimeError(error_msg) from exc

    def _update_state_from_insights(self, insights: WeeklyReviewInsights) -> None:
        """WeeklyReviewInsights から ViewState を更新する。"""
        period = insights.metadata.period
        self.state.current_week_start = period.start
        self.state.current_week_end = period.end
        self.state.highlights_intro = insights.highlights.intro
        self.state.achievement_highlights = self._format_highlights(insights.highlights.items)

        completed_tasks = self._load_completed_tasks(insights.highlights.items)
        self.state.completed_tasks_this_week = completed_tasks

        zombie_entries = self._build_zombie_entries(insights.zombie_tasks)
        memo_entries = self._build_memo_entries(insights.memo_audits)

        self.state.zombie_tasks = zombie_entries
        self.state.unprocessed_memos = memo_entries
        self.state.recommendations = self._build_recommendations(zombie_entries, memo_entries)

        completed_count = len(completed_tasks)
        inbox_count = len(memo_entries)
        self.state.stats = WeeklyStats(
            completed_tasks=completed_count,
            focus_hours=0.0,
            inbox_count=inbox_count,
            waiting_count=0,
            someday_count=0,
            active_projects=len(insights.metadata.project_filters) or len(self.state.recommendations),
            completed_last_week=completed_count,
        )
        self.state.data_loaded = True

    def _format_highlights(self, items: list[WeeklyReviewHighlightsItem]) -> list[str]:
        """ハイライト項目をUI表示用のテキストに整形する。"""
        formatted: list[str] = []
        for item in items:
            description = item.description.strip()
            formatted.append(f"{item.title}: {description}")
        return formatted

    def _load_completed_tasks(self, items: list[WeeklyReviewHighlightsItem]) -> list[TaskRead]:
        """ハイライトに含まれるタスクIDから TaskRead を読み込む。"""
        tasks: list[TaskRead] = []
        ordered_ids: dict[UUID, None] = {}
        for item in items:
            for task_id in item.source_task_ids:
                ordered_ids[task_id] = None

        for task_id in ordered_ids:
            task = self._safe_get_task(task_id)
            if task is not None:
                tasks.append(task)
        return tasks

    def _build_zombie_entries(self, payload: WeeklyReviewZombiePayload) -> list[ZombieTaskReviewItem]:
        """ゾンビタスクのペイロードをUI表示用データに変換する。"""
        return [self._map_zombie_insight(insight) for insight in payload.tasks]

    def _map_zombie_insight(self, insight: ZombieTaskInsight) -> ZombieTaskReviewItem:
        """単一のゾンビタスクインサイトを表示用データにマッピングする。"""
        suggestion = insight.suggestions[0].rationale if insight.suggestions else insight.memo_excerpt
        reason_parts = [f"{insight.stale_days}日停滞"]
        if suggestion:
            reason_parts.append(suggestion)
        reason = " / ".join(reason_parts)
        return ZombieTaskReviewItem(
            id=str(insight.task_id),
            title=insight.title,
            reason=reason,
            stale_days=insight.stale_days,
        )

    def _build_memo_entries(self, payload: WeeklyReviewMemoAuditPayload) -> list[MemoReviewItem]:
        """未処理メモペイロードをUI表示用データに変換する。"""
        return [self._map_memo_audit(audit) for audit in payload.audits]

    def _map_memo_audit(self, audit: MemoAuditInsight) -> MemoReviewItem:
        """単一のメモ監査情報を表示用にマッピングする。"""
        memo = self._safe_get_memo(audit.memo_id)
        title = memo.title if memo else audit.summary
        content = memo.content if memo else audit.guidance or audit.summary
        return MemoReviewItem(
            id=str(audit.memo_id),
            title=title,
            content=content,
            suggestion=audit.guidance,
            recommended_route=audit.recommended_route,
        )

    def _build_recommendations(
        self,
        zombie_entries: list[ZombieTaskReviewItem],
        memo_entries: list[MemoReviewItem],
    ) -> list[RecommendationData]:
        """ゾンビタスクとメモ分析から推奨事項カードを生成する。"""
        recommendations: list[RecommendationData] = []

        if zombie_entries:
            recommendations.append(
                RecommendationData(
                    title="停滞タスクの再起動",
                    count=len(zombie_entries),
                    description="停滞期間が長いタスクです。次のアクションを決めてリストを軽くしましょう。",
                    tasks=[
                        PlanTaskData(task_id=entry.id, title=entry.title, due_date=f"{entry.stale_days}日停滞")
                        for entry in zombie_entries[:5]
                    ],
                )
            )

        actionable_memos = [memo for memo in memo_entries if memo.recommended_route in {None, "task"}]
        if actionable_memos:
            recommendations.append(
                RecommendationData(
                    title="メモをタスク化",
                    count=len(actionable_memos),
                    description="Inboxにすぐタスク化できるメモがあります。週明けの着手対象にどうぞ。",
                    tasks=[
                        PlanTaskData(
                            task_id=memo.id,
                            title=memo.title,
                            due_date=self._route_to_label(memo.recommended_route),
                        )
                        for memo in actionable_memos[:5]
                    ],
                )
            )

        return recommendations

    def _route_to_label(self, route: str | None) -> str:
        mapping = {
            "task": "タスク化推奨",
            "reference": "資料化",
            "someday": "Someday",
            "discard": "棚卸し候補",
        }
        return mapping.get(route or "task", "タスク化推奨")

    def _safe_get_task(self, task_id: UUID) -> TaskRead | None:
        """TaskApplicationService から単一タスクを取得し、失敗時は None を返す。"""
        try:
            return self.task_app_service.get_by_id(task_id, with_details=True)
        except Exception as exc:  # pragma: no cover - ログ用
            logger.warning("タスク取得に失敗しました (id=%s): %s", task_id, exc)
            return None

    def _safe_get_memo(self, memo_id: UUID) -> MemoRead | None:
        """MemoApplicationService からメモを取得し、失敗時は None を返す。"""
        try:
            return self.memo_app_service.get_by_id(memo_id, with_details=False)
        except Exception as exc:  # pragma: no cover - ログ用
            logger.warning("メモ取得に失敗しました (id=%s): %s", memo_id, exc)
            return None

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
