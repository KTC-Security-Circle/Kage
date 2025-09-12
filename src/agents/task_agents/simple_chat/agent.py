from __future__ import annotations

from typing import TYPE_CHECKING

if __package__ is None:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langgraph.graph import START, StateGraph

from agents.agent_conf import LLMProvider
from agents.base import BaseAgent, KwargsAny
from agents.task_agents.simple_chat.prompt import simple_chat_prompt
from agents.task_agents.simple_chat.state import SimpleChatOutput, SimpleChatState
from agents.utils import agents_logger

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableSerializable
    from pydantic import BaseModel

    from agents.base import ErrorAgentOutput

_fake_responses: list[BaseModel] = [
    SimpleChatOutput(response="こんにちは！私はあなたのアシスタントです。"),
    SimpleChatOutput(response="ご質問ありがとうございます。お手伝いできることがあれば教えてください。"),
]


class SimpleChatAgent(BaseAgent[SimpleChatState, SimpleChatOutput]):
    """シンプルな1ターン/メモリ付きチャットエージェント.

    現状は1ノード構成で user_message を受け取り reply を返す。
    system_prompt が state で指定されない場合はデフォルトを適用。
    """

    _name = "SimpleChatAgent"
    _description = "ユーザーメッセージに素早く応答するシンプルチャットエージェント"
    _state = SimpleChatState

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
        structured_llm = self._model.with_structured_output(SimpleChatOutput)
        return simple_chat_prompt | structured_llm

    def chatbot(self, state: SimpleChatState) -> dict[str, SimpleChatOutput | ErrorAgentOutput]:
        """チャットボットノードの処理."""
        self._agent = self._create_agent()
        response = self._agent.invoke({"user_message": state["user_message"]})
        output = self.validate_output(response, SimpleChatOutput)
        return {"final_response": output}


if __name__ == "__main__":  # 単体テスト用簡易実行
    from uuid import uuid4

    from agents.agent_conf import HuggingFaceModel
    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = SimpleChatAgent(
        LLMProvider.OPENVINO, model_name=HuggingFaceModel.QWEN_3_8B_INT4, verbose=True, error_response=False
    )
    thread_id = str(uuid4())

    state: SimpleChatState = {
        "user_message": "こんにちは！自己紹介して。",
        "system_prompt": None,
        "final_response": "",
    }
    result = agent.invoke(state, thread_id)
    if result:
        agents_logger.debug("Assistant: " + result.model_dump_json())
