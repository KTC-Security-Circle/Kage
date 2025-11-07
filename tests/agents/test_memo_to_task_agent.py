import uuid

from agents.agent_conf import LLMProvider
from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from models import MemoRead, MemoStatus


def _build_state(memo_text: str, current_datetime: str = "2025-10-25T10:00:00+09:00") -> MemoToTaskState:
    title_source = next((line.strip() for line in memo_text.splitlines() if line.strip()), "タイトル未設定")
    memo = MemoRead(
        id=uuid.uuid4(),
        title=title_source,
        content=memo_text,
        status=MemoStatus.INBOX,
    )
    return {
        "memo": memo,
        "existing_tags": ["仕事", "プライベート"],
        "current_datetime_iso": current_datetime,
    }


def test_memo_to_task_handles_non_actionable(thread_id: str) -> None:
    """アイデア扱いのメモはタスク生成せず、suggested_memo_status=idea を返す。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    state = _build_state("アイデア: 新しいUIの検討メモ")

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks == []
    assert result.suggested_memo_status == "idea"


def test_memo_to_task_handles_empty_memo(thread_id: str) -> None:
    """空メモでもFAKEシード生成が失敗せずデフォルトタイトルでタスク化される。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    state = _build_state("")

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].title == "メモの整理"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_routes_quick_action(thread_id: str) -> None:
    """タイトルに「確認」を含むとクイックアクションとして progress にルーティングされる。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    state = _build_state("田中さんに承認状況を確認する")

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].route == "progress"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_routes_delegate(thread_id: str) -> None:
    """本文に「依頼」を含むと waiting にルーティングされる。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    state = _build_state("上長に承認を依頼するメールを送る")

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].route == "waiting"
    assert result.suggested_memo_status == "active"


def test_memo_to_task_schedules_calendar(thread_id: str) -> None:
    """本文に「会議」を含むと calendar にルーティングされ、due_date は current_datetime_iso が用いられる。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    current_datetime = "2025-11-01T09:00:00+09:00"
    state = _build_state("会議の準備メモ", current_datetime)

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].route == "calendar"
    assert result.tasks[0].due_date == current_datetime
    assert result.suggested_memo_status == "active"


def test_memo_to_task_keeps_utc_z_due_date(thread_id: str) -> None:
    """UTCのZ付きISO8601期日がサニタイズで破棄されない。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    current_datetime = "2025-03-10T09:00:00Z"
    state = _build_state("会議の予定を整理する", current_datetime)

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].route == "calendar"
    assert result.tasks[0].due_date == current_datetime
    assert result.suggested_memo_status == "active"


def test_memo_to_task_handles_project(thread_id: str) -> None:
    """本文に「プロジェクト」を含むと project 計画経由で next_action が含まれる。"""
    agent = MemoToTaskAgent(LLMProvider.FAKE, verbose=False, error_response=False)
    state = _build_state("新しい資料作成プロジェクトを開始する")

    result = agent.invoke(state, thread_id)

    assert isinstance(result, MemoToTaskResult)
    assert result.tasks, "タスクが1件以上生成されること"
    assert result.tasks[0].route == "next_action"
    assert result.tasks[0].project_title is not None
    assert all(task.project_title == result.tasks[0].project_title for task in result.tasks)
    assert result.suggested_memo_status == "active"
