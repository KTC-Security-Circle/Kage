# Project Overview
- **Purpose**: Kage is a Windows desktop task-management app that leverages LLM agents to transform memos into actionable tasks.
- **Primary Stack**: Python 3.12+, Flet for UI, LangChain/LangGraph agents, Loguru for logging, Poetry-equivalent tooling managed via `uv` and `poethepoet` task runner.
- **Key Directories**:
  - `src/agents`: LLM agents (e.g., memo-to-task agent).
  - `src/views`: Flet UI layouts and components.
  - `src/logic`: Application services, repositories, and unit-of-work patterns.
  - `tests/`: Pytest suites for agents, logic, settings, etc.
  - `docs/`: Developer and product documentation.
- **Notable Guidelines**: Keep UI modern, modularize via `ft.UserControl`, manage state separately, follow dependency injection patterns in logic layer, store prompts under `prompts/` or module-specific files.