if __package__ is None:
    import sys
    from pathlib import Path

    # Set the package path to the parent directory of this script
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langchain_core.messages import BaseMessage
from langgraph.graph import START, StateGraph
from loguru import logger

from agents.base import BaseAgent
from agents.task_agents.splitter.state import TaskSplitterState
from agents.utils import LLMProvider, get_model


class TaskSplitterAgent(BaseAgent):
    """タスク分割エージェントの実装."""

    name = "TaskSplitterAgent"
    description = "タスクを分割して処理するエージェント"
    _state = TaskSplitterState

    def __init__(self, provider: LLMProvider = LLMProvider.GOOGLE) -> None:
        """初期化."""
        super().__init__(provider)

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        """グラフを作成."""
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "chatbot")
        return graph_builder

    def chatbot(self, state: TaskSplitterState) -> dict[str, list[BaseMessage]]:
        """チャットボットノードの処理."""
        self._model = get_model(LLMProvider.GOOGLE, "gemini-2.0-flash")
        response = self._model.invoke(state["messages"])
        return {"messages": [response]}


# graph_builder = StateGraph(TaskSplitterState)


# def chatbot(state: TaskSplitterState) -> dict[str, list[BaseMessage]]:
#     model = get_model(LLMProvider.GOOGLE, "gemini-2.0-flash")
#     return {"messages": [model.invoke(state["messages"])]}


# graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_edge(START, "chatbot")
# graph = graph_builder.compile()


# def stream_graph_updates(user_input: str) -> None:
#     for event in graph.stream(
#         {"messages": [{"role": "user", "content": user_input}]},
#     ):
#         for value in event.values():
#             logger.debug("Assistant:" + value["messages"][-1].content)


if __name__ == "__main__":
    from env import setup_environment

    setup_environment()

    agent = TaskSplitterAgent()

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                logger.debug("Goodbye!")
                break
            response = agent.invoke(user_input)
            if response:
                logger.debug("Assistant: " + response)
            else:
                logger.debug("No response from the agent.")
        except Exception as _:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            logger.debug("User: " + user_input)
            response = agent.invoke(user_input)
            if response:
                logger.debug("Assistant: " + response)
            else:
                logger.debug("No response from the agent.")
            break
