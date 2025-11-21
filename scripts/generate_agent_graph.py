from pathlib import Path

from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
from agents.task_agents.one_liner.agent import OneLinerAgent

asset_path = Path(__file__).parent.parent / "src" / "assets" / "agent_graphs"

if not Path.exists(asset_path):
    Path.mkdir(asset_path, parents=True)


agents = [MemoToTaskAgent(), OneLinerAgent()]

for agent in agents:
    file_path = asset_path / f"{agent.__class__.__name__.lower()}_graph.png"
    agent._graph.get_graph().draw_mermaid_png(output_file_path=str(file_path))  # noqa: SLF001
