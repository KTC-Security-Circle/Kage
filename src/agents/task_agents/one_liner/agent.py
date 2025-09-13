from __future__ import annotations

from typing import TYPE_CHECKING

if __package__ is None:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langgraph.graph import START, StateGraph

from agents.agent_conf import LLMProvider
from agents.base import BaseAgent, KwargsAny
from agents.task_agents.one_liner.prompt import one_liner_prompt
from agents.task_agents.one_liner.state import OneLinerOutput, OneLinerState
from agents.utils import agents_logger

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableSerializable
    from pydantic import BaseModel

    from agents.base import ErrorAgentOutput

_fake_responses: list[BaseModel] = [
    OneLinerOutput(response="こんにちは！私は Kage AI です。"),
    OneLinerOutput(response="今日も一日頑張りましょう！"),
]


class OneLinerAgent(BaseAgent[OneLinerState, OneLinerOutput]):
    """シンプルな1ターン/メモリ付きチャットエージェント.

    現状は1ノード構成でタスク統計 (today / completed / overdue 等) を受け取り
    ホーム画面向けの短い励ましメッセージを返す。
    """

    _name = "OneLinerAgent"
    _description = "ユーザーメッセージに素早く応答するワンライナーエージェント"
    _state = OneLinerState

    _fake_responses = _fake_responses

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        super().__init__(provider, **kwargs)

    # グラフ構築
    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "chatbot")
        return graph_builder

    def _create_agent(self) -> RunnableSerializable:
        # モデル取得 & シンプルチェーン作成
        self._model = self.get_model()
        structured_llm = self._model.with_structured_output(OneLinerOutput)
        return one_liner_prompt | structured_llm

    def chatbot(self, state: OneLinerState) -> dict[str, OneLinerOutput | ErrorAgentOutput]:
        """チャットボットノードの処理."""
        self._agent = self._create_agent()
        response = self._agent.invoke(
            {
                "today_task_count": state["today_task_count"],
                "completed_task_count": state["completed_task_count"],
                "overdue_task_count": state["overdue_task_count"],
                "progress_summary": state["progress_summary"],
                "user_name": state["user_name"],
            }
        )
        output = self.validate_output(response, OneLinerOutput)
        return {"final_response": output}


if __name__ == "__main__":  # 単体テスト用簡易実行 # pragma: no cover
    from uuid import uuid4

    from agents.agent_conf import HuggingFaceModel
    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = OneLinerAgent(
        LLMProvider.OPENVINO, model_name=HuggingFaceModel.QWEN_3_8B_INT4, verbose=True, error_response=False
    )
    thread_id = str(uuid4())

    state: OneLinerState = {
        "today_task_count": 5,
        "completed_task_count": 2,
        "overdue_task_count": 0,
        "progress_summary": "午前中に主要タスクを進行",
        "user_name": "ユーザー",
        "final_response": "",
    }
    result = agent.invoke(state, thread_id)
    if result:
        agents_logger.debug("Assistant: " + result.model_dump_json())
