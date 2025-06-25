# Agent層 設計ガイド - LangChainとLangGraphの活用

このドキュメントでは、`agents`層の設計と実装方針について説明します。`LangChain`と`LangGraph`を利用して、自律的なタスク実行エージェントを構築する方法を解説します。

## Agent層の役割

Agent層は、複雑で複数のステップを要するタスクや、大規模言語モデル（LLM）の能力を最大限に活用する必要がある処理を担当します。

### 主な責務

- **自律的なタスク実行**: 与えられた目標に対し、ツールを使い分けながら自律的にタスクを遂行します。
- **状態管理**: `LangGraph`を利用して、タスクの進捗や中間結果などの状態を管理します。
- **ツール連携**: `Logic`層のサービスや外部APIを「ツール」として呼び出し、タスクを実行します。

## なぜLangChainとLangGraphを使うのか？

- **LangChain**: LLMアプリケーション開発のための豊富なコンポーネント（プロンプトテンプレート、パーサー、ツール連携など）を提供します。
- **LangGraph**: 状態を持つグラフとしてエージェントの処理フローを定義できます。これにより、ループや条件分岐を含む複雑なワークフローを堅牢に構築できます。

## アーキテクチャ上の位置づけ

Agent層は、`Logic`層から呼び出される形で動作します。`Logic`層がユーザーからの指示を解釈し、どのエージェントにタスクを依頼するかを決定します。

```plain text
┌─────────────────┐
│      Views      │ (UI Layer)
└────────┬────────┘
         │
┌────────▼────────┐
│      Logic      │ (Business Logic Layer)
└────────┬───┬────┘
         │   │
┌────────▼─┐ │ ┌──────────┐
│  Models  │ │ │  Agents  │ (AI Agent Layer)
│ (Data)   │ │ │          │
└──────────┘ │ └─────┬────┘
             │       │
             └───────► Tools (e.g., Logic services, APIs)
```

## ディレクトリ構造

```plain text
src/agents/
├── __init__.py
├── base.py                 # BaseAgentなど、すべてのエージェントの基底定義
├── agent_conf.py           # LLMプロバイダなど、エージェント関連の設定
├── utils.py                # LLMモデルやメモリ取得などの共通ユーティリティ
├── tools/                  # 複数のエージェントで共有するツール
│   └── __init__.py
└── task_agents/            # 特定の目的を持つエージェント群
    ├── __init__.py
    └── splitter/           # 「タスク分割エージェント」
        ├── __init__.py
        ├── agent.py        # エージェント本体 (グラフ定義、ノード実装)
        ├── prompt.py       # プロンプト定義
        └── state.py        # 状態(State)と出力モデル(Pydantic)の定義
```

## 実装テンプレート

`BaseAgent`を継承したエージェントの実装例です。エージェントは主に`state.py`, `prompt.py`, `agent.py`の3つのファイルで構成されます。

### 1. 状態と出力モデルの定義 (`splitter/state.py`)

エージェントが内部でり扱う状態と、最終的に出力するデータ構造を定義します。

```python
from pydantic import BaseModel, Field
from agents.base import BaseAgentState

# エージェントの内部状態を定義
class TaskSplitterState(BaseAgentState):
    """タスク分割エージェントの状態."""
    task_title: str
    task_description: str

# LLMに構造化された出力を強制するためのPydanticモデル
class TaskSplitterOutput(BaseModel):
    """このツールを常に応答の構造化に使用してください."""
    task_titles: list[str] = Field(description="分割されたタスクのタイトルのリスト")
    task_descriptions: list[str] = Field(description="分割されたタスクの説明のリスト")
```

### 2. プロンプトの定義 (`splitter/prompt.py`)

エージェントが使用するプロンプトを定義します。

```python
from langchain_core.prompts import ChatPromptTemplate

# システムプロンプトでエージェントの役割を定義
SPLITTER_AGENT_SYSTEM_PROMPT = """あなたは、タスクを小さなサブタスクに分割するのが得意なアシスタントです。
...（役割や指示の詳細）...
"""

# ユーザーからの入力を受け取るプロンプト
SPLITTER_AGENT_HUMAN_PROMPT = """以下のタスクを小さなサブタスクに分割してください

タスク名: {task_name}
タスク説明: {task_description}
"""

# ChatPromptTemplateを使用してプロンプトを組み立てる
splitter_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SPLITTER_AGENT_SYSTEM_PROMPT),
        ("human", SPLITTER_AGENT_HUMAN_PROMPT),
    ]
)
```

### 3. エージェント本体の実装 (`splitter/agent.py`)

`BaseAgent`を継承し、グラフの構築とノードの処理を実装します。

```python
from langgraph.graph import START, StateGraph
from agents.base import BaseAgent
from .prompt import splitter_agent_prompt
from .state import TaskSplitterOutput, TaskSplitterState

class TaskSplitterAgent(BaseAgent[TaskSplitterState, TaskSplitterOutput]):
    """タスク分割エージェントの実装."""

    # エージェントの基本情報を定義
    _name = "TaskSplitterAgent"
    _description = "タスクを分割して処理するエージェント"
    _state = TaskSplitterState

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        """グラフのワークフローを定義."""
        graph_builder.add_node("chatbot", self.chatbot_node) # ノードを追加
        graph_builder.add_edge(START, "chatbot") # エントリーポイントを設定
        return graph_builder

    def chatbot_node(self, state: TaskSplitterState) -> dict[str, TaskSplitterOutput]:
        """グラフのノードとして実行される処理."""
        # モデルとプロンプトを準備
        model = self.get_model()
        # 出力モデル(Pydantic)をツールとしてLLMにバインドし、構造化出力を強制
        llm_with_tools = model.bind_tools([TaskSplitterOutput])
        agent = splitter_agent_prompt | llm_with_tools

        # エージェントを実行
        response = agent.invoke({
            "task_name": state["task_title"],
            "task_description": state["task_description"],
        })

        # 結果をパースして状態を更新
        output_obj = TaskSplitterOutput.model_validate(response.tool_calls[0]["args"])
        return {"final_response": output_obj}
```
