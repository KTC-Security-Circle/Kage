from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from agents.agent_conf import LLMProvider
from agents.utils import agents_logger, get_memory, get_model

if TYPE_CHECKING:
    from collections.abc import Iterator

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.runnables.config import RunnableConfig
    from langgraph.graph.state import CompiledStateGraph
    from pydantic import BaseModel


class AgentStatus(Enum):
    """エージェントの実行状態."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class AgentProperty:
    """エージェントのプロパティ."""

    name: str
    description: str
    status: AgentStatus
    thread_id: str | None = None


class BaseAgentState(TypedDict):
    """エージェントの状態を表す基本的な型定義."""

    final_response: dict[str, Any] | str
    """最終的な応答を表す文字列."""


# 型変数を定義
# StateType = TypeVar("StateType")
# ReturnType = TypeVar("ReturnType")


class BaseAgent[StateType, ReturnType](ABC):
    """LangGraphエージェントのベースクラス.

    このクラスを継承して具体的なエージェントを実装します。

    Attributes:
        -- 必須項目 --
        _name (str): エージェントの名前
        _description (str): エージェントの説明
        _state (type[Any]): エージェントの状態の型
        -- オプション項目 --
        _status (AgentStatus): エージェントの実行状態 (デフォルトはIDLE)
        _model (BaseChatModel | None): 使用するLLMモデル (デフォルトはNone、_get_modelで初期化)
        _model_name (str | None): 使用するモデルの名前 (デフォルトはNone)
        _fake_responses (list[str] | None): FAKEプロバイダ用のダミー応答リスト (デフォルトはNone)
        _graph (CompiledStateGraph | None): エージェントのグラフ (デフォルトはNone、_create_graphで初期化)
    """

    # 必須
    _name: str
    _description: str
    _state: type[Any]

    # オプションまたはデフォルト値あり
    _status: AgentStatus = AgentStatus.IDLE
    _model: BaseChatModel | None = None
    _model_name: str | None = None
    _fake_responses: list[BaseModel] | None = None
    _graph: CompiledStateGraph | None = None

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.FAKE,
    ) -> None:
        """初期化.

        Args:
            provider (LLMProvider): LLMプロバイダ (デフォルトはFAKE)
        """
        self.provider = provider
        self._memory = get_memory()

        self._graph = self._create_graph()

    @property
    def is_running(self) -> bool:
        """エージェントが実行中かどうか."""
        return self._status == AgentStatus.RUNNING

    @property
    def agent_property(self) -> AgentProperty:
        """エージェントのプロパティを取得.

        Returns:
            AgentProperty: エージェントのプロパティ
        """
        return AgentProperty(
            name=self._name,
            description=self._description,
            status=self._status,
        )

    @abstractmethod
    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        """LangGraphのグラフを作成するためのメソッド.

        このメソッドを実装して、具体的なグラフの構築ロジックを定義します。

        Example:
            ```python
            def _create_graph(self, graph_builder: StateGraph) -> StateGraph:
                # グラフのノードとエッジを定義
                graph_builder.add_node("node_name", node_function)
                graph_builder.add_edge(START, "node_name")
                return graph_builder
            ```

        Args:
            graph_builder (StateGraph): グラフビルダーインスタンス

        Returns:
            StateGraph: 作成されたグラフ
        """
        err_msg = "Subclasses must implement the _create_graph method."
        raise NotImplementedError(err_msg)

    def _create_graph(self) -> CompiledStateGraph:
        """LangGraphのグラフを作成.

        Returns:
            作成されたStateGraphインスタンス
        """
        graph_builder = self.create_graph(StateGraph(self._state))
        return graph_builder.compile(checkpointer=self._memory)

    def get_model(self) -> BaseChatModel:
        """LLMモデルを取得.

        Returns:
            BaseChatModel: 使用するLLMモデル
        """
        if not self._model:
            self._model = get_model(self.provider, self._model_name, self._fake_responses)
        return self._model

    def get_config(self, thread_id: str) -> RunnableConfig:
        return {"configurable": {"thread_id": thread_id}}

    def invoke(self, state: StateType, thread_id: str) -> ReturnType | None:
        """ユーザー入力を処理して応答を生成.

        Args:
            state (StateType): エージェントの状態
            thread_id (str): スレッドID

        Returns:
            ReturnType: モデルからの応答
        """
        # グラフの初期化がされているかを確認
        if not self._graph:
            err_msg = "Graph is not initialized. Please create the graph before invoking."
            agents_logger.error(err_msg)
            raise RuntimeError(err_msg)

        agents_logger.debug(f"Invoking agent with input: {state} in thread: {thread_id}")
        response = self._graph.invoke(
            state,
            self.get_config(thread_id),
        )
        agents_logger.debug(f"Graph invoke response: {response}")
        if isinstance(response, dict) and "final_response" in response:
            return response["final_response"]

        agents_logger.error("Invalid response format from graph invoke.")
        return None

    def stream(self, state: StateType, thread_id: str) -> Iterator[dict[str, Any] | Any]:
        """ユーザー入力をストリーミングして応答を生成.

        Args:
            state (BaseAgentState): エージェントの状態
            thread_id (str): スレッドID

        Yields:
            dict[str, Any] | Any: ストリーミングされた応答
        """
        if not self._graph:
            err_msg = "Graph is not initialized. Please create the graph before streaming."
            agents_logger.error(err_msg)
            raise RuntimeError(err_msg)

        agents_logger.debug(f"Streaming agent with input: {state} in thread: {thread_id}")

        yield from self._graph.stream(
            state,
            self.get_config(thread_id),
            stream_mode="messages",
        )
