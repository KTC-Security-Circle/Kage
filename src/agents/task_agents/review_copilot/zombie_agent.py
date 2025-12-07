"""ゾンビタスク向け提案を生成するサブエージェント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NotRequired, cast

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field

from agents.agent_conf import LLMProvider
from agents.base import AgentError, BaseAgent, BaseAgentResponse, BaseAgentState, KwargsAny
from agents.utils import agents_logger

if TYPE_CHECKING:  # pragma: no cover
    from langchain_core.runnables import RunnableSerializable

ZombieActionType = Literal["split", "defer", "someday", "delete"]


class ZombieTaskState(BaseAgentState):
    tasks: list[dict[str, object]]
    tone_hint: str
    detail_hint: NotRequired[str]
    custom_instructions: NotRequired[str]


class ZombieAction(BaseModel):
    action: ZombieActionType = Field(description="推奨するアクション")
    rationale: str = Field(description="そのアクションを提案する理由")
    suggested_subtasks: list[str] = Field(default_factory=list, description="分割案など")


class ZombieTaskOutput(BaseModel):
    title: str
    summary: str
    suggestions: list[ZombieAction] = Field(default_factory=list)


class ZombieAgentOutput(BaseModel):
    tasks: list[ZombieTaskOutput] = Field(default_factory=list)


@dataclass
class ZombieAgentResult(BaseAgentResponse[ZombieTaskState]):
    tasks: list[ZombieTaskOutput]


_fake_responses = cast(
    "list[BaseModel]",
    [
        ZombieAgentOutput(
            tasks=[
                ZombieTaskOutput(
                    title="資料作成",
                    summary="2週間以上停滞している企画資料",
                    suggestions=[
                        ZombieAction(
                            action="split",
                            rationale="段取りが大きいため分割しましょう",
                            suggested_subtasks=["アウトライン決定"],
                        ),
                        ZombieAction(action="defer", rationale="締切を再設定して安心して進めましょう"),
                        ZombieAction(action="someday", rationale="優先度が低ければSomedayに移動"),
                    ],
                )
            ]
        )
    ],
)


class ZombieSuggestionAgent(BaseAgent[ZombieTaskState, ZombieAgentResult]):
    """停滞タスクに対する処置案を提示するエージェント。"""

    _name = "ZombieSuggestionAgent"
    _description = "長期間停滞したタスクのケアプランを提案する"
    _state = ZombieTaskState
    _fake_responses = _fake_responses

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        super().__init__(provider, **kwargs)
        self._logger = agents_logger

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("suggest", self._suggest_actions)
        graph_builder.add_edge(START, "suggest")
        return graph_builder

    def _chain(self) -> RunnableSerializable:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "あなたは生産性コーチです。\n"
                        "各タスクが停滞している理由を推測し、最大3件の処置案を返してください。\n"
                        "処置案は split/defer/someday/delete のいずれかを使用し、理由とサブタスク案を含めます。\n"
                        "出力粒度ヒント: {detail_hint}\n"
                        "追加指示:\n"
                        "{custom_instructions}\n"
                    ),
                ),
                (
                    "human",
                    "停滞タスク一覧:\n{tasks}\n\n背景: {tone_hint}",
                ),
            ]
        )
        structured_llm = self.get_model().with_structured_output(ZombieAgentOutput)
        return prompt | structured_llm

    def _suggest_actions(self, state: ZombieTaskState) -> dict[str, object]:
        chain = self._chain()
        debug_msg = f"Suggesting actions for tasks: {state['tasks']} with tone hint: {state['tone_hint']}"
        self._logger.debug(debug_msg)
        task_text = "\n".join(f"- {task['title']}: {task['summary']}" for task in state["tasks"])
        overrides = self._prompt_overrides(state)
        response = chain.invoke({"tasks": task_text, "tone_hint": state["tone_hint"], **overrides})
        debug_msg = f"ZombieAgent raw response: {response}"
        self._logger.debug(debug_msg)
        output = self.validate_output(response, ZombieAgentOutput)
        if isinstance(output, AgentError):
            debug_msg = f"ZombieAgent validation error: {output}"
            self._logger.warning(debug_msg)
            return {"error": output}
        return {"tasks": output.tasks}

    def _create_return_response(
        self,
        final_response: dict[str, object] | ZombieAgentOutput,
    ) -> ZombieAgentResult | AgentError:
        if isinstance(final_response, dict):
            err = final_response.get("error")
            if isinstance(err, AgentError):
                return err
            tasks_data = final_response.get("tasks", [])
            tasks = [ZombieTaskOutput.model_validate(task) for task in cast("list[object]", tasks_data)]
            return ZombieAgentResult(tasks=tasks, processed_data=self._state)
        if isinstance(final_response, ZombieAgentOutput):
            return ZombieAgentResult(tasks=final_response.tasks, processed_data=self._state)
        if isinstance(final_response, AgentError):
            return final_response
        return AgentError("Invalid zombie suggestion response")

    def _prompt_overrides(self, state: ZombieTaskState) -> dict[str, str]:
        detail_hint = str(state.get("detail_hint", "") or "").strip()
        custom_text = str(state.get("custom_instructions", "") or "").strip()
        return {
            "detail_hint": detail_hint or "停滞の理由と対処を簡潔に提示してください。",
            "custom_instructions": custom_text or "追加指示はありません。",
        }
