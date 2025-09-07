if __package__ is None:
    import sys
    from pathlib import Path

    # Set the package path to the parent directory of this script
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langchain_core.runnables import RunnableSerializable
from langgraph.graph import START, StateGraph
from pydantic import BaseModel

from agents.base import BaseAgent
from agents.task_agents.splitter.prompt import splitter_agent_prompt
from agents.task_agents.splitter.state import TaskSplitterOutput, TaskSplitterOutputDict, TaskSplitterState
from agents.utils import LLMProvider, agents_logger

_fake_responses: list[BaseModel] = [
    TaskSplitterOutput(
        task_titles=["A", "B"],
        task_descriptions=["A説明", "B説明"],
    ),
    TaskSplitterOutput(
        task_titles=["C", "D"],
        task_descriptions=["C説明", "D説明"],
    ),
]


class TaskSplitterAgent(BaseAgent[TaskSplitterState, TaskSplitterOutput]):
    """タスク分割エージェントの実装."""

    _name = "TaskSplitterAgent"
    _description = "タスクを分割して処理するエージェント"
    _state = TaskSplitterState

    _fake_responses = _fake_responses

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE) -> None:
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
        # llm_with_tools = self._model.bind_tools([TaskSplitterOutput])
        # self._agent = splitter_agent_prompt | llm_with_tools
        structured_llm = self._model.with_structured_output(TaskSplitterOutputDict)
        self._agent = splitter_agent_prompt | structured_llm
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
        agents_logger.debug(f"Raw response: {response}")
        try:
            output_obj = TaskSplitterOutput.model_validate(response)
            agents_logger.debug(f"Output object: {output_obj}")
        except Exception as e:
            agents_logger.error(f"Error validating output: {e}")
            output_obj = TaskSplitterOutput(task_titles=[], task_descriptions=[])
        return {"final_response": output_obj}


if __name__ == "__main__":
    from uuid import uuid4

    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = TaskSplitterAgent(LLMProvider.HUGGINGFACE)

    thread_id = str(uuid4())
    # thread_id = "649869e4-0782-4683-98d6-9dd3fda02133"  # Example thread ID for testing
    agents_logger.debug(f"Starting TaskSplitterAgent with thread ID: {thread_id}")

    task_name = "課題をやる"
    task_description = "国語、数学、英語の宿題をやる。"

    state = TaskSplitterState(
        task_title=task_name,
        task_description=task_description,
        final_response="",
    )
    response = agent.invoke(state, thread_id)
    if response:
        agents_logger.debug("Assistant: " + response.model_dump_json())
    else:
        agents_logger.debug("No response from the agent.")

    # stream mode test
    # for msg, metadata in agent.stream(state, thread_id):
    #     if isinstance(msg, TaskSplitterOutput):
    #         agents_logger.debug(f"Assistant: {msg.model_dump_json()}")
    #     else:
    #         agents_logger.debug("No content in the message. Metadata: " + str(metadata))
