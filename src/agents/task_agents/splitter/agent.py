if __package__ is None:
    import sys
    from pathlib import Path

    # Set the package path to the parent directory of this script
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langchain_core.runnables import RunnableSerializable
from langgraph.graph import START, StateGraph

from agents.base import BaseAgent
from agents.task_agents.splitter.prompt import splitter_agent_prompt
from agents.task_agents.splitter.state import TaskSplitterOutput, TaskSplitterState
from agents.utils import LLMProvider
from logging_conf import agent_logger as logger


class TaskSplitterAgent(BaseAgent[TaskSplitterState, TaskSplitterOutput]):
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

    def _create_agent(self) -> RunnableSerializable:
        """エージェントのインスタンスを作成."""
        self._model = self.get_model()
        llm_with_tools = self._model.bind_tools([TaskSplitterOutput])
        self._agent = splitter_agent_prompt | llm_with_tools
        return self._agent

    def chatbot(self, state: TaskSplitterState) -> dict[str, TaskSplitterOutput]:
        """チャットボットノードの処理."""
        self._agent = self._create_agent()
        response = self._agent.invoke(
            {
                "task_name": state["task_title"],
                "task_description": state["task_description"],
            },
        )
        try:
            output_obj = TaskSplitterOutput.model_validate(response.tool_calls[0]["args"])
            logger.debug(f"Output object: {output_obj}")
        except Exception as e:
            logger.error(f"Error validating output: {e}")
            output_obj = TaskSplitterOutput(task_titles=[], task_descriptions=[])
        return {"final_response": output_obj}


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

    task_name = "課題をやる"
    task_description = "国語、数学、英語の宿題をやる。"

    state = TaskSplitterState(
        task_title=task_name,
        task_description=task_description,
        final_response="",
    )
    response = agent.invoke(state, thread_id)
    if response:
        logger.debug("Assistant: " + response.model_dump_json())
    else:
        logger.debug("No response from the agent.")

    # stream mode test
    # for msg, metadata in agent.stream(state, thread_id):
    #     if isinstance(msg, TaskSplitterOutput):
    #         logger.debug(f"Assistant: {msg.model_dump_json()}")
    #     else:
    #         logger.debug("No content in the message. Metadata: " + str(metadata))
