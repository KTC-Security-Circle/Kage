"""週次レビューStep2向けのタスクアクションエージェント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, NotRequired, cast
from uuid import UUID, uuid4

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field

from agents.agent_conf import LLMProvider
from agents.base import AgentError, BaseAgent, BaseAgentResponse, BaseAgentState, KwargsAny
from models import (
    WeeklyReviewSplitPlan,
    WeeklyReviewSplitSubtask,
    WeeklyReviewSplitTarget,
)

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableSerializable


class WeeklyReviewTaskAgentState(BaseAgentState):
    """エージェントに渡すステート構造。"""

    targets: list[dict[str, object]]
    tone_hint: str
    detail_hint: NotRequired[str]
    custom_instructions: NotRequired[str]
    plans: NotRequired[list[WeeklyReviewSplitPlan]]


class WeeklyReviewTaskAgentOutput(BaseModel):
    """LLM の構造化出力。"""

    plans: list[WeeklyReviewSplitPlan] = Field(default_factory=list)


@dataclass
class WeeklyReviewTaskAgentResult(BaseAgentResponse[WeeklyReviewTaskAgentState]):
    """エージェントの戻り値。"""

    plans: list[WeeklyReviewSplitPlan]


_fake_output = WeeklyReviewTaskAgentOutput(
    plans=[
        WeeklyReviewSplitPlan(
            parent_task_id=UUID(int=0),
            rationale="粒度が大きいため3ステップに分割",
            subtasks=[
                WeeklyReviewSplitSubtask(
                    title="情報整理",
                    description="必要資料を収集",
                    first_step_hint="完了済みメモを洗い出す",
                    estimate_minutes=15,
                )
            ],
        )
    ]
)


class WeeklyReviewTaskAgent(BaseAgent[WeeklyReviewTaskAgentState, WeeklyReviewTaskAgentResult]):
    """ゾンビタスクの細分化案を生成する軽量エージェント。"""

    _name = "WeeklyReviewTaskAgent"
    _description = "停滞タスクの細分化案を生成する"
    _state = WeeklyReviewTaskAgentState
    _fake_responses: ClassVar[list[WeeklyReviewTaskAgentOutput]] = [_fake_output]

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.FAKE,
        *,
        model_name: str | None = None,
        device: str | None = None,
        **kwargs: KwargsAny,
    ) -> None:
        super().__init__(provider, model_name=model_name, device=device, **kwargs)

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("suggest", self._build_plan)
        graph_builder.add_edge(START, "suggest")
        return graph_builder

    def _chain(self) -> RunnableSerializable:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "あなたはGTDコーチです。各タスクを2〜5個の実行可能なサブタスクへ分割します。\n"
                        "課題の背景や停滞理由を考慮し、各サブタスクの最初の一歩を示してください。\n"
                        "応答は JSON のみで、各要素は parent_task_id を含む必要があります。\n"
                        "出力粒度ヒント: {detail_hint}\n"
                        "追加指示: {custom_instructions}\n"
                    ),
                ),
                (
                    "human",
                    "対象タスク:\n{tasks}\n背景: {tone_hint}",
                ),
            ]
        )
        structured_llm = self.get_model().with_structured_output(WeeklyReviewTaskAgentOutput)
        return prompt | structured_llm

    def _build_plan(self, state: WeeklyReviewTaskAgentState) -> dict[str, object]:
        overrides = self._prompt_overrides(state)
        tasks_text = self._format_tasks(state["targets"])
        chain = self._chain()
        response = chain.invoke({"tasks": tasks_text, **overrides})
        output = self.validate_output(response, WeeklyReviewTaskAgentOutput)
        if isinstance(output, AgentError):
            return {"error": output}
        return {"plans": output.plans}

    def _format_tasks(self, targets: list[dict[str, object]]) -> str:
        lines: list[str] = []
        for item in targets:
            pieces = [f"- {item['title']} ({item['stale_days']}日停滞)"]
            context = str(item.get("context") or "").strip()
            if context:
                pieces.append(f"理由: {context}")
            lines.append(" ".join(pieces))
        return "\n".join(lines)

    def _prompt_overrides(self, state: WeeklyReviewTaskAgentState) -> dict[str, str]:
        detail_hint = str(state.get("detail_hint", "") or "").strip()
        custom_text = str(state.get("custom_instructions", "") or "").strip()
        return {
            "detail_hint": detail_hint or "各サブタスクは30分以内で完了できる粒度で記述してください。",
            "custom_instructions": custom_text or "ユーザーの負担を減らす観点で提案してください。",
            "tone_hint": state.get("tone_hint", "停滞タスクを再始動します"),
        }

    def _create_return_response(
        self,
        final_response: dict[str, object] | WeeklyReviewTaskAgentOutput,
    ) -> WeeklyReviewTaskAgentResult | AgentError:
        if isinstance(final_response, dict):
            err = final_response.get("error")
            if isinstance(err, AgentError):
                return err
            plans_data = cast("list[object]", final_response.get("plans", []))
            plans = [WeeklyReviewSplitPlan.model_validate(plan) for plan in plans_data]
            return WeeklyReviewTaskAgentResult(plans=plans, processed_data=self._state)
        if isinstance(final_response, WeeklyReviewTaskAgentOutput):
            return WeeklyReviewTaskAgentResult(plans=final_response.plans, processed_data=self._state)
        if isinstance(final_response, AgentError):
            return final_response
        return AgentError("Invalid weekly review task agent response")

    def plan_subtasks(self, targets: list[WeeklyReviewSplitTarget]) -> list[WeeklyReviewSplitPlan]:
        """タスク群を細分化し、サブタスク案を返す。"""
        if not targets:
            return []
        if self.provider == LLMProvider.FAKE:
            return self._build_fake_plans(targets)
        state: WeeklyReviewTaskAgentState = {
            "targets": [
                {
                    "task_id": str(target.task_id),
                    "title": target.title,
                    "stale_days": target.stale_days,
                    "context": target.context,
                }
                for target in targets
            ],
            "tone_hint": f"{len(targets)}件の停滞タスクを再起動",
        }
        result = self.invoke(state, thread_id=str(uuid4()))
        if isinstance(result, AgentError):
            raise result
        return result.plans

    def _build_fake_plans(self, targets: list[WeeklyReviewSplitTarget]) -> list[WeeklyReviewSplitPlan]:
        """FAKE プロバイダ用の決定的な細分化案を返す。"""
        plans: list[WeeklyReviewSplitPlan] = []
        for target in targets:
            rationale = f"{target.title} を再起動するためのサブタスク案"
            subtasks = [
                WeeklyReviewSplitSubtask(
                    title=f"{target.title}の状況整理",
                    description=target.context or "停滞理由を棚卸しして阻害要因を洗い出します。",
                    first_step_hint="過去のメモと進捗ログを5分で見直す",
                    estimate_minutes=20,
                ),
                WeeklyReviewSplitSubtask(
                    title="次のアクションを確定",
                    description="責任者・期日・依存関係を整理します。",
                    first_step_hint="必要な関係者をチャットで ping する",
                    estimate_minutes=30,
                ),
            ]
            plans.append(
                WeeklyReviewSplitPlan(
                    parent_task_id=target.task_id,
                    rationale=rationale,
                    subtasks=subtasks,
                )
            )
        return plans
