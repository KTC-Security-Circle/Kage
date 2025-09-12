import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

# ---- 早期にストレージディレクトリを確定させ agent_conf の定数評価前に環境を整える ----
if "FLET_APP_STORAGE_DATA" not in os.environ:  # [AI GENERATED] CI 環境で未設定の場合
    os.environ["FLET_APP_STORAGE_DATA"] = tempfile.mkdtemp(prefix="storage_")

from agents.agent_conf import SQLITE_DB_PATH, LLMProvider
from agents.task_agents.simple_chat.agent import SimpleChatAgent
from agents.task_agents.splitter.agent import TaskSplitterAgent

# ディレクトリ安全確保
db_parent = Path(SQLITE_DB_PATH).parent
db_parent.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def thread_id() -> str:
    return str(uuid4())


@pytest.fixture
def simple_chat_agent() -> SimpleChatAgent:
    return SimpleChatAgent(LLMProvider.FAKE, verbose=False, error_response=False)


@pytest.fixture
def task_splitter_agent() -> TaskSplitterAgent:
    return TaskSplitterAgent(LLMProvider.FAKE, verbose=False, error_response=False)


@pytest.fixture
def agents_db_path() -> Path:
    return Path(SQLITE_DB_PATH)
