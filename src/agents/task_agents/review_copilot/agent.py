"""LLM/ルールベース併用で週次レビューを生成するエージェント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast
from uuid import uuid4

from agents.agent_conf import HuggingFaceModel, LLMProvider
from agents.base import AgentError
from agents.task_agents.review_copilot.highlights_agent import ReviewHighlightsAgent
from agents.task_agents.review_copilot.memo_audit_agent import MemoAuditSuggestionAgent
from agents.task_agents.review_copilot.zombie_agent import ZombieSuggestionAgent
from agents.utils import agents_logger
from models import (
    CompletedTaskDigest,
    MemoAuditDigest,
    MemoAuditInsight,
    WeeklyReviewHighlightsItem,
    WeeklyReviewHighlightsPayload,
    WeeklyReviewMemoAuditPayload,
    WeeklyReviewZombiePayload,
    ZombieTaskDigest,
    ZombieTaskInsight,
    ZombieTaskSuggestion,
)

POSITIVITY_PREFIX = "お疲れさまです！"
MEMO_LINE_THRESHOLD = 3
MemoRoute = Literal["task", "reference", "someday", "discard"]

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

    from agents.task_agents.review_copilot.highlights_agent import HighlightsState
    from agents.task_agents.review_copilot.memo_audit_agent import MemoAuditState
    from agents.task_agents.review_copilot.zombie_agent import ZombieTaskState


@dataclass(frozen=True, slots=True)
class _MemoRoutingRule:
    keyword: str
    route: MemoRoute
    guidance: str


class ReviewCopilotAgent:
    """週次レビュー用の軽量エージェント。

    実運用では LLM 呼び出しで最終文章を整える拡張を想定しつつ、
    本実装ではポジティブなテンプレートとヒューリスティクスで JSON を構築する。
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.FAKE,
        *,
        model_name: HuggingFaceModel | str | None = None,
        device: str | None = None,
        **agent_kwargs: object,
    ) -> None:
        self.provider = provider
        self._logger = agents_logger
        shared_kwargs = {
            "provider": provider,
            "model_name": model_name,
            "device": device,
            **agent_kwargs,
        }
        self._highlights_agent = ReviewHighlightsAgent(**shared_kwargs)
        self._zombie_agent = ZombieSuggestionAgent(**shared_kwargs)
        self._memo_agent = MemoAuditSuggestionAgent(**shared_kwargs)

    def build_highlights(self, completed: list[CompletedTaskDigest]) -> WeeklyReviewHighlightsPayload:
        """完了タスクから成果サマリーを生成する。"""
        if not completed:
            return self._build_highlights_fallback([])

        state: HighlightsState = {
            "completed_task_summaries": [
                " | ".join(
                    filter(
                        None,
                        [
                            digest.task.title,
                            digest.project_title,
                            digest.memo_excerpt or digest.task.description,
                        ],
                    )
                )
                for digest in completed
            ],
            "tone_hint": f"{len(completed)}件の成果を肯定的にまとめる",
        }
        try:
            result = self._highlights_agent.invoke(state, thread_id=str(uuid4()))
        except Exception:
            msg = "ReviewHighlightsAgent.invoke が例外で失敗しました。"
            self._logger.exception(msg)
            return self._build_highlights_fallback(completed)
        if isinstance(result, AgentError) or not getattr(result, "bullets", None):
            msg = f"ReviewHighlightsAgent が無効な結果を返したためフォールバックします。 result={result}"
            self._logger.warning(msg)
            return self._build_highlights_fallback(completed)

        intro = result.intro or f"{POSITIVITY_PREFIX} 今週の成果を振り返りましょう。"
        items: list[WeeklyReviewHighlightsItem] = []
        for bullet, digest in zip(result.bullets, completed, strict=False):
            description = bullet.description or digest.task.description or "進捗を記録しました。"
            items.append(
                WeeklyReviewHighlightsItem(
                    title=bullet.title or digest.project_title or digest.task.title,
                    description=description.strip(),
                    source_task_ids=[digest.task.id],
                )
            )

        return WeeklyReviewHighlightsPayload(status="ready", intro=intro, items=items)

    def build_zombie_suggestions(
        self,
        stale_tasks: list[ZombieTaskDigest],
        *,
        zombie_threshold_days: int,
    ) -> WeeklyReviewZombiePayload:
        """ゾンビタスクへのアクション案を生成する。"""
        if not stale_tasks:
            return WeeklyReviewZombiePayload(
                status="ready",
                tasks=[],
                fallback_message="停滞中のタスクはありません。安心して次のステップに進みましょう。",
            )

        state: ZombieTaskState = {
            "tasks": [
                {
                    "title": digest.task.title,
                    "summary": f"{digest.stale_days}日停滞 / {digest.memo_excerpt or digest.task.description}",
                }
                for digest in stale_tasks
            ],
            "tone_hint": f"{zombie_threshold_days}日以上滞留したタスクを整理",
        }
        try:
            result = self._zombie_agent.invoke(state, thread_id=str(uuid4()))
        except Exception:
            msg = "ZombieSuggestionAgent.invoke が例外で失敗しました。"
            self._logger.exception(msg)
            return self._build_zombie_fallback(stale_tasks)
        if isinstance(result, AgentError) or not getattr(result, "tasks", None):
            msg = f"ZombieSuggestionAgent が失敗したためフォールバック案を返します。 result={result}"
            self._logger.warning(msg)
            return self._build_zombie_fallback(stale_tasks)

        insights: list[ZombieTaskInsight] = []
        for output, digest in zip(result.tasks, stale_tasks, strict=False):
            suggestions: list[ZombieTaskSuggestion] = []
            for suggestion in output.suggestions:
                if suggestion.action not in {"split", "defer", "someday", "delete"}:
                    continue
                suggestions.append(
                    ZombieTaskSuggestion(
                        action=suggestion.action,
                        rationale=suggestion.rationale,
                        suggested_subtasks=suggestion.suggested_subtasks,
                    )
                )
            if not suggestions:
                suggestions = self._default_suggestions(digest)
            insights.append(
                ZombieTaskInsight(
                    task_id=digest.task.id,
                    title=digest.task.title,
                    stale_days=digest.stale_days,
                    project_title=digest.project_title,
                    memo_excerpt=digest.memo_excerpt,
                    suggestions=suggestions,
                )
            )

        return WeeklyReviewZombiePayload(status="ready", tasks=insights)

    def build_memo_audits(self, memos: list[MemoAuditDigest]) -> WeeklyReviewMemoAuditPayload:
        """未処理メモの棚卸し提案を生成する。"""
        if not memos:
            return WeeklyReviewMemoAuditPayload(
                status="ready",
                audits=[],
                fallback_message="未処理メモはありません。Inbox がクリアな状態です。",
            )

        state: MemoAuditState = {
            "memos": [
                {
                    "title": digest.memo.title,
                    "content": digest.memo.content,
                    "project": digest.linked_project.title if digest.linked_project else None,
                }
                for digest in memos
            ],
            "tone_hint": "優先順位づけを助けるフレンドリーな問いかけ",
        }
        try:
            result = self._memo_agent.invoke(state, thread_id=str(uuid4()))
        except Exception:
            msg = "MemoAuditSuggestionAgent.invoke が例外で失敗しました。"
            self._logger.exception(msg)
            return self._build_memo_fallback(memos)
        if isinstance(result, AgentError) or not getattr(result, "audits", None):
            msg = f"MemoAuditSuggestionAgent が失敗したためヒューリスティックにフォールバックします。 result={result}"
            self._logger.warning(msg)
            return self._build_memo_fallback(memos)

        audits: list[MemoAuditInsight] = []
        for output, digest in zip(result.audits, memos, strict=False):
            route = output.recommended_route.lower()
            if route not in {"task", "reference", "someday", "discard"}:
                route = "task"
            route_literal = cast("MemoRoute", route)
            audits.append(
                MemoAuditInsight(
                    memo_id=digest.memo.id,
                    summary=output.summary or self._summarize_text(digest.memo.title or digest.memo.content),
                    recommended_route=route_literal,
                    linked_project_id=(digest.linked_project.id if digest.linked_project else None),
                    linked_project_title=(digest.linked_project.title if digest.linked_project else None),
                    guidance=output.guidance,
                )
            )

        return WeeklyReviewMemoAuditPayload(status="ready", audits=audits)

    def _build_highlights_fallback(self, completed: list[CompletedTaskDigest]) -> WeeklyReviewHighlightsPayload:
        message = "今週は完了済みタスクが見つからなかったため、自由入力の振り返りをおすすめします。"
        if not completed:
            return WeeklyReviewHighlightsPayload(
                status="fallback",
                intro=f"{POSITIVITY_PREFIX} 今週は整理に時間を使えました。小さな前進も大切にしましょう。",
                items=[],
                fallback_message=message,
            )

        intro = f"{POSITIVITY_PREFIX} 今週は {len(completed)} 件のタスクが完了し、次の3点が大きな成果でした。"
        items: list[WeeklyReviewHighlightsItem] = []
        for digest in completed[:3]:
            description = (
                digest.task.description
                or digest.memo_excerpt
                or f"{digest.task.title} に取り組み、着実に進捗しました。"
            )
            items.append(
                WeeklyReviewHighlightsItem(
                    title=digest.project_title or digest.task.title,
                    description=description.strip(),
                    source_task_ids=[digest.task.id],
                )
            )
        return WeeklyReviewHighlightsPayload(status="ready", intro=intro, items=items)

    def _build_zombie_fallback(self, stale_tasks: list[ZombieTaskDigest]) -> WeeklyReviewZombiePayload:
        insights: list[ZombieTaskInsight] = []
        for digest in stale_tasks:
            suggestions = self._default_suggestions(digest)
            insights.append(
                ZombieTaskInsight(
                    task_id=digest.task.id,
                    title=digest.task.title,
                    stale_days=digest.stale_days,
                    project_title=digest.project_title,
                    memo_excerpt=digest.memo_excerpt,
                    suggestions=suggestions,
                )
            )
        return WeeklyReviewZombiePayload(status="ready", tasks=insights)

    def _build_memo_fallback(self, memos: list[MemoAuditDigest]) -> WeeklyReviewMemoAuditPayload:
        audits: list[MemoAuditInsight] = []
        for digest in memos:
            route, guidance = self._recommend_route(digest)
            audits.append(
                MemoAuditInsight(
                    memo_id=digest.memo.id,
                    summary=self._summarize_text(digest.memo.title or digest.memo.content),
                    recommended_route=route,
                    linked_project_id=(digest.linked_project.id if digest.linked_project else None),
                    linked_project_title=(digest.linked_project.title if digest.linked_project else None),
                    guidance=guidance,
                )
            )
        return WeeklyReviewMemoAuditPayload(status="ready", audits=audits)

    def _default_suggestions(self, digest: ZombieTaskDigest) -> list[ZombieTaskSuggestion]:
        """ゾンビタスクへの定型提案を生成する。"""
        base_reason = digest.memo_excerpt or digest.task.description or "対応内容を細分化してみましょう。"
        split = ZombieTaskSuggestion(
            action="split",
            rationale=(
                f"大きな塊になっているため、30分以内のサブタスクに分割することをおすすめします ({base_reason[:60]}...)"
            ),
            suggested_subtasks=[f"{digest.task.title} - 最初のステップ"],
        )
        defer = ZombieTaskSuggestion(
            action="defer",
            rationale=f"{digest.stale_days}日以上停滞しているため、締切を再設定して心置きなく優先度を見直しましょう。",
            suggested_subtasks=[],
        )
        someday = ZombieTaskSuggestion(
            action="someday",
            rationale="中長期のテーマであれば Someday/Maybe へ一旦移し、次回レビュー時に再考できます。",
            suggested_subtasks=[],
        )
        delete = ZombieTaskSuggestion(
            action="delete",
            rationale="優先度が低い場合はタスク自体を削除し、メモのみ残すとリストがすっきりします。",
            suggested_subtasks=[],
        )
        return [split, defer, someday, delete]

    def _recommend_route(self, digest: MemoAuditDigest) -> tuple[MemoRoute, str]:
        """メモ内容から次のアクションを判定する。"""
        content = digest.memo.content.lower()
        title = digest.memo.title.lower()
        text = f"{title} {content}"
        rules: Iterable[_MemoRoutingRule] = (
            _MemoRoutingRule("調査", "reference", "資料ボックスへ移し、必要時に参照しますか？"),
            _MemoRoutingRule("someday", "someday", "Someday/Maybe リストに移動して定期的に見直しますか？"),
            _MemoRoutingRule("?", "reference", "メモは疑問形なので、情報として残しますか？"),
        )
        for rule in rules:
            if rule.keyword in text:
                return rule.route, rule.guidance

        if len(digest.memo.content.splitlines()) > MEMO_LINE_THRESHOLD:
            route: MemoRoute = "task"
            return route, "複数行のメモです。次に着手すべきアクションへ変換しましょうか？"

        route = "task"
        return route, "短いメモなので、小さなタスクとして追加するのが良さそうですか？"

    @staticmethod
    def _summarize_text(text: str, limit: int = 80) -> str:
        sanitized = " ".join(text.strip().split())
        return sanitized if len(sanitized) <= limit else f"{sanitized[:limit]}…"
