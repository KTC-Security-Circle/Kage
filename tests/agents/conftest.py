import os
from pathlib import Path
from uuid import uuid4

import pytest

from agents.agent_conf import SQLITE_DB_PATH, LLMProvider
from agents.task_agents.simple_chat.agent import SimpleChatAgent
from agents.task_agents.splitter.agent import TaskSplitterAgent


@pytest.fixture(scope="session", autouse=True)
def _set_storage_tmp(tmp_path_factory: pytest.TempPathFactory) -> None:
    """FLET_APP_STORAGE_DATA をテスト用一時ディレクトリに設定。[AI GENERATED]

    agents.db / llms などの副作用を隔離する。
    """
    tmp_dir = tmp_path_factory.mktemp("storage")
    os.environ["FLET_APP_STORAGE_DATA"] = str(tmp_dir)


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
