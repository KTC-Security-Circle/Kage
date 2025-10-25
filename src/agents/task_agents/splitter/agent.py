if __package__ is None:  # pragma: no cover
    import sys
    from pathlib import Path

    # Set the package path to the parent directory of this script
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from langchain_core.runnables import RunnableSerializable
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agents.base import BaseAgent, ErrorAgentOutput, KwargsAny
from agents.task_agents.splitter.prompt import splitter_agent_prompt
from agents.task_agents.splitter.state import TaskSplitterOutput, TaskSplitterState
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

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        """初期化."""
        super().__init__(provider, **kwargs)

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        """LangGraphのノードとエッジを構築する."""
        graph_builder.add_node("generate_candidates", self._generate_candidates)
        graph_builder.add_node("refine_candidates", self._refine_candidates)
        graph_builder.add_node("finalize_response", self._finalize_response)

        graph_builder.add_edge(START, "generate_candidates")
        graph_builder.add_conditional_edges(
            "generate_candidates",
            self._route_after_generate,
            ["refine_candidates", "finalize_response"],
        )
        graph_builder.add_edge("refine_candidates", "finalize_response")
        graph_builder.add_edge("finalize_response", END)

        return graph_builder

    def _create_agent(self) -> RunnableSerializable:
        """TaskSplitter用のLLMパイプラインを生成する."""
        self._model = self.get_model()
        structured_llm = self._model.with_structured_output(TaskSplitterOutput)
        self._agent = splitter_agent_prompt | structured_llm
        return self._agent

    def _generate_candidates(self, state: TaskSplitterState) -> dict[str, object]:
        """タスク分割候補を生成するノード."""
        agent = self._create_agent()
        response = agent.invoke(
            {
                "task_name": state["task_title"],
                "task_description": state["task_description"],
            }
        )
        output = self.validate_output(response, TaskSplitterOutput)
        if isinstance(output, TaskSplitterOutput):
            return {"candidate_output": output}
        return {"error_output": output}

    def _route_after_generate(self, state: TaskSplitterState) -> str:
        """分岐先を決定する条件付きエッジ用コールバック."""
        if "error_output" in state:
            return "finalize_response"

        candidate = state.get("candidate_output")
        if not isinstance(candidate, TaskSplitterOutput) or not candidate.task_titles:
            return "finalize_response"
        return "refine_candidates"

    def _refine_candidates(self, state: TaskSplitterState) -> dict[str, object]:
        """分割候補に追加情報を付与するノード."""
        candidate = state.get("candidate_output")
        if not isinstance(candidate, TaskSplitterOutput):
            return {}

        refined_titles = [title.strip() or f"Step {index + 1}" for index, title in enumerate(candidate.task_titles)]
        base_context = state.get("task_description", "")

        refined_descriptions: list[str] = []
        for index, title in enumerate(refined_titles):
            description = ""
            if index < len(candidate.task_descriptions):
                description = candidate.task_descriptions[index].strip()
            if not description:
                description = f"{title} を行うための準備: {base_context}".strip()
            refined_descriptions.append(description)

        refined_output = TaskSplitterOutput(task_titles=refined_titles, task_descriptions=refined_descriptions)
        return {"refined_output": refined_output}

    def _finalize_response(self, state: TaskSplitterState) -> dict[str, TaskSplitterOutput | ErrorAgentOutput]:
        """最終的な応答を決定する終端ノード."""
        error_output = state.get("error_output")
        if isinstance(error_output, ErrorAgentOutput):
            return {"final_response": error_output}

        final_output = state.get("refined_output")
        if not isinstance(final_output, TaskSplitterOutput):
            candidate_output = state.get("candidate_output")
            if isinstance(candidate_output, TaskSplitterOutput):
                final_output = candidate_output
            else:
                final_output = TaskSplitterOutput(task_titles=[], task_descriptions=[])

        return {"final_response": final_output}


if __name__ == "__main__":  # pragma: no cover
    from uuid import uuid4

    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = TaskSplitterAgent(LLMProvider.FAKE, verbose=True)

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
