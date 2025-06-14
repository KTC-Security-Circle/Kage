if __package__ is None:
    import sys
    from pathlib import Path

    # Set the package path to the parent directory of this script
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langchain_core.messages import BaseMessage
from langgraph.graph import START, StateGraph

from agents.base import BaseAgent
from agents.task_agents.splitter.state import TaskSplitterState
from agents.utils import LLMProvider, get_model
from logging_conf import agent_logger as logger


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


if __name__ == "__main__":
    from uuid import uuid4

    from env import setup_environment
    from logging_conf import setup_logger

    setup_environment()
    setup_logger()

    agent = TaskSplitterAgent()

    thread_id = str(uuid4())
    # thread_id = "649869e4-0782-4683-98d6-9dd3fda02133"  # Example thread ID for testing
    logger.debug(f"Starting TaskSplitterAgent with thread ID: {thread_id}")

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                logger.debug("Goodbye!")
                break
            response = agent.invoke(user_input, thread_id)
            if response:
                logger.debug("Assistant: " + response)
            else:
                logger.debug("No response from the agent.")

            # stream mode test
            # for msg, metadata in agent.stream(user_input, thread_id):
            #     if isinstance(msg, BaseMessage) and msg.content:
            #         print(msg.content, end="", flush=True)
            #     else:
            #         logger.debug("No content in the message. Metadata: " + str(metadata))
            # logger.debug(f"\nAssistant: Stream completed. {metadata=}")
        except Exception as e:
            # fallback if input() is not available
            logger.error(f"An error occurred: {e}")
            user_input = "What do you know about LangGraph?"
            logger.debug("User: " + user_input)
            response = agent.invoke(user_input, thread_id)
            if response:
                logger.debug("Assistant: " + response)
            else:
                logger.debug("No response from the agent.")
            break
