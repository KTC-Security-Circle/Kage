from __future__ import annotations

from typing import TYPE_CHECKING

if __package__ is None:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langgraph.graph import START, StateGraph

from agents.agent_conf import LLMProvider
from agents.base import BaseAgent
from agents.task_agents.simple_chat.prompt import SIMPLE_CHAT_SYSTEM_PROMPT, simple_chat_prompt
from agents.task_agents.simple_chat.state import SimpleChatOutput, SimpleChatState
from agents.utils import agents_logger

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableSerializable


class SimpleChatAgent(BaseAgent[SimpleChatState, SimpleChatOutput]):
    """シンプルな1ターン/メモリ付きチャットエージェント.

    現状は1ノード構成で user_message を受け取り reply を返す。
    system_prompt が state で指定されない場合はデフォルトを適用。
    """

    _name = "SimpleChatAgent"
    _description = "ユーザーメッセージに素早く応答するシンプルチャットエージェント"
    _state = SimpleChatState

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE) -> None:
        super().__init__(provider)

    # グラフ構築
    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "chatbot")
        return graph_builder

    def _create_agent(self) -> RunnableSerializable:
        # モデル取得 & シンプルチェーン作成
        self._model = self.get_model()
        # bind_tools を現状使わず素の出力をそのまま reply に格納
        self._agent = simple_chat_prompt | self._model
        return self._agent

    def chatbot(self, state: SimpleChatState) -> dict[str, SimpleChatOutput]:
        self._agent = self._create_agent()
        system_prompt = state.get("system_prompt") or SIMPLE_CHAT_SYSTEM_PROMPT
        user_message = state["user_message"]
        agents_logger.debug(f"SimpleChatAgent input: {user_message}")
        response = self._agent.invoke({"system_prompt": system_prompt, "user_message": user_message})
        # response は AIMessage か str を想定
        content = response.content if hasattr(response, "content") else str(response)
        output = SimpleChatOutput(reply=content)
        return {"final_response": output}


if __name__ == "__main__":  # 単体テスト用簡易実行
    from uuid import uuid4

    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = SimpleChatAgent(LLMProvider.HUGGINGFACE)
    thread_id = str(uuid4())

    state: SimpleChatState = {
        "user_message": "こんにちは！自己紹介して。",
        "system_prompt": None,
        "final_response": "",
    }
    result = agent.invoke(state, thread_id)
    if result:
        agents_logger.debug("Assistant: " + result.model_dump_json())
