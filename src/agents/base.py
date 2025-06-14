from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

from langgraph.graph import StateGraph
from loguru import logger

from agents.agent_conf import LLMProvider
from agents.utils import get_model

if TYPE_CHECKING:
    from collections.abc import Iterator

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage
    from langgraph.graph.state import CompiledStateGraph


class AgentStatus(Enum):
    """エージェントの実行状態."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class BaseAgent(ABC):
    """LangGraphエージェントのベースクラス.

    このクラスを継承して具体的なエージェントを実装します。
    """

    # 必須
    name: str
    description: str
    _state: type[Any]

    # オプションまたはデフォルト値あり
    status: AgentStatus = AgentStatus.IDLE
    _model: BaseChatModel | None = None
    _graph: CompiledStateGraph | None = None

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.GOOGLE,
    ) -> None:
        """初期化.

        Args:
            provider (LLMProvider): LLMプロバイダ (デフォルトはGOOGLE)
            tools (list | None): 使用するツールのリスト（オプション）
        """
        self.provider = provider

        self._graph = self._create_graph()

    @property
    def is_running(self) -> bool:
        """エージェントが実行中かどうか."""
        return self.status == AgentStatus.RUNNING

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
        return graph_builder.compile()

    def get_model(self) -> BaseChatModel:
        """LLMモデルを取得.

        Returns:
            BaseChatModel: 使用するLLMモデル
        """
        if not self._model:
            self._model = get_model(self.provider, "gemini-2.0-flash")
        return self._model

    def invoke(self, user_input: str) -> str | None:
        """ユーザー入力を処理して応答を生成.

        Args:
            user_input (str): ユーザーからの入力

        Returns:
            str: モデルからの応答
        """
        # グラフの初期化がされているかを確認
        if not self._graph:
            err_msg = "Graph is not initialized. Please create the graph before invoking."
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        response = self._graph.invoke({"messages": [{"role": "user", "content": user_input}]})
        if isinstance(response, dict) and "messages" in response:
            return response["messages"][-1].content

        logger.error("Invalid response format from graph invoke.")
        return None

    def stream(self, user_input: str) -> Iterator[dict[str, list[BaseMessage]]]:
        if not self._graph:
            err_msg = "Graph is not initialized. Please create the graph before streaming."
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        return self._graph.stream({"messages": [{"role": "user", "content": user_input}]})
