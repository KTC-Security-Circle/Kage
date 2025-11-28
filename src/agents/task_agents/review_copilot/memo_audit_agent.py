"""未処理メモ棚卸しを生成するサブエージェント。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NotRequired, cast

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field

from agents.agent_conf import LLMProvider
from agents.base import AgentError, BaseAgent, BaseAgentResponse, BaseAgentState, KwargsAny
from agents.utils import agents_logger

if TYPE_CHECKING:  # pragma: no cover
    from langchain_core.runnables import RunnableSerializable


class MemoAuditState(BaseAgentState):
    memos: list[dict[str, str | None]]
    tone_hint: str
    audits: NotRequired[list[MemoAuditOutputItem]]


class MemoAuditOutputItem(BaseModel):
    summary: str = Field(description="メモ内容の短い要約")
    recommended_route: str = Field(description="task/reference/someday/discard いずれか")
    guidance: str = Field(description="ユーザーへ投げかける短い問いかけ")


class MemoAuditAgentOutput(BaseModel):
    audits: list[MemoAuditOutputItem] = Field(default_factory=list)


@dataclass
class MemoAuditAgentResult(BaseAgentResponse[MemoAuditState]):
    audits: list[MemoAuditOutputItem]


_fake_responses = cast(
    "list[BaseModel]",
    [
        MemoAuditAgentOutput(
            audits=[
                MemoAuditOutputItem(
                    summary="アイデアメモ: UI 改善案",
                    recommended_route="task",
                    guidance="次の一歩をタスク化しませんか？",
                )
            ]
        )
    ],
)


class MemoAuditSuggestionAgent(BaseAgent[MemoAuditState, MemoAuditAgentResult]):
    """未処理メモの扱いを提案するエージェント。"""

    _name = "MemoAuditSuggestionAgent"
    _description = "棚卸し対象メモを振り分ける提案を行う"
    _state = MemoAuditState
    _fake_responses = _fake_responses

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        super().__init__(provider, **kwargs)
        self._logger = agents_logger

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("audit", self._suggest_routes)
        graph_builder.add_edge(START, "audit")
        return graph_builder

    def _chain(self) -> RunnableSerializable:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "あなたはメモ整理のアシスタントです。\n"
                        "各メモを読み、task/reference/someday/discard のいずれかの扱いを提案し、"
                        "短い説明を返してください。"
                    ),
                ),
                (
                    "human",
                    "未処理メモ:\n{memo_list}\n\n背景: {tone_hint}",
                ),
            ]
        )
        structured_llm = self.get_model().with_structured_output(MemoAuditAgentOutput)
        return prompt | structured_llm

    def _suggest_routes(self, state: MemoAuditState) -> dict[str, object]:
        chain = self._chain()
        msg = f"MemoAuditAgent state memos={state['memos']} tone={state['tone_hint']}"
        self._logger.debug(msg)
        memo_text = "\n".join(f"- {memo['title']}: {memo.get('content', '')}" for memo in state["memos"])
        response = chain.invoke({"memo_list": memo_text, "tone_hint": state["tone_hint"]})
        msg = f"MemoAuditAgent raw response: {response}"
        self._logger.debug(msg)
        output = self.validate_output(response, MemoAuditAgentOutput)
        if isinstance(output, AgentError):
            msg = f"MemoAuditAgent failed to validate output: {output}"
            self._logger.warning(msg)
            return {"error": output}
        return {"audits": output.audits}

    def _create_return_response(
        self,
        final_response: dict[str, object] | MemoAuditAgentOutput,
    ) -> MemoAuditAgentResult | AgentError:
        if isinstance(final_response, dict):
            err = final_response.get("error")
            if isinstance(err, AgentError):
                return err
            raw_audits = final_response.get("audits", [])
            audits = [MemoAuditOutputItem.model_validate(a) for a in cast("list[object]", raw_audits)]
            return MemoAuditAgentResult(audits=audits, processed_data=self._state)
        if isinstance(final_response, MemoAuditAgentOutput):
            return MemoAuditAgentResult(audits=final_response.audits, processed_data=self._state)
        if isinstance(final_response, AgentError):
            return final_response
        return AgentError("Invalid memo audit response")
