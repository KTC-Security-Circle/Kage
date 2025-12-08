from __future__ import annotations

import json
from uuid import uuid4

from models import AiSuggestionStatus, MemoRead, MemoStatus, TaskRead, TaskStatus
from views.memos.state import MemosViewState


def test_restore_ai_flow_sets_project_info() -> None:
    memo_id = uuid4()
    task_id = uuid4()
    project_id = uuid4()
    log_payload = json.dumps(
        {
            "version": 3,
            "draft_task_refs": [
                {
                    "task_id": str(task_id),
                    "route": "next_action",
                    "project_id": str(project_id),
                    "project_title": "LLM連携",
                }
            ],
            "tasks": [],
            "project_info": {
                "project_id": str(project_id),
                "title": "LLM連携",
                "description": "AIが作成したプロジェクト",
                "status": "active",
                "error": None,
            },
        }
    )
    task = TaskRead(
        id=task_id,
        title="AIタスク",
        description="desc",
        status=TaskStatus.DRAFT,
        memo_id=memo_id,
        project_id=project_id,
    )
    memo = MemoRead(
        id=memo_id,
        title="memo",
        content="タスク化",
        status=MemoStatus.INBOX,
        ai_suggestion_status=AiSuggestionStatus.AVAILABLE,
        ai_analysis_log=log_payload,
        tasks=[task],
    )
    state = MemosViewState()
    state.set_all_memos([memo])

    ai_state = state.ai_flow_state_for(memo_id)
    assert ai_state.project_id == str(project_id)
    assert ai_state.project_title == "LLM連携"
    assert ai_state.project_status == "active"
    assert ai_state.generated_tasks[0].project_id == str(project_id)
