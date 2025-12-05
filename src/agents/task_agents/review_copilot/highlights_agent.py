"""成果サマリー生成を担当するサブエージェント。"""

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


class HighlightsState(BaseAgentState):
    """完了タスクの簡易サマリーを受け取る状態。"""

    completed_task_summaries: list[str]
    tone_hint: str
    intro: NotRequired[str]
    detail_hint: NotRequired[str]
    custom_instructions: NotRequired[str]


class HighlightBullet(BaseModel):
    title: str = Field(description="ハイライトの見出し")
    description: str = Field(description="ユーザーに伝える詳細")


class HighlightsAgentOutput(BaseModel):
    intro: str = Field(description="肯定的な導入文")
    bullets: list[HighlightBullet] = Field(default_factory=list, description="箇条書き3件")


@dataclass
class HighlightsAgentResult(BaseAgentResponse[HighlightsState]):
    intro: str
    bullets: list[HighlightBullet]


_fake_responses = cast(
    "list[BaseModel]",
    [
        HighlightsAgentOutput(
            intro="お疲れさまです！主要な取り組みが確実に前進しました。",
            bullets=[
                HighlightBullet(title="タスク整理", description="完了タスクの棚卸しで進捗が可視化されました"),
                HighlightBullet(title="プロジェクト前進", description="主要プロジェクトのボトルネックを解消しました"),
                HighlightBullet(title="学習と改善", description="振り返りから次の一手が明確になりました"),
            ],
        )
    ],
)


class ReviewHighlightsAgent(BaseAgent[HighlightsState, HighlightsAgentResult]):
    """成果ハイライトをLLMで整形するエージェント。"""

    _name = "ReviewHighlightsAgent"
    _description = "週次レビュー向けに3件の成果サマリーを組み立てる"
    _state = HighlightsState
    _fake_responses = _fake_responses

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        super().__init__(provider, **kwargs)
        self._logger = agents_logger

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("summarize", self._generate_highlights)
        graph_builder.add_edge(START, "summarize")
        return graph_builder

    def _create_chain(self) -> RunnableSerializable:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """あなたはポジティブなエグゼクティブアシスタントです。
完了タスクのブリーフを読み取り、励ますトーンの導入文と3件の箇条書きを生成してください。
各箇条書きは30文字以内のタイトルと、質的な成果を表す説明文を含めます。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
                ),
                (
                    "human",
                    "完了タスク一覧:\n{task_summaries}\n\n求めるトーン: {tone_hint}\n",
                ),
            ]
        )
        structured_llm = self.get_model().with_structured_output(HighlightsAgentOutput)
        return prompt | structured_llm

    def _generate_highlights(self, state: HighlightsState) -> dict[str, object]:
        chain = self._create_chain()
        self._logger.debug(
            "HighlightsAgent state summaries=%s tone=%s", state["completed_task_summaries"], state["tone_hint"]
        )
        summary_text = "\n".join(f"- {line}" for line in state["completed_task_summaries"])
        overrides = self._prompt_overrides(state)
        response = chain.invoke(
            {
                "task_summaries": summary_text,
                "tone_hint": state["tone_hint"],
                **overrides,
            }
        )
        self._logger.debug("HighlightsAgent raw response: %s", response)
        output = self.validate_output(response, HighlightsAgentOutput)
        if isinstance(output, AgentError):
            self._logger.warning("HighlightsAgent validation error: %s", output)
            return {"error": output}
        return {"intro": output.intro, "bullets": output.bullets}

    def _create_return_response(
        self,
        final_response: dict[str, object] | HighlightsAgentOutput,
    ) -> HighlightsAgentResult | AgentError:
        if isinstance(final_response, dict):
            err = final_response.get("error")
            if isinstance(err, AgentError):
                return err
            intro = str(final_response.get("intro", ""))
            bullet_objs = final_response.get("bullets")
            if isinstance(bullet_objs, list):
                bullets = [HighlightBullet.model_validate(bullet) for bullet in bullet_objs]
            else:
                bullets = []
            return HighlightsAgentResult(intro=intro, bullets=bullets, processed_data=self._state)
        if isinstance(final_response, HighlightsAgentOutput):
            return HighlightsAgentResult(
                intro=final_response.intro,
                bullets=final_response.bullets,
                processed_data=self._state,
            )
        if isinstance(final_response, AgentError):
            return final_response
        return AgentError("Invalid highlights response")

    def _prompt_overrides(self, state: HighlightsState) -> dict[str, str]:
        detail_hint = str(state.get("detail_hint", "") or "").strip()
        custom_text = str(state.get("custom_instructions", "") or "").strip()
        return {
            "detail_hint": detail_hint or "バランスよくポジティブにまとめてください。",
            "custom_instructions": custom_text or "追加指示はありません。",
        }
